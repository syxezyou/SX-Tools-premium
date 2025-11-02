import requests
import threading
from queue import Queue
from utils.logger import app_logger
import os

NUM_THREADS_SUBDOMAIN = 10
sub_q = Queue()

def check_subdomain(subdomain, domain, found_subdomains_list):
    target_url_http = f"http://{subdomain}.{domain}"
    target_url_https = f"https://{subdomain}.{domain}"
    
    for url_to_check in [target_url_http, target_url_https]:
        try:
            response = requests.get(url_to_check, timeout=3, allow_redirects=False, headers={'User-Agent': 'SXTOOLS PREMIUMSubdomainFinder/1.0'})
            # On considère un succès si ce n'est pas une redirection vers la page principale
            # ou une page d'erreur standard (404). Certains serveurs renvoient 200 pour des sous-domaines inexistants (wildcard DNS).
            # C'est une heuristique simple. Un vrai outil ferait plus d'analyses.
            if response.status_code < 400 : # 2xx, 3xx
                app_logger.info(f"Found potential subdomain: {url_to_check} (Status: {response.status_code})")
                found_subdomains_list.append(url_to_check)
                return # Trouvé, pas besoin de vérifier l'autre protocole
        except requests.exceptions.ConnectionError:
            pass # Ne peut pas se connecter, probablement n'existe pas
        except requests.exceptions.Timeout:
            app_logger.warning(f"Timeout checking {url_to_check}")
        except requests.exceptions.RequestException as e:
            app_logger.debug(f"Request exception for {url_to_check}: {e}")


def subdomain_worker(domain, found_subdomains_list):
    while not sub_q.empty():
        sub = sub_q.get()
        check_subdomain(sub, domain, found_subdomains_list)
        sub_q.task_done()

def find_subdomains(domain, wordlist_path="wordlists/subdomains_common.txt"):
    app_logger.info(f"Starting subdomain search for {domain} using wordlist {wordlist_path}")
    if not domain:
        return "Error: Domain cannot be empty."
    
    if not os.path.exists(wordlist_path):
        app_logger.error(f"Wordlist not found: {wordlist_path}")
        return f"Error: Wordlist not found at '{wordlist_path}'."

    try:
        with open(wordlist_path, 'r') as f:
            wordlist = [line.strip() for line in f if line.strip()]
    except Exception as e:
        app_logger.error(f"Error reading wordlist {wordlist_path}: {e}")
        return f"Error reading wordlist: {e}"

    if not wordlist:
        return "Error: Wordlist is empty or could not be read."

    app_logger.info(f"Loaded {len(wordlist)} subdomains from wordlist.")

    for sub in wordlist:
        sub_q.put(sub)

    found_subdomains = []
    threads = []
    for _ in range(min(NUM_THREADS_SUBDOMAIN, len(wordlist))):
        t = threading.Thread(target=subdomain_worker, args=(domain, found_subdomains), daemon=True)
        threads.append(t)
        t.start()

    sub_q.join()

    result_str = f"Subdomain Scan Results for {domain}:\n"
    result_str += "----------------------------------------\n"
    if found_subdomains:
        for f_sub in sorted(list(set(found_subdomains))): # set pour dédupliquer
            result_str += f"{f_sub}\n"
        app_logger.info(f"Found {len(found_subdomains)} potential subdomains for {domain}.")
    else:
        result_str += "No subdomains found with the given wordlist.\n"
        app_logger.info(f"No subdomains found for {domain} with wordlist {wordlist_path}.")
    
    return result_str

if __name__ == '__main__':
    test_domain = "google.com" # Un domaine avec beaucoup de sous-domaines connus
    # Créez un petit wordlists/subdomains_common.txt pour tester:
    # www
    # mail
    # ftp
    # api
    # dev
    # m
    # blog
    # support
    # images
    # accounts
    
    # Assurez-vous que le fichier wordlists/subdomains_common.txt existe avec quelques entrées
    if not os.path.exists("wordlists"): os.makedirs("wordlists")
    if not os.path.exists("wordlists/subdomains_common.txt"):
        with open("wordlists/subdomains_common.txt", "w") as f:
            f.write("www\nmail\napi\ndevelop\n")

    print(f"Searching subdomains for {test_domain}...")
    results = find_subdomains(test_domain)
    print(results)