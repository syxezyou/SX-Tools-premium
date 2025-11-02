# MXTools/core/gaming/performance_booster.py
import subprocess
import os
import sys
import shutil
import winreg # Pour modifier le registre Windows
from utils.logger import app_logger
from core.ano.anonymizer import is_admin

# GUIDs pour les modes d'alimentation de Windows
POWER_PLAN_HIGH_PERFORMANCE = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
POWER_PLAN_BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"

def _run_command(command):
    """Exécute une commande shell et retourne le succès et la sortie."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        app_logger.error(f"Command failed: {command}\n{e.stderr}")
        return False, e.stderr.strip()

def clear_temp_files():
    """Nettoie les dossiers temporaires de l'utilisateur et de Windows."""
    # Utiliser les variables d'environnement pour plus de robustesse
    paths_to_clear = [os.environ.get("TEMP"), os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")]
    
    deleted_files_count = 0
    deleted_folders_count = 0
    skipped_count = 0
    summary = ""

    for path in paths_to_clear:
        if not (path and os.path.exists(path)):
            continue

        summary += f"Cleaning folder: {path}\n"
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                    deleted_files_count += 1
                except OSError:
                    skipped_count += 1
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                    deleted_folders_count += 1
                except OSError:
                    skipped_count += 1
    
    summary += f"\nCleanup Summary:\n  - Deleted files: {deleted_files_count}\n  - Deleted folders: {deleted_folders_count}\n  - Skipped items (in use): {skipped_count}\n"
    return summary

def apply_fps_boost():
    """Applique les optimisations pour les FPS."""
    if not is_admin():
        return "Error: Administrator rights are required for this feature."
    
    results = "--- Applying FPS Boost ---\n\n"
    
    # 1. Changer le mode d'alimentation en "Performances élevées"
    results += "1. Setting power plan to High Performance...\n"
    success, output = _run_command(f"powercfg /setactive {POWER_PLAN_HIGH_PERFORMANCE}")
    results += "  - Status: " + ("Success" if success else f"Failed\n{output}") + "\n\n"
    
    # 2. Nettoyer les fichiers temporaires
    results += "2. Clearing temporary files...\n"
    results += clear_temp_files() + "\n"
    
    results += "\nFPS Boost applied successfully!"
    app_logger.info("FPS Boost applied.")
    return results

def revert_fps_boost():
    """Rétablit les paramètres par défaut."""
    if not is_admin():
        return "Error: Administrator rights are required for this feature."
        
    results = "--- Reverting FPS Boost ---\n\n"
    
    # Rétablir le mode d'alimentation en "Utilisation normale"
    results += "1. Setting power plan back to Balanced...\n"
    success, output = _run_command(f"powercfg /setactive {POWER_PLAN_BALANCED}")
    results += "  - Status: " + ("Success" if success else f"Failed\n{output}") + "\n\n"
    
    results += "\nSystem settings reverted."
    app_logger.info("FPS Boost reverted.")
    return results

def _set_nagle_algorithm(enabled=True):
    """Active ou désactive l'algorithme de Nagle via le registre."""
    try:
        # Chemin vers les interfaces réseau dans le registre
        interfaces_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interfaces_path) as interfaces_key:
            num_interfaces = winreg.QueryInfoKey(interfaces_key)[0]
            for i in range(num_interfaces):
                interface_guid = winreg.EnumKey(interfaces_key, i)
                interface_path = f"{interfaces_path}\\{interface_guid}"
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interface_path, 0, winreg.KEY_WRITE) as interface_key:
                        if enabled:
                            # Pour réactiver Nagle, on supprime les clés
                            try:
                                winreg.DeleteValue(interface_key, "TcpAckFrequency")
                            except FileNotFoundError:
                                pass # La clé n'existait pas, c'est ok
                            try:
                                winreg.DeleteValue(interface_key, "TCPNoDelay")
                            except FileNotFoundError:
                                pass
                        else:
                            # Pour désactiver Nagle, on crée/modifie les clés
                            winreg.SetValueEx(interface_key, "TcpAckFrequency", 0, winreg.REG_DWORD, 1)
                            winreg.SetValueEx(interface_key, "TCPNoDelay", 0, winreg.REG_DWORD, 1)
                except Exception as e:
                    app_logger.warning(f"Could not modify registry for interface {interface_guid}: {e}")
        return True, "Nagle algorithm settings updated for all network interfaces."
    except Exception as e:
        app_logger.error(f"Failed to access registry for Nagle algorithm: {e}")
        return False, f"Failed to access registry: {e}"

def apply_network_boost():
    """Applique les optimisations réseau."""
    if not is_admin():
        return "Error: Administrator rights are required for this feature."
    
    results = "--- Applying Network Boost ---\n\n"
    
    # 1. Désactiver l'algorithme de Nagle
    results += "1. Disabling Nagle's Algorithm for lower latency...\n"
    success, output = _set_nagle_algorithm(enabled=False)
    results += f"  - Status: {'Success' if success else 'Failed'}\n  - Info: {output}\n\n"
    
    # 2. Vider le cache DNS
    results += "2. Flushing DNS cache...\n"
    success, output = _run_command("ipconfig /flushdns")
    results += "  - Status: " + ("Success" if success else f"Failed\n{output}") + "\n\n"
    
    results += "\nNetwork Boost applied successfully!"
    return results

def revert_network_boost():
    """Rétablit les paramètres réseau par défaut."""
    if not is_admin():
        return "Error: Administrator rights are required for this feature."
    
    results = "--- Reverting Network Boost ---\n\n"
    results += "1. Re-enabling Nagle's Algorithm (default)...\n"
    success, output = _set_nagle_algorithm(enabled=True)
    results += f"  - Status: {'Success' if success else 'Failed'}\n  - Info: {output}\n\n"
    
    results += "\nNetwork settings reverted to default."
    return results