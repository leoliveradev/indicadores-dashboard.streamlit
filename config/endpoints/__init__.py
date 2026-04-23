# config/endpoints/__init__.py

from .internet import InternetEndpoints
from .telefonia_movil import MovilEndpoints
from .tv import TVEndpoints
from .telefonia_fija import FijaEndpoints
from .mercado_postal import PostalEndpoints
from .portabilidad import PortabilidadEndpoints

# Esto permite controlar qué se exporta cuando alguien hace: from config.endpoints import *
__all__ = [
    "InternetEndpoints",
    "MovilEndpoints",
    "TVEndpoints",
    "FijaEndpoints",
    "PostalEndpoints",
    "PortabilidadEndpoints",
]