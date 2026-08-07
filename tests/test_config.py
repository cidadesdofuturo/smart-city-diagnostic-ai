import pytest

from municipio_analise.config import Config


class TestConfig:
    def test_caminho_planilha(self):
        config = Config(base_path="/tmp/base", nome_arquivo_planilha="dados.xlsx", api_key="x")
        assert config.caminho_planilha == "/tmp/base/dados.xlsx"

    def test_caminho_relatorio_substitui_espacos(self):
        config = Config(base_path="/tmp/base", api_key="x")
        assert config.caminho_relatorio("Belo Horizonte") == "/tmp/base/Relatorio_Belo_Horizonte.docx"

    def test_api_key_do_construtor_tem_prioridade(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_API_KEY", "da-variavel-de-ambiente")
        config = Config(api_key="da-config")
        assert config.api_key == "da-config"

    def test_api_key_cai_para_variavel_de_ambiente(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_API_KEY", "da-variavel-de-ambiente")
        config = Config()
        assert config.api_key == "da-variavel-de-ambiente"

    def test_validar_api_key_levanta_erro_se_ausente(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        config = Config(api_key=None)
        with pytest.raises(ValueError):
            config.validar_api_key()

    def test_config_padrao_reflete_notebook_atualizado(self):
        config = Config(api_key="x")
        assert config.temperature == 0.2
        assert config.top_p == 0.9
        assert config.modelo_embedding == "models/gemini-embedding-001"

    def test_caminhos_faiss(self):
        config = Config(base_path="/tmp/base", api_key="x")
        assert config.caminho_faiss_topicos == "/tmp/base/faiss_index_topicos"
        assert config.caminho_faiss_chunks == "/tmp/base/faiss_index_chunks"
