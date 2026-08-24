from municipio_analise import Config


def test_config_nova_arquitetura(tmp_path):
    cfg = Config(base_path=tmp_path, anthropic_api_key="anthropic-test", gemini_api_key="gemini-test")
    assert cfg.modelo == "claude-sonnet-4-6"
    assert cfg.modelo_embedding == "models/gemini-embedding-001"
    assert cfg.max_usos_web_por_dimensao == 5
    assert cfg.max_indicadores_rag_por_dimensao == 5
    assert cfg.k_candidatos_rag_por_indicador == 8
    assert cfg.max_chunks_carta_completa == 8
    assert cfg.modo_rag_carta == "completa"
