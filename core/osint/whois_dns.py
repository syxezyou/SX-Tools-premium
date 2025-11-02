import whois # python-whois
import dns.resolver # dnspython
from utils.logger import app_logger

def get_whois_info(domain_or_ip):
    app_logger.info(f"Performing WHOIS lookup for: {domain_or_ip}")
    if not domain_or_ip:
        return "Error: Domain or IP cannot be empty."
    try:
        w = whois.whois(domain_or_ip)
        if w.text: # whois.whois peut renvoyer un objet avec text=None si rien n'est trouvé
            app_logger.info(f"WHOIS lookup successful for {domain_or_ip}")
            # L'objet w peut avoir beaucoup d'attributs, w.text contient la sortie brute
            # return str(w) # Donne toutes les infos structurées si disponibles
            return w.text # Retourne le texte brut, souvent plus complet
        else:
            app_logger.warning(f"No WHOIS data found for {domain_or_ip}")
            return f"No WHOIS data found for {domain_or_ip}."
            
    except whois.parser.PywhoisError as e: # Gère les erreurs spécifiques de la lib
        app_logger.error(f"WHOIS lookup failed for {domain_or_ip}: {e} (Possibly TLD not supported or network issue)")
        return f"WHOIS lookup failed: {e}\n(This TLD might not be supported or there could be a network issue. Try using a command-line WHOIS tool for this TLD if problems persist.)"
    except Exception as e:
        app_logger.error(f"Unexpected error during WHOIS lookup for {domain_or_ip}: {e}", exc_info=True)
        return f"An unexpected error occurred during WHOIS lookup: {e}"


def get_dns_records(domain):
    app_logger.info(f"Performing DNS lookup for: {domain}")
    if not domain:
        return "Error: Domain cannot be empty."

    results = f"DNS Records for: {domain}\n"
    results += "----------------------------------------\n"
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    found_any = False

    for r_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, r_type)
            results += f"\n--- {r_type} Records ---\n"
            for rdata in answers:
                results += f"{rdata.to_text()}\n"
            found_any = True
            app_logger.debug(f"Found {r_type} records for {domain}")
        except dns.resolver.NoAnswer:
            results += f"\n--- {r_type} Records ---\nNo {r_type} records found.\n"
            app_logger.debug(f"No {r_type} records found for {domain}")
        except dns.resolver.NXDOMAIN:
            app_logger.warning(f"DNS lookup failed for {domain}: NXDOMAIN (Non-Existent Domain)")
            return f"Error: Domain '{domain}' does not exist (NXDOMAIN)."
        except dns.resolver.Timeout:
            app_logger.warning(f"DNS lookup timeout for {domain} (type {r_type})")
            results += f"\n--- {r_type} Records ---\nQuery timed out.\n"
        except dns.exception.DNSException as e: # Attrape d'autres exceptions DNS
            app_logger.warning(f"DNS error for {domain} (type {r_type}): {e}")
            results += f"\n--- {r_type} Records ---\nError querying {r_type}: {e}\n"
    
    if not found_any and not "Error: Domain" in results: # Si aucune erreur NXDOMAIN mais aucun record
        results = f"No DNS records found for {domain} across common types."

    app_logger.info(f"DNS lookup complete for {domain}")
    return results

if __name__ == '__main__':
    test_domain_whois = "google.com"
    print("--- WHOIS Test ---")
    print(get_whois_info(test_domain_whois))
    
    test_domain_dns = "google.com"
    print("\n--- DNS Test ---")
    print(get_dns_records(test_domain_dns))

    test_nxdomain = "thisshouldnotexist12345.com"
    print("\n--- DNS NXDOMAIN Test ---")
    print(get_dns_records(test_nxdomain))