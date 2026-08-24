import pandas as pd

from municipio_analise import Config
from municipio_analise.pipeline import PipelineAnaliseMunicipio
from municipio_analise.taxonomia import DIMENSAO_PARA_CHAVE


class FakeSelector:
    def selecionar(self, dimensao, indicadores, linha_planilha=None):
        return [{"chunk_id": "teste", "topico": "Teste", "texto": "Base conceitual de teste."}]


class FakeLLM:
    def __init__(self):
        self.ordem=[]
    def gerar_analise_dimensao(self, dimensao, municipio, porte, indicadores, chunks, dados_contextuais_dimensao=None):
        self.ordem.append(("rascunho", dimensao))
        return {"analise": "Parágrafo positivo suficientemente longo para teste.\n\nParágrafo de desafios suficientemente longo para teste.", "sugestoes":["s1","s2","s3","s4"]}
    def pesquisar_validacao_dimensao(self, dimensao, municipio, indicadores, rascunho, estado=None, codigo_ibge=None):
        self.ordem.append(("web", dimensao))
        return "Pesquisa web sem atualização relevante para esta dimensão."
    def revisar_analise_dimensao(self, dimensao, municipio, porte, indicadores, rascunho, dados_contextuais_dimensao=None, validacao_web=None):
        self.ordem.append(("revisao", dimensao)); return rascunho
    def gerar_analise_geral(self, municipio, porte, dimensoes):
        self.ordem.append(("geral", None)); return "Síntese positiva.\n\nSíntese de desafios."


def test_ordem_pipeline_pos_rascunho(monkeypatch, tmp_path):
    # Planilha já normalizada para testar apenas a orquestração.
    dados={"municipio":"Cidade Teste", "populacao total estimada do municipio":10000, "estado":"MG", "cod municipio":1234567}
    # um indicador mapeado por dimensão
    dados.update({
      "indice da populacao total com atendimento de agua": 1,
      "indice de equipamentos de tecnologia disponiveis nas escolas publicas municipais": 1,
      "indice da populacao urbana com atendimento de esgoto": 1,
      "planejamento estrategico para a transformacao digital": 1,
    })
    df=pd.DataFrame([dados])
    monkeypatch.setattr("municipio_analise.pipeline.carregar_planilha", lambda cfg: df)
    cfg=Config(base_path=tmp_path, anthropic_api_key="a", gemini_api_key="g", pausa_entre_pesquisas_web=0)
    fake=FakeLLM()
    pipe=PipelineAnaliseMunicipio(cfg, llm_service=fake, seletor_chunks=FakeSelector())
    # Para este teste, force a classificação mínima por dimensão.
    dimensoes=list(DIMENSAO_PARA_CHAVE)
    contador={}
    def classificar(nome):
        if nome in {"estado","cod municipio"}: return None
        i=contador.setdefault("i",0); contador["i"]=i+1
        d=dimensoes[min(i,3)]
        return {"dimensao":d,"topico":"Teste","chunk_id":"teste"}
    pipe.classificador.classificar=classificar
    out=pipe.analisar("Cidade Teste", gerar_word=False)
    assert set(out["dimensoes"]) == set(DIMENSAO_PARA_CHAVE.values())
    assert fake.ordem[-1] == ("geral", None)
    for d in dimensoes:
        assert fake.ordem.index(("rascunho",d)) < fake.ordem.index(("web",d)) < fake.ordem.index(("revisao",d))
