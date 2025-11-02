# MXTools/core/csint/connection_monitor.py
import psutil
from collections import Counter
from utils.logger import app_logger

def monitor_connections(threshold=20):
    """
    Surveille les connexions réseau et détecte les IP avec un nombre élevé de connexions.
    """
    app_logger.info("Starting network connection monitoring.")
    results = "--- Active Network Connections ---\n\n"
    
    try:
        connections = psutil.net_connections(kind='inet')
        ip_counts = Counter()

        for conn in connections:
            if conn.raddr: # Si une adresse distante existe
                ip_counts[conn.raddr.ip] += 1
        
        if not ip_counts:
            return "No active remote connections found."

        results += f"{'IP Address':<20} | {'Connections':<15}\n"
        results += "-"*40 + "\n"

        suspicious_ips = []
        for ip, count in ip_counts.most_common():
            results += f"{ip:<20} | {count:<15}\n"
            if count > threshold:
                suspicious_ips.append(f"{ip} (Connections: {count})")

        if suspicious_ips:
            results += "\n--- ⚠️ Suspicious Activity Detected! ---\n"
            results += "The following IPs have an unusually high number of connections:\n"
            results += "\n".join(suspicious_ips)

        return results

    except Exception as e:
        app_logger.error(f"Failed to monitor connections: {e}")
        return f"Error monitoring connections: {e}"