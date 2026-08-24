from __future__ import annotations

import re
import time
import textwrap
import unicodedata
import pandas as pd

from .config import Config
from .modelos import AnaliseDimensao, AnaliseGeral, RevisaoDimensao
from .prompts import (
    INSTRUCAO_COM_BASE, INSTRUCAO_SEM_BASE, TEMPLATE_ANALISE_DIMENSAO,
    TEMPLATE_ANALISE_GERAL, TEMPLATE_REVISAO_DIMENSAO,
)
from .utils import separar_paragrafos


def formatar_indicadores(indicadores: dict) -> str:
    return "\n".join(f"- {k}: {v}" for k, v in indicadores.items())


def formatar_chunks(chunks: list) -> str:
    blocos = []
    for c in chunks:
        topico = c.get("topico") or c.get("titulo") or c.get("recomendacao_id") or c.get("chunk_id") or "Trecho da Carta"
        texto = str(c.get("texto", "")).strip()
        if texto:
            blocos.append(f"[{topico}] {texto}")
    return "\n\n".join(blocos)


def formatar_dados_contextuais(dados: dict) -> str:
    if not dados:
        return "Nenhum dado contextual disponível para este recorte."
    return "\n".join(f"- {k}: {v}" for k, v in dados.items())


def extrair_texto_resposta(resposta) -> str:
    texto = getattr(resposta, "text", None)
    if isinstance(texto, str) and texto.strip():
        return texto.strip()
    conteudo = getattr(resposta, "content", "")
    if isinstance(conteudo, str):
        return conteudo.strip()
    partes = []
    if isinstance(conteudo, list):
        for bloco in conteudo:
            if isinstance(bloco, str):
                partes.append(bloco)
            elif isinstance(bloco, dict) and bloco.get("type") == "text":
                partes.append(str(bloco.get("text", "")))
    return "\n".join(p for p in partes if p.strip()).strip()


def normalizar_codigo_ibge(codigo_ibge):
    if codigo_ibge is None or pd.isna(codigo_ibge):
        return None
    try:
        if isinstance(codigo_ibge, (int, float)):
            return str(int(codigo_ibge))
    except Exception:
        pass
    texto = str(codigo_ibge).strip()
    if texto.endswith(".0") and texto[:-2].isdigit():
        texto = texto[:-2]
    return texto or None


def validacao_sem_atualizacao(texto: str) -> bool:
    texto_norm = re.sub(r"\s+", " ", (texto or "").strip().lower())
    marcadores = {
        "pesquisa web sem atualização relevante para esta dimensão.",
        "pesquisa web sem atualizacao relevante para esta dimensao.",
        "pesquisa web sem atualização relevante para a análise geral.",
        "pesquisa web sem atualizacao relevante para a analise geral.",
        "pesquisa web sem contexto adicional confiável.",
        "pesquisa web sem contexto adicional confiavel.",
    }
    return (not texto_norm) or texto_norm in marcadores


def validar_regras_editoriais(textos, rotulo="texto"):
    if isinstance(textos, str):
        textos = [textos]
    combinado = "\n".join(str(t or "") for t in textos)
    norm = unicodedata.normalize("NFKD", combinado)
    norm = "".join(c for c in norm if not unicodedata.combining(c)).lower()
    if "cidades do futuro" in norm:
        raise ValueError(f"{rotulo} contém referência proibida ao programa 'Cidades do Futuro'.")
    if "—" in combinado:
        raise ValueError(f"{rotulo} contém travessão (—), proibido pelas regras editoriais.")
    return True


# Aliases de compatibilidade com os utilitários do pacote anterior/notebook.
_extrair_texto_resposta = extrair_texto_resposta
_normalizar_codigo_ibge = normalizar_codigo_ibge
_validacao_sem_atualizacao = validacao_sem_atualizacao
_separar_paragrafos = separar_paragrafos
_validar_regras_editoriais = validar_regras_editoriais


class LLMService:
    def __init__(self, config: Config):
        self.config = config
        config.validar(exigir_planilha=False, exigir_api=True, exigir_embeddings=False)
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain_core.prompts import ChatPromptTemplate
        except ImportError as exc:
            raise RuntimeError("Instale langchain-anthropic e langchain-core.") from exc
        self.llm = ChatAnthropic(
            model=config.modelo,
            api_key=config.anthropic_api_key,
            max_tokens=config.max_output_tokens,
        )
        self.llm_pesquisa_web = ChatAnthropic(
            model=config.modelo_pesquisa_web,
            api_key=config.anthropic_api_key,
            max_tokens=config.max_output_tokens,
        ).bind_tools([{
            "type": "web_search_20250305", "name": "web_search",
            "max_uses": config.max_usos_web_por_dimensao,
        }])
        self.chain_geral = ChatPromptTemplate.from_template(TEMPLATE_ANALISE_GERAL) | self.llm.with_structured_output(AnaliseGeral)
        self.chain_dimensao = ChatPromptTemplate.from_template(TEMPLATE_ANALISE_DIMENSAO) | self.llm.with_structured_output(AnaliseDimensao)
        self.chain_revisao = ChatPromptTemplate.from_template(TEMPLATE_REVISAO_DIMENSAO) | self.llm.with_structured_output(RevisaoDimensao)

    @staticmethod
    def _backoff(numero_falha: int) -> int:
        return 5 * (3 ** numero_falha)

    def _grounding(self, prompt: str, rotulo: str, tentativas=None):
        tentativas = tentativas or self.config.tentativas_llm
        ultimo = None
        for tentativa in range(tentativas):
            try:
                texto = extrair_texto_resposta(self.llm_pesquisa_web.invoke(prompt))
                if texto:
                    return texto
                raise ValueError("Resposta de grounding vazia.")
            except Exception as exc:
                ultimo = exc
                if tentativa < tentativas - 1:
                    espera = self._backoff(tentativa)
                    print(f"⚠️ Falha em {rotulo}. Nova tentativa em {espera}s. ({exc})")
                    time.sleep(espera)
        print(f"⚠️ {rotulo} indisponível. ({ultimo})")
        return ""

    def pesquisar_validacao_dimensao(self, dimensao, municipio, indicadores_dimensao, rascunho_dimensao, estado=None, codigo_ibge=None, tentativas=None):
        codigo = normalizar_codigo_ibge(codigo_ibge)
        uf_txt = str(estado).strip() if estado is not None and not pd.isna(estado) else "UF não informada"
        codigo_txt = codigo or "não informado"
        sugestoes_txt = "\n".join(f"- {s}" for s in rascunho_dimensao["sugestoes"])
        indicadores_txt = formatar_indicadores(indicadores_dimensao)
        prompt = textwrap.dedent(f"""
        Valide de forma PONTUAL o rascunho abaixo da dimensão "{dimensao}" de um
        diagnóstico municipal. A pesquisa ocorre DEPOIS da geração do texto.

        Faça UMA ÚNICA ETAPA DE GROUNDING.

        IDENTIFICAÇÃO TERRITORIAL OBRIGATÓRIA:
        - Município: {municipio}
        - UF: {uf_txt}
        - Código IBGE: {codigo_txt}

        INDICADORES DA PLANILHA — FONTE PRINCIPAL:
        {indicadores_txt}

        RASCUNHO DA ANÁLISE:
        {rascunho_dimensao['analise']}

        SUGESTÕES DO RASCUNHO:
        {sugestoes_txt}

        ============================================================
        PARTE A — VALIDAÇÃO PONTUAL
        ============================================================

        MANTENHA A MESMA LÓGICA DE VALIDAÇÃO:

        Escolha ATÉ CINCO pontos prioritários e DISTINTOS do rascunho cuja situação
        possa ter mudado desde a coleta dos dados. Não force cinco pontos: selecione apenas
        os que realmente sejam relevantes e sujeitos a atualização. Se houver somente um,
        valide apenas um; se houver dois, três ou quatro, limite-se a eles.

        PRIORIZE:
        - deficiência que possa ter recebido obra, programa ou implantação recente;
        - sugestão que possa já estar em execução;
        - fato institucional sujeito a mudança recente;
        - serviço ou sistema cuja situação atual possa alterar a interpretação;
        - projeto, equipamento ou infraestrutura que possa estar planejado, contratado,
          em implantação ou já concluído.

        NÃO escolha pontos que tratem essencialmente do mesmo assunto.
        Exemplo: "tratamento de esgoto" e "construção da ETE" contam como um único tema.

        REGRAS DA VALIDAÇÃO:
        - Não faça busca genérica sobre toda a dimensão.
        - Faça no máximo UMA consulta específica por ponto escolhido.
        - Não recalcule nem substitua indicadores da planilha.
        - Não declare que a planilha está errada por diferença de data/metodologia.
        - Confirme que o fato pertence especificamente a {municipio}/{uf_txt};
          descarte município homônimo ou localização duvidosa.
        - Priorize fontes oficiais e institucionais.
        - Diferencie rigorosamente: planejado; licitado/contratado; em implantação/
          construção; concluído/em operação.
        - Não trate anúncio ou obra em andamento como resultado já alcançado.
        - Só considere uma atualização quando ela tiver impacto real na interpretação
          ou em uma das sugestões.
        - Não desperdice consulta tentando apenas confirmar um fato estável já registrado
          na planilha.
        - NÃO selecione, pesquise, valide, cite ou use como atualização o programa "Cidades do Futuro". Se ele aparecer nos resultados de busca, ignore-o completamente.
        - O programa "Cidades do Futuro" também NÃO pode ser usado como enriquecimento nominal, exemplo de parceria, marco institucional ou justificativa para sugestão.

        FORMATO DA PARTE A:
        Para cada ponto com atualização útil, use:

        PONTO 1
        - ponto checado:
        - fato atual encontrado:
        - estágio da ação:
        - fonte/instituição e data/ano, quando disponível:
        - impacto na análise:
        - impacto em uma sugestão, se houver:

        PONTO 2
        - ponto checado:
        - fato atual encontrado:
        - estágio da ação:
        - fonte/instituição e data/ano, quando disponível:
        - impacto na análise:
        - impacto em uma sugestão, se houver:

        PONTO 3
        - ponto checado:
        - fato atual encontrado:
        - estágio da ação:
        - fonte/instituição e data/ano, quando disponível:
        - impacto na análise:
        - impacto em uma sugestão, se houver:

        PONTO 4
        - ponto checado:
        - fato atual encontrado:
        - estágio da ação:
        - fonte/instituição e data/ano, quando disponível:
        - impacto na análise:
        - impacto em uma sugestão, se houver:

        PONTO 5
        - ponto checado:
        - fato atual encontrado:
        - estágio da ação:
        - fonte/instituição e data/ano, quando disponível:
        - impacto na análise:
        - impacto em uma sugestão, se houver:

        Retorne somente os pontos que trouxerem atualização relevante.

        ============================================================
        PARTE B — ENRIQUECIMENTO NOMINAL
        ============================================================

        Depois da validação, procure referências GENÉRICAS já presentes no rascunho
        que possam ser substituídas por nomes oficiais confirmados, por exemplo:
        - "universidade federal" ou "universidade pública";
        - "parque tecnológico";
        - "hospital";
        - "estação de tratamento";
        - "conselho", "órgão", "secretaria" ou "autarquia";
        - "programa municipal";
        - "equipamento público";
        - "sistema", "aplicativo" ou "plataforma";
        - instituição de pesquisa, ensino ou inovação.

        REGRAS DO ENRIQUECIMENTO NOMINAL:
        - O enriquecimento NÃO substitui nem ocupa um dos pontos da Parte A.
        - Só enriqueça uma entidade que JÁ esteja mencionada no rascunho.
        - Não introduza instituição, programa ou equipamento novo apenas porque apareceu
          na pesquisa.
        - Confirme o nome oficial em fonte oficial ou institucional sempre que possível.
        - Confirme que a entidade pertence ou se relaciona inequivocamente a
          {municipio}/{uf_txt}.
        - Aproveite preferencialmente as mesmas consultas feitas na Parte A.
        - Evite buscas adicionais quando o nome não for importante para tornar o texto
          mais concreto.
        - Não invente nomes nem complete siglas por inferência.
        - Retorne no máximo 5 enriquecimentos nominais nesta dimensão.

        FORMATO DA PARTE B:

        ENRIQUECIMENTO NOMINAL 1
        - referência genérica do rascunho:
        - nome oficial confirmado:
        - sigla, se houver:
        - fonte/instituição de confirmação:

        (repita apenas quando houver outros nomes realmente confiáveis)

        ============================================================
        REGRA FINAL
        ============================================================

        Se houver atualização em apenas um ponto, retorne esse ponto normalmente.
        Se não houver atualização relevante nos pontos, MAS houver enriquecimento nominal
        confiável, retorne somente o enriquecimento nominal.

        Somente se não houver NENHUMA atualização confiável E NENHUM enriquecimento
        nominal confiável, responda EXATAMENTE:
        "Pesquisa web sem atualização relevante para esta dimensão."

        IMPORTANTE:
        Se apenas parte dos pontos trouxer novidade, NÃO use a frase
        "Pesquisa web sem atualização relevante para esta dimensão."; retorne somente
        os pontos que trouxeram atualização, junto com os enriquecimentos nominais que houver.
        """)
        texto = self._grounding(prompt, f"validação web pós-geração da dimensão '{dimensao}'", tentativas)
        return texto or "Pesquisa web sem atualização relevante para esta dimensão."

    @staticmethod
    def _formatar_dimensoes_validadas(dimensoes: dict):
        nomes = {
            "economica": "Dimensão Econômica", "sociocultural": "Dimensão Sociocultural",
            "meio_ambiente": "Dimensão Meio Ambiente",
            "capacidades_institucionais": "Dimensão Capacidades Institucionais",
        }
        blocos = []
        for chave, titulo in nomes.items():
            bloco = dimensoes.get(chave)
            if not bloco or not bloco.get("analise"):
                raise ValueError(f"Análise final ausente para '{titulo}'.")
            blocos.append(f"{titulo}:\n{bloco['analise']}")
        return "\n\n".join(blocos)

    def gerar_analise_geral(self, municipio, porte, dimensoes_validadas, tentativas=None):
        tentativas = tentativas or self.config.tentativas_llm
        txt = self._formatar_dimensoes_validadas(dimensoes_validadas)
        ultimo = None
        for _ in range(tentativas):
            try:
                resultado = self.chain_geral.invoke({"municipio": municipio, "porte": porte, "dimensoes_validadas_txt": txt})
                paragrafos = separar_paragrafos(resultado.analise_geral)
                if len(paragrafos) != 2:
                    raise ValueError(f"Análise Geral retornou {len(paragrafos)} parágrafo(s); esperado 2.")
                validar_regras_editoriais(paragrafos, "Análise Geral")
                return "\n\n".join(paragrafos)
            except Exception as exc:
                ultimo = exc
                print(f"⚠️ Falha ao gerar Análise Geral; tentando novamente... ({exc})")
        raise RuntimeError(f"Não foi possível gerar a Análise Geral: {ultimo}")

    def gerar_analise_dimensao(self, dimensao, municipio, porte, indicadores_dimensao, chunks_selecionados, dados_contextuais_dimensao=None, tentativas=None):
        if not indicadores_dimensao:
            raise ValueError(f"A dimensão '{dimensao}' não possui indicadores associados.")
        tentativas = tentativas or self.config.tentativas_llm
        instrucao_base = INSTRUCAO_COM_BASE.format(base_conceitual=formatar_chunks(chunks_selecionados)) if chunks_selecionados else INSTRUCAO_SEM_BASE
        ultimo = None
        for _ in range(tentativas):
            try:
                resultado = self.chain_dimensao.invoke({
                    "municipio": municipio, "porte": porte, "dimensao": dimensao,
                    "indicadores_txt": formatar_indicadores(indicadores_dimensao),
                    "instrucao_base": instrucao_base,
                    "dados_contextuais_txt": formatar_dados_contextuais(dados_contextuais_dimensao or {}),
                })
                if len(resultado.sugestoes) != 4:
                    raise ValueError("A dimensão deve retornar exatamente 4 sugestões.")
                p1=(resultado.paragrafo_1 or "").strip(); p2=(resultado.paragrafo_2 or "").strip(); p3=(resultado.paragrafo_3 or "").strip()
                if len(p1)<40 or len(p2)<40 or (p3 and len(p3)<40):
                    raise ValueError("Parágrafo vazio ou curto demais.")
                paragrafos=[p1,p2]+([p3] if p3 else [])
                validar_regras_editoriais(paragrafos + list(resultado.sugestoes), f"Rascunho {dimensao}")
                return {"analise":"\n\n".join(paragrafos), "sugestoes":resultado.sugestoes}
            except Exception as exc:
                ultimo=exc; print(f"⚠️ Falha ao gerar rascunho de '{dimensao}'; tentando novamente... ({exc})")
        raise RuntimeError(f"Não foi possível gerar '{dimensao}': {ultimo}")

    def revisar_analise_dimensao(self, dimensao, municipio, porte, indicadores_dimensao, rascunho_dimensao, dados_contextuais_dimensao=None, validacao_web=None, tentativas=None):
        if validacao_sem_atualizacao(validacao_web):
            return rascunho_dimensao
        tentativas = tentativas or self.config.tentativas_llm
        sugestoes_txt = "\n".join(f"- {s}" for s in rascunho_dimensao["sugestoes"])
        ultimo = None
        for _ in range(tentativas):
            try:
                resultado = self.chain_revisao.invoke({
                    "municipio": municipio, "porte": porte, "dimensao": dimensao,
                    "rascunho_analise": rascunho_dimensao["analise"],
                    "rascunho_sugestoes_txt": sugestoes_txt,
                    "indicadores_txt": formatar_indicadores(indicadores_dimensao),
                    "dados_contextuais_txt": formatar_dados_contextuais(dados_contextuais_dimensao or {}),
                    "validacao_web_txt": validacao_web,
                })
                if len(resultado.sugestoes) != 4:
                    raise ValueError("A revisão deve retornar exatamente 4 sugestões.")
                p1=(resultado.paragrafo_1 or "").strip(); p2=(resultado.paragrafo_2 or "").strip(); p3=(resultado.paragrafo_3 or "").strip()
                if len(p1)<20 or len(p2)<20 or (p3 and len(p3)<20):
                    raise ValueError("Parágrafo revisado vazio ou curto demais.")
                paragrafos=[p1,p2]+([p3] if p3 else [])
                validar_regras_editoriais(paragrafos + list(resultado.sugestoes), f"Revisão {dimensao}")
                return {"analise":"\n\n".join(paragrafos), "sugestoes":resultado.sugestoes}
            except Exception as exc:
                ultimo=exc; print(f"⚠️ Falha ao revisar '{dimensao}'; tentando novamente... ({exc})")
        print(f"⚠️ Revisão de '{dimensao}' falhou; mantendo rascunho. ({ultimo})")
        return rascunho_dimensao
