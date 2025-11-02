# SXTOOLS PREMIUM/core/ano/anonymizer.py
import subprocess
import sys
import os
import random
import string
import psutil # Vous devrez peut-être installer cette librairie: pip install psutil
from utils.logger import app_logger

def is_admin():
    """Vérifie si le script est exécuté avec des privilèges d'administrateur."""
    try:
        if sys.platform.startswith('win'):
            return os.getuid() == 0
        else: # Pour Linux/macOS
            return os.geteuid() == 0
    except AttributeError: # os.getuid() n'existe pas sur Windows standard
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except (ImportError, AttributeError):
            return False

def generate_random_mac():
    """Génère une adresse MAC aléatoire (localement administrée)."""
    # Le deuxième caractère doit être 2, 6, A, ou E pour une adresse locale
    mac = [0x02, random.randint(0x00, 0x7f), random.randint(0x00, 0xff),
           random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))

def generate_random_hostname(length=12):
    """Génère un nom d'hôte aléatoire."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def change_hostname(new_hostname):
    """Change le nom d'hôte du système."""
    app_logger.info(f"Attempting to change hostname to: {new_hostname}")
    if sys.platform.startswith('win'):
        command = f'wmic computersystem where name="%COMPUTERNAME%" call rename name="{new_hostname}"'
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        command = f'sudo hostnamectl set-hostname {new_hostname}'
    else:
        return "Unsupported OS for hostname change."

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        app_logger.info(f"Hostname change command output: {result.stdout}")
        return f"Hostname change initiated to '{new_hostname}'. A system restart is required for changes to take full effect."
    except subprocess.CalledProcessError as e:
        app_logger.error(f"Failed to change hostname: {e.stderr}")
        return f"Error changing hostname: {e.stderr}\nMake sure to run as administrator."

def spoof_mac_address(interface_name, new_mac):
    """Spoofe l'adresse MAC d'une interface réseau."""
    app_logger.info(f"Attempting to spoof MAC for interface '{interface_name}' to '{new_mac}'")
    if sys.platform.startswith('win'):
        # C'est complexe sur Windows via des commandes simples.
        # La méthode la plus fiable est via le registre, mais c'est risqué.
        # Une alternative est PowerShell.
        command = f'powershell -Command "Set-NetAdapter -Name \'{interface_name}\' -MacAddress \'{new_mac.replace(":", "-")}\'"'
    elif sys.platform.startswith('linux'):
        command = f'sudo ip link set dev {interface_name} down && sudo ip link set dev {interface_name} address {new_mac} && sudo ip link set dev {interface_name} up'
    elif sys.platform.startswith('darwin'): # macOS
        command = f'sudo ifconfig {interface_name} ether {new_mac}'
    else:
        return "Unsupported OS for MAC spoofing."

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        app_logger.info(f"MAC spoof command output: {result.stdout}")
        return f"MAC address for '{interface_name}' spoofed to '{new_mac}'. Network connection may be temporarily interrupted."
    except subprocess.CalledProcessError as e:
        app_logger.error(f"Failed to spoof MAC address: {e.stderr}")
        return f"Error spoofing MAC: {e.stderr}\nMake sure to run as administrator and the interface name is correct."

def change_all():
    """Fonction principale qui change le nom d'hôte et l'adresse MAC."""
    if not is_admin():
        return "Error: This feature requires administrator privileges. Please restart SXTOOLS PREMIUM as an administrator."

    results = "--- Anonymization Process ---\n"
    
    # 1. Changer le nom d'hôte
    new_hostname = "MX-" + generate_random_hostname()
    results += f"Changing hostname to {new_hostname}...\n"
    results += change_hostname(new_hostname) + "\n\n"

    # 2. Changer l'adresse MAC de la première interface active
    # On cible la première interface non-loopback qui a une adresse.
    # C'est une simplification, une version avancée permettrait de choisir l'interface.
    interfaces = psutil.net_if_addrs()
    target_interface = None
    for name, addrs in interfaces.items():
        if name != 'lo' and not name.lower().startswith('loopback'):
            target_interface = name
            break
    
    if target_interface:
        new_mac = generate_random_mac()
        results += f"Changing MAC address for interface '{target_interface}' to {new_mac}...\n"
        results += spoof_mac_address(target_interface, new_mac) + "\n"
    else:
        results += "Could not find a suitable network interface to spoof."

    return results

def clear_event_logs():
    """Efface tous les journaux d'événements Windows."""
    if not is_admin():
        return "Error: Administrator rights are required to clear event logs."
    if not sys.platform.startswith('win'):
        return "Error: This feature is only available on Windows."

    app_logger.warning("Initiating Windows Event Log clearing.")
    results = "--- Clearing Windows Event Logs ---\n\n"
    try:
        # Commande PowerShell pour obtenir et effacer chaque journal
        command = 'powershell -Command "Get-WinEvent -ListLog * | ForEach-Object { wevtutil.exe cl $_.LogName }"'
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if process.returncode == 0:
            results += "All Windows Event Logs have been cleared successfully.\n"
            app_logger.info("Successfully cleared all event logs.")
        else:
            # Certaines erreurs sont normales (journaux en cours d'utilisation), mais on les logue quand même
            error_output = process.stderr or process.stdout
            results += f"Completed with some errors (this can be normal for logs in use):\n{error_output}\n"
            app_logger.warning(f"Event log clearing process completed with errors: {error_output}")

    except Exception as e:
        results += f"An unexpected error occurred: {e}\n"
        app_logger.error(f"Failed to clear event logs: {e}", exc_info=True)

    return results

def toggle_telemetry(enable=False):
    """Active ou désactive les principaux services de télémétrie de Windows."""
    if not is_admin():
        return "Error: Administrator rights are required to modify services."
    if not sys.platform.startswith('win'):
        return "Error: This feature is only available on Windows."

    services = ["DiagTrack", "dmwappushservice"] # Principaux services de télémétrie
    action = "start" if enable else "stop"
    config = "auto" if enable else "disabled"
    status_text = "Enabled" if enable else "Disabled"
    
    results = f"--- Setting Telemetry Services to: {status_text} ---\n\n"
    app_logger.info(f"Setting telemetry services to {status_text}.")

    for service in services:
        subprocess.run(f'sc {action} {service}', shell=True, capture_output=True) # Tente d'arrêter/démarrer
        result = subprocess.run(f'sc config {service} start={config}', shell=True, capture_output=True, text=True)
        results += f"Service '{service}':\n  - Status: {'Configuration updated.' if result.returncode == 0 else 'Failed or not found.'}\n"

    results += "\nTelemetry services configuration updated."
    return results