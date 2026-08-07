"""municipio_analise — análise institucional municipal do Cidades do Futuro."""
from .agent import AgenteAnaliseMunicipal
from .config import Config
from .pipeline import PipelineAnaliseMunicipio

__all__ = ["Config", "PipelineAnaliseMunicipio", "AgenteAnaliseMunicipal"]
__version__ = "1.1.0"
