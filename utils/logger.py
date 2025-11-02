import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """Fonction pour configurer un logger."""
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5) # 10MB per file, 5 backups
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Éviter d'ajouter plusieurs handlers si le logger existe déjà (ex: rechargement de module)
    if not logger.hasHandlers():
        logger.addHandler(handler)
        # Optionnel: ajouter un StreamHandler pour voir les logs en console pendant le dev
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(formatter)
        # logger.addHandler(console_handler)


    return logger

# Logger global pour les modules (si besoin d'un accès rapide sans passer par param)
app_logger = setup_logger('mxtools_global', 'logs/mxtools_global.log')