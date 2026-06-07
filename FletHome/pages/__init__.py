# -*- coding: utf-8 -*-
"""
Pages module - importa dinamicamente tutti i moduli nella cartella pages
"""
import os
import glob
import importlib
import logging
from logging.handlers import TimedRotatingFileHandler

log = logging.getLogger(__name__)


# Ottieni tutti i file .py nella directory corrente
module_files = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))

# Lista dei nomi dei moduli da esportare
__all__ = []

for f in module_files:
    # Filtra solo i file ed escludi __init__.py
    if os.path.isfile(f) and not f.endswith("__init__.py"):
        # Estrai il nome del file senza estensione
        module_name = os.path.basename(f)[:-3]
        __all__.append(module_name)
        
        # Importa dinamicamente il modulo
        try:
            module = importlib.import_module(f".{module_name}", package=__name__)
            # Aggiungi il modulo al namespace corrente così da essere accessibile
            globals()[module_name] = module
        except Exception as e:
            log.error(f"Errore importazione modulo {module_name}: {e}")