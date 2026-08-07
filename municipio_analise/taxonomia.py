CHUNKS_GERAIS = ['conceito_brasileiro_de_cidades_inteligentes',
 'diversidade_territorial_e_reducao_de_desigualdades',
 'transformacao_digital_adaptada_a_capacidade_municipal']

CHUNKS_ECONOMICA = ['agua_e_esgoto',
 'residuos_solidos',
 'transporte',
 'vias_publicas',
 'conectividade',
 'inovacao',
 'gestao_urbana',
 'servicos_online',
 'dados_abertos']

CHUNKS_SOCIOCULTURAL = ['educacao',
 'cultura_e_esporte',
 'saude',
 'seguranca_publica',
 'defesa_civil',
 'inclusao_digital',
 'inclusao_e_equidade',
 'participacao_cidada']

CHUNKS_MEIO_AMBIENTE = ['agua_e_saneamento',
 'residuos_solidos',
 'areas_verdes',
 'qualidade_do_ar_e_emissoes',
 'energia_e_iluminacao_publica']

CHUNKS_CAPACIDADES_INSTITUCIONAIS = ['governanca_e_planejamento',
 'infraestrutura_de_ti',
 'servicos_publicos_digitais',
 'monitoramento_e_transparencia',
 'dados_e_seguranca_da_informacao']

DIMENSOES = {
    "Econômica": {"prefixo": "economica", "topicos": CHUNKS_ECONOMICA},
    "Sociocultural": {"prefixo": "sociocultural", "topicos": CHUNKS_SOCIOCULTURAL},
    "Meio Ambiente": {"prefixo": "meio_ambiente", "topicos": CHUNKS_MEIO_AMBIENTE},
    "Capacidades Institucionais": {"prefixo": "institucional", "topicos": CHUNKS_CAPACIDADES_INSTITUCIONAIS},
}


PALAVRAS_CHAVE_TOPICO = {'agua_e_esgoto': ['água', 'esgoto', 'saneamento básico', 'abastecimento'],
 'residuos_solidos': ['resíduos sólidos', 'lixo', 'coleta seletiva', 'reciclagem'],
 'transporte': ['transporte público', 'mobilidade urbana', 'ônibus'],
 'vias_publicas': ['vias públicas', 'pavimentação', 'trânsito', 'mobiliário urbano'],
 'conectividade': ['conectividade', 'internet', 'banda larga', 'wi-fi'],
 'inovacao': ['inovação', 'empreendedorismo', 'startups'],
 'gestao_urbana': ['gestão urbana', 'planejamento urbano', 'uso do solo', 'plano diretor'],
 'servicos_online': ['serviços online', 'serviços digitais', 'atendimento digital', 'governo digital'],
 'dados_abertos': ['dados abertos', 'portal de dados', 'transparência de dados'],
 'educacao': ['educação', 'escola', 'ensino'],
 'cultura_e_esporte': ['cultura', 'esporte', 'lazer'],
 'saude': ['saúde', 'atenção primária', 'telessaúde', 'telemedicina'],
 'seguranca_publica': ['segurança pública', 'violência', 'policiamento'],
 'defesa_civil': ['defesa civil', 'risco', 'desastre'],
 'inclusao_digital': ['inclusão digital', 'acesso digital', 'letramento digital'],
 'inclusao_e_equidade': ['inclusão', 'equidade', 'acessibilidade', 'grupos vulneráveis'],
 'participacao_cidada': ['participação cidadã', 'participação social', 'controle social'],
 'agua_e_saneamento': ['água', 'saneamento', 'recursos hídricos'],
 'areas_verdes': ['áreas verdes', 'parques', 'arborização'],
 'qualidade_do_ar_e_emissoes': ['qualidade do ar', 'emissões', 'poluição'],
 'energia_e_iluminacao_publica': ['energia', 'iluminação pública', 'eficiência energética'],
 'governanca_e_planejamento': ['governança', 'planejamento estratégico', 'plano diretor'],
 'infraestrutura_de_ti': ['infraestrutura de ti', 'tecnologia da informação', 'sistemas municipais'],
 'servicos_publicos_digitais': ['serviços públicos digitais', 'digitalização'],
 'monitoramento_e_transparencia': ['monitoramento', 'transparência', 'prestação de contas'],
 'dados_e_seguranca_da_informacao': ['proteção de dados', 'segurança da informação', 'lgpd']}


TOPICOS_SEM_CHUNK_NA_CARTA = ['economica_transporte',
 'economica_vias_publicas',
 'sociocultural_cultura_e_esporte',
 'sociocultural_saude',
 'sociocultural_seguranca_publica',
 'sociocultural_defesa_civil',
 'meio_ambiente_agua_e_saneamento',
 'meio_ambiente_residuos_solidos',
 'meio_ambiente_areas_verdes',
 'institucional_servicos_publicos_digitais']


DIMENSAO_PARA_CHAVE = {
    "Econômica": "economica",
    "Sociocultural": "sociocultural",
    "Meio Ambiente": "meio_ambiente",
    "Capacidades Institucionais": "capacidades_institucionais",
}
