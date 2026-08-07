from __future__ import annotations

import pandas as pd

from .config import Config
from .modelos import AnaliseDimensao, AnaliseGeral
from .prompts import (
    INSTRUCAO_COM_BASE,
    INSTRUCAO_SEM_BASE,
    TEMPLATE_ANALISE_DIMENSAO,
    TEMPLATE_ANALISE_GERAL,
)
from .utils import separar_paragrafos


SEM_CONTEXTO_WEB = "Pesquisa web sem contexto adicional confiável."
SEM_ATUALIZACAO_WEB = "Pesquisa web sem atualização relevante para esta dimensão."


def _formatar_indicadores(indicadores: dict) -> str:
    return "\n".join(f"- {k}: {v}" for k, v in indicadores.items())


def _formatar_chunks(chunks: list) -> str:
    return "\n\n".join(f"[{c['topico']}] {c['texto']}" for c in chunks)


def _formatar_dados_contextuais(dados_contextuais: dict) -> str:
    """Formata dados contextuais para uso apenas como caracterização."""
    if not dados_contextuais:
        return "Nenhum dado contextual disponível para este recorte."
    return "\n".join(f"- {k}: {v}" for k, v in dados_contextuais.items())


def extrair_texto_resposta(resposta) -> str:
    """Extrai texto de uma AIMessage, inclusive com Google Search Grounding."""
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
    """Normaliza o código IBGE vindo da planilha sem inventar valor."""
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


def _identificacao_municipio(municipio, estado=None, codigo_ibge=None):
    codigo = normalizar_codigo_ibge(codigo_ibge)
    uf_txt = (
        str(estado).strip()
        if estado is not None and not pd.isna(estado)
        else "UF não informada"
    )
    codigo_txt = codigo if codigo else "não informado"
    return uf_txt, codigo_txt


class LLMService:
    """Centraliza geração estruturada e pesquisa web controlada com Gemini."""

    def __init__(self, config: Config):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate
        except ImportError as exc:
            raise RuntimeError(
                "Dependências de IA ausentes. Execute: pip install -r requirements.txt"
            ) from exc

        self.config = config
        # Gemini 3.6 Flash: não enviamos temperature/top_p/top_k.
        llm = ChatGoogleGenerativeAI(
            model=config.modelo,
            google_api_key=config.api_key,
            max_output_tokens=config.max_output_tokens,
        )

        # Google Search Grounding é usado apenas como contexto complementar e
        # validação pontual. A planilha permanece a fonte principal do diagnóstico.
        self.llm_pesquisa_web = llm.bind_tools([{"google_search": {}}])

        llm_geral = llm.with_structured_output(AnaliseGeral)
        llm_dimensao = llm.with_structured_output(AnaliseDimensao)
        self.chain_geral = (
            ChatPromptTemplate.from_template(TEMPLATE_ANALISE_GERAL) | llm_geral
        )
        self.chain_dimensao = (
            ChatPromptTemplate.from_template(TEMPLATE_ANALISE_DIMENSAO) | llm_dimensao
        )

    def pesquisar_contexto_municipio(
        self, municipio, estado=None, codigo_ibge=None, tentativas: int | None = None
    ) -> str:
        """Pesquisa web breve para complementar somente a Análise Geral."""
        tentativas = tentativas or self.config.tentativas_llm
        uf_txt, codigo_txt = _identificacao_municipio(municipio, estado, codigo_ibge)

        prompt_pesquisa = f"""
Faça uma pesquisa BREVE na internet sobre o município abaixo para apoiar a
contextualização de um diagnóstico institucional municipal. Use no máximo
3 consultas de busca.

IDENTIFICAÇÃO TERRITORIAL OBRIGATÓRIA:
- Município: {municipio}
- UF: {uf_txt}
- Código IBGE: {codigo_txt}

Antes de utilizar QUALQUER fato, confirme que a fonte se refere especificamente
a esse município e a essa UF. Quando o código IBGE estiver disponível, use-o
como elemento adicional de conferência. Ignore resultados de municípios
homônimos ou de localidades com nome semelhante. Se a identidade territorial
não estiver clara na fonte, DESCARTE a informação.

Priorize fontes nesta ordem:
1. Prefeitura e outros órgãos públicos;
2. IBGE e órgãos oficiais estaduais/federais;
3. universidades e instituições públicas de ensino/pesquisa;
4. imprensa confiável, apenas quando realmente necessário.

Procure somente fatos úteis e relativamente estáveis sobre:
- perfil econômico e territorial;
- presença de universidades, centros de pesquisa ou ecossistema de inovação;
- papel regional do município;
- infraestrutura ou serviços públicos relevantes;
- iniciativas públicas recentes que ajudem a compreender o contexto local.

Regras:
- NÃO faça avaliação de maturidade do município;
- NÃO dê recomendações;
- NÃO infira relações de causa e efeito;
- NÃO use textos promocionais, rankings comerciais ou opiniões como fatos;
- prefira fatos confirmados por fontes institucionais;
- seja seletivo: traga apenas 4 a 6 pontos curtos;
- em cada ponto, indique entre parênteses a fonte ou instituição de origem;
- se houver dúvida territorial, omita o ponto em vez de arriscar atribuí-lo
  ao município errado.

Se não encontrar informações confiáveis e úteis, responda exatamente:
"Pesquisa web sem contexto adicional confiável."
"""

        ultimo_erro = None
        for _ in range(tentativas):
            try:
                resposta = self.llm_pesquisa_web.invoke(prompt_pesquisa)
                texto = extrair_texto_resposta(resposta)
                if texto:
                    return texto
            except Exception as exc:
                ultimo_erro = exc

        if ultimo_erro:
            return SEM_CONTEXTO_WEB
        return SEM_CONTEXTO_WEB

    def pesquisar_validacao_dimensao(
        self,
        dimensao,
        municipio,
        indicadores_dimensao,
        estado=None,
        codigo_ibge=None,
        tentativas: int | None = None,
    ) -> str:
        """Pesquisa web breve para validar/atualizar pontos de uma dimensão."""
        tentativas = tentativas or self.config.tentativas_llm
        uf_txt, codigo_txt = _identificacao_municipio(municipio, estado, codigo_ibge)
        indicadores_txt = _formatar_indicadores(indicadores_dimensao)

        prompt_pesquisa = f"""
Faça uma pesquisa BREVE na internet para VALIDAR E ATUALIZAR informações
relevantes da dimensão "{dimensao}" de um diagnóstico municipal. Use no máximo
3 consultas de busca e seja muito seletivo.

IDENTIFICAÇÃO TERRITORIAL OBRIGATÓRIA:
- Município: {municipio}
- UF: {uf_txt}
- Código IBGE: {codigo_txt}

INDICADORES DA PLANILHA QUE DEVEM ORIENTAR A PESQUISA:
{indicadores_txt}

OBJETIVO DA PESQUISA:
Localizar somente informações externas que ajudem a confirmar, qualificar ou
atualizar os pontos mais importantes desses indicadores. Dê prioridade a ações
recentes que possam mudar a interpretação prática do diagnóstico, como:
- obra pública em andamento;
- novo equipamento ou infraestrutura em implantação;
- programa, serviço ou sistema recentemente lançado;
- contrato, licitação ou expansão comprovada;
- alteração institucional relevante já formalizada.

Exemplo de interpretação correta: se a planilha aponta baixo tratamento de
esgoto, mas existe uma nova estação de tratamento em construção, NÃO diga que
o problema já foi resolvido. Registre que o indicador mostra uma deficiência
atual/histórica e que há uma ação em andamento que pode alterar esse cenário
quando concluída e operacionalizada.

VALIDAÇÃO TERRITORIAL:
Antes de usar qualquer fato, confirme que ele pertence especificamente a
{municipio}/{uf_txt}. Quando disponível, confira também o código IBGE
{codigo_txt}. Descarte resultados de municípios homônimos, órgãos de outra
localidade ou fontes cuja localização não seja clara.

FONTES — prioridade:
1. Prefeitura, autarquias e prestadores públicos locais;
2. Governo estadual/federal, IBGE, SNIS/SINISA, ministérios e agências oficiais;
3. universidades e instituições públicas de pesquisa;
4. imprensa confiável apenas como complemento, preferencialmente quando citar
   documento, obra, contrato ou autoridade identificável.

REGRAS DE CONFIABILIDADE E ATUALIDADE:
- Priorize informações recentes e páginas com data identificável.
- Diferencie claramente: anunciado/planejado; licitado/contratado;
  em implantação/em construção; concluído/em operação.
- Não trate anúncio político ou intenção como execução comprovada.
- Não use ranking comercial, texto promocional, postagem sem fonte ou opinião.
- Não declare que a planilha está errada apenas porque a web traz número
  diferente; datas, métodos e definições podem ser distintos.
- A web NÃO deve recalcular o nível de maturidade.
- Traga no máximo 3 achados realmente relevantes para esta dimensão.
- Para cada achado, informe: tema; fato atual; estágio da ação; fonte/instituição
  e data/ano quando disponível.
- Se não houver informação externa que realmente melhore a leitura da dimensão,
  não force resultados.

Se não encontrar informação confiável, diretamente relacionada aos indicadores
ou territorialmente segura, responda exatamente:
"Pesquisa web sem atualização relevante para esta dimensão."
"""

        ultimo_erro = None
        for _ in range(tentativas):
            try:
                resposta = self.llm_pesquisa_web.invoke(prompt_pesquisa)
                texto = extrair_texto_resposta(resposta)
                if texto:
                    return texto
            except Exception as exc:
                ultimo_erro = exc

        if ultimo_erro:
            return SEM_ATUALIZACAO_WEB
        return SEM_ATUALIZACAO_WEB

    def gerar_analise_geral(
        self,
        municipio,
        porte,
        indicadores,
        chunks_gerais,
        dados_contextuais=None,
        pesquisa_web=None,
    ):
        instrucao_base = (
            INSTRUCAO_COM_BASE.format(base_conceitual=_formatar_chunks(chunks_gerais))
            if chunks_gerais
            else INSTRUCAO_SEM_BASE
        )
        payload = {
            "municipio": municipio,
            "porte": porte,
            "indicadores_txt": _formatar_indicadores(indicadores),
            "instrucao_base": instrucao_base,
            "dados_contextuais_txt": _formatar_dados_contextuais(
                dados_contextuais or {}
            ),
            "pesquisa_web_txt": pesquisa_web or SEM_CONTEXTO_WEB,
        }

        ultimo_erro = None
        for _ in range(self.config.tentativas_llm):
            try:
                resultado = self.chain_geral.invoke(payload)
                if not resultado.analise_geral or len(resultado.analise_geral.strip()) < 40:
                    raise ValueError("Resposta do modelo vazia ou incompleta.")
                return resultado.analise_geral
            except Exception as exc:
                ultimo_erro = exc

        raise RuntimeError(
            "Não foi possível gerar a análise geral após "
            f"{self.config.tentativas_llm} tentativas: {ultimo_erro}"
        )

    def gerar_analise_dimensao(
        self,
        dimensao,
        municipio,
        porte,
        indicadores_dimensao,
        chunks_selecionados,
        dados_contextuais_dimensao=None,
        pesquisa_web_dimensao=None,
    ):
        if not indicadores_dimensao:
            raise ValueError(f"A dimensão '{dimensao}' não possui indicadores associados.")

        instrucao_base = (
            INSTRUCAO_COM_BASE.format(
                base_conceitual=_formatar_chunks(chunks_selecionados)
            )
            if chunks_selecionados
            else INSTRUCAO_SEM_BASE
        )
        payload = {
            "municipio": municipio,
            "porte": porte,
            "dimensao": dimensao,
            "indicadores_txt": _formatar_indicadores(indicadores_dimensao),
            "instrucao_base": instrucao_base,
            "dados_contextuais_txt": _formatar_dados_contextuais(
                dados_contextuais_dimensao or {}
            ),
            "pesquisa_web_dimensao_txt": pesquisa_web_dimensao
            or SEM_ATUALIZACAO_WEB,
        }

        ultimo_erro = None
        for _ in range(self.config.tentativas_llm):
            try:
                resultado = self.chain_dimensao.invoke(payload)
                if len(resultado.sugestoes) != 4:
                    raise ValueError(
                        f"Modelo retornou {len(resultado.sugestoes)} sugestões "
                        "(esperado: 4)."
                    )
                if not resultado.analise or len(resultado.analise.strip()) < 80:
                    raise ValueError("Análise da dimensão vazia ou curta demais.")

                paragrafos = separar_paragrafos(resultado.analise)
                if len(paragrafos) != 2:
                    raise ValueError(
                        f"Modelo retornou {len(paragrafos)} parágrafo(s) na análise "
                        "(esperado: 2)."
                    )

                return {
                    "analise": "\n\n".join(paragrafos),
                    "sugestoes": resultado.sugestoes,
                }
            except Exception as exc:
                ultimo_erro = exc

        raise RuntimeError(
            f"Não foi possível gerar a análise de '{dimensao}' após "
            f"{self.config.tentativas_llm} tentativas: {ultimo_erro}"
        )
