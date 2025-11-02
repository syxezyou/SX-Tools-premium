# MXTools/utils/config_manager.py
import json
import os
from utils.logger import app_logger

CONFIG_FILE = "mxtools_config.json"

DEFAULT_CONFIG = {
    "accent_color": "#ff0000",  # Rouge par défaut
    "appearance_mode": "dark", # Peut être "light", "dark", "system"
    "font_family": "Consolas",
    "font_size": 11,
    "discord_bot_token": "" # L'utilisateur devra mettre son propre token ici
    # Ajoute d'autres paramètres par défaut ici si besoin
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # S'assurer que toutes les clés par défaut sont présentes
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                app_logger.info(f"Configuration loaded from {CONFIG_FILE}")
                return config
        except json.JSONDecodeError:
            app_logger.error(f"Error decoding JSON from {CONFIG_FILE}. Loading default config.")
            return DEFAULT_CONFIG.copy() # Retourne une copie pour éviter la modification de l'original
        except Exception as e:
            app_logger.error(f"Error loading config: {e}. Loading default config.")
            return DEFAULT_CONFIG.copy()
    else:
        app_logger.info(f"Config file {CONFIG_FILE} not found. Loading default config.")
        return DEFAULT_CONFIG.copy()

def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        app_logger.info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        app_logger.error(f"Error saving config: {e}")

# Charger la configuration au démarrage du module pour qu'elle soit disponible
# current_config = load_config() # On le fera dans MainWindow pour appliquer dynamiquement