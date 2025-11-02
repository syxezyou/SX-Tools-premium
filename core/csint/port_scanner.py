import socket
import threading
from queue import Queue
from utils.logger import app_logger

# Un pool de threads pour le scan
NUM_THREADS = 20
q = Queue()

def port_scan(target_host, port):
    """Scanne un port unique."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5) # Timeout rapide pour ne pas bloquer longtemps
        result = sock.connect_ex((target_host, port))
        if result == 0:
            return True
        return False
    except socket.gaierror: # Erreur de résolution de nom
        # Géré au niveau supérieur
        raise
    except Exception:
        return False # Autres erreurs, port considéré comme fermé ou inaccessible
    finally:
        sock.close()

def worker(target_ip, open_ports_list, errors_list):
    """Travailleur pour le pool de threads."""
    while not q.empty():
        port = q.get()
        if port_scan(target_ip, port):
            open_ports_list.append(port)
        q.task_done()

def parse_ports(ports_str):
    """Parse la chaîne de ports (ex: "80,443,21-25,1000")."""
    parsed_ports = set()
    if not ports_str.strip(): # Si vide, scanner les ports communs
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135,139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
        return sorted(list(common_ports))

    parts = ports_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            try:
                start_port = int(start)
                end_port = int(end)
                if 0 < start_port <= end_port <= 65535:
                    for p in range(start_port, end_port + 1):
                        parsed_ports.add(p)
                else:
                    raise ValueError("Port range invalid.")
            except ValueError:
                raise ValueError(f"Invalid port range: {part}")
        else:
            try:
                port_num = int(part)
                if 0 < port_num <= 65535:
                    parsed_ports.add(port_num)
                else:
                    raise ValueError("Port number out of range.")
            except ValueError:
                raise ValueError(f"Invalid port number: {part}")
    return sorted(list(parsed_ports))


def scan_ports_handler(target_host, ports_str):
    app_logger.info(f"Port scan initiated for target: {target_host}, ports: {ports_str}")
    if not target_host:
        return "Error: Target host cannot be empty."

    try:
        target_ip = socket.gethostbyname(target_host)
    except socket.gaierror:
        app_logger.error(f"Cannot resolve hostname: {target_host}")
        return f"Error: Cannot resolve hostname '{target_host}'"

    try:
        ports_to_scan = parse_ports(ports_str)
        if not ports_to_scan: # S'il n'y a pas de ports après parsing (ex: string vide après trim)
             ports_to_scan = parse_ports("") # Utiliser les ports par défaut
    except ValueError as e:
        app_logger.error(f"Invalid port specification: {ports_str} - {e}")
        return f"Error: Invalid port specification - {e}"

    app_logger.info(f"Scanning {target_ip} for ports: {ports_to_scan}")

    for port in ports_to_scan:
        q.put(port)

    open_ports = []
    errors = [] # Pourrait être utilisé pour collecter des erreurs spécifiques par thread

    threads = []
    for _ in range(min(NUM_THREADS, len(ports_to_scan))): # Ne pas créer plus de threads que de ports
        t = threading.Thread(target=worker, args=(target_ip, open_ports, errors), daemon=True)
        threads.append(t)
        t.start()

    q.join() # Attendre que tous les items de la queue soient traités

    # S'assurer que tous les threads sont terminés (normalement q.join() suffit)
    # for t in threads:
    #    t.join()

    result_str = f"Port Scan Results for {target_host} ({target_ip}):\n"
    result_str += "----------------------------------------\n"
    if open_ports:
        open_ports.sort()
        for port in open_ports:
            service_name = "unknown"
            try:
                service_name = socket.getservbyport(port)
            except OSError: # ou socket.error
                pass # Garder "unknown"
            result_str += f"Port {port} ({service_name}): Open\n"
        app_logger.info(f"Open ports found on {target_ip}: {open_ports}")
    else:
        result_str += "No open ports found in the specified range.\n"
        app_logger.info(f"No open ports found on {target_ip} for specified range.")
    
    if errors:
        result_str += "\nErrors during scan:\n" + "\n".join(errors)

    return result_str

if __name__ == '__main__':
    # Test
    # Pour tester, il faut une machine cible. Utilisez 'localhost' ou une IP de test.
    # Soyez prudent et n'utilisez que des cibles que vous avez la permission de scanner.
    target = "scanme.nmap.org" # Site de test de Nmap
    # target = "localhost"
    ports_spec = "21-25,80,443"
    # ports_spec = "" # Test des ports par défaut

    print(f"Scanning {target} for ports {ports_spec if ports_spec else 'default'}...")
    results = scan_ports_handler(target, ports_spec)
    print(results)