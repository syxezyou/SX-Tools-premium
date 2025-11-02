# SXTOOLS PREMIUM/main.py
import customtkinter as ctk
from gui.main_window import MainWindow
from utils.logger import setup_logger, app_logger
from utils.config_manager import load_config # Importer load_config
import os
import sys
import ctypes
from core.ano.anonymizer import is_admin

def main():
    # Vérifier les privilèges d'administrateur au démarrage
    if sys.platform.startswith('win'):
        if not is_admin():
            app_logger.warning("Not running as admin. Attempting to re-launch with admin rights.")
            try:
                # Relancer le script avec des privilèges d'administrateur
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            except Exception as e:
                app_logger.error(f"Failed to elevate privileges: {e}")
            sys.exit(0) # Quitter le processus non-admin

    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists("wordlists"):
        os.makedirs("wordlists")
        with open("wordlists/subdomains_common.txt", "w") as f:
            f.write("www\nmail\nftp\nadmin\napi\n")

    main_logger = setup_logger('main_app', 'logs/mxtools.log')
    main_logger.info("SXTOOLS PREMIUM application started.")

    # Charger la configuration pour le thème initial
    config = load_config()
    ctk.set_appearance_mode(config.get("appearance_mode", "dark")) # Utiliser la valeur du config ou dark par défaut
    # La couleur d'accentuation sera gérée dynamiquement dans MainWindow

    app = MainWindow(config=config) # Passer la config à MainWindow
    app.mainloop()

if __name__ == "__main__":
    main()