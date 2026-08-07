from municipio_analise.config import Config


def test_modelo_e_escala_configurada_no_codigo(tmp_path):
    cfg = Config(base_path=tmp_path, api_key="teste")
    assert cfg.modelo == "gemini-3.6-flash"
    assert cfg.max_output_tokens == 4096
    assert not hasattr(cfg, "temperature")
    assert not hasattr(cfg, "top_p")
