# SXTOOLS PREMIUM/core/csint/url_analyzer.py
import requests
from urllib.parse import urlparse
from utils.logger import app_logger

def analyze_url(url_string):
    """
    Analyzes a URL for basic syntax, components, and checks for suspicious redirections.
    """
    app_logger.info(f"Analyzing URL: {url_string}")
    if not url_string:
        return "Error: URL string cannot be empty."

    results = f"URL Analysis for: {url_string}\n"
    results += "----------------------------------------\n"

    # 1. Syntax Check (basic using urlparse)
    try:
        parsed_url = urlparse(url_string)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            results += "Syntax: Invalid URL structure (missing scheme or netloc).\n"
            app_logger.warning(f"Invalid URL structure for: {url_string}")
            # On peut s'arrêter ici ou essayer de continuer avec ce qu'on a
            # return results # Décommenter pour arrêter l'analyse ici
        else:
            results += "Syntax: Appears to be a valid URL structure.\n"
            results += f"  Scheme: {parsed_url.scheme}\n"
            results += f"  Netloc (domain): {parsed_url.netloc}\n"
            results += f"  Path: {parsed_url.path}\n"
            results += f"  Params: {parsed_url.params}\n"
            results += f"  Query: {parsed_url.query}\n"
            results += f"  Fragment: {parsed_url.fragment}\n"

    except ValueError as e:
        results += f"Syntax: Error parsing URL - {e}\n"
        app_logger.error(f"Error parsing URL {url_string}: {e}")
        return results # Arrêter si parsing initial échoue

    # 2. Redirection Check (simple, sans suivre toutes les redirections profondément)
    # Pour une analyse de redirection plus poussée, il faudrait gérer les boucles, max_redirects, etc.
    if parsed_url.scheme and parsed_url.netloc: # Only proceed if basic parsing was ok
        try:
            # Ajouter un user-agent pour éviter les blocages basiques
            headers = {'User-Agent': 'SXTOOLS PREMIUM URL Analyzer/1.0'}
            response = requests.head(url_string, allow_redirects=False, timeout=5, headers=headers)
            results += "\n--- Redirection Check (Initial Request) ---\n"
            results += f"Status Code: {response.status_code}\n"
            
            if 'Location' in response.headers:
                results += f"Redirects to: {response.headers['Location']}\n"
                # On pourrait ici analyser la nouvelle 'Location' si on le souhaitait
                # Par exemple, comparer le domaine de la redirection avec le domaine original.
                redirect_parsed = urlparse(response.headers['Location'])
                if parsed_url.netloc.lower() != redirect_parsed.netloc.lower() and redirect_parsed.netloc:
                    results += "  WARNING: Redirects to a different domain!\n"
                app_logger.info(f"URL {url_string} redirects to {response.headers['Location']}")

            else:
                results += "No immediate redirection detected (based on 'Location' header).\n"
                app_logger.info(f"No immediate redirection for {url_string}")

        except requests.exceptions.SSLError as e:
            results += f"\n--- Redirection Check ---\nSSL Error: {e}\n"
            app_logger.warning(f"SSL Error for {url_string}: {e}")
        except requests.exceptions.ConnectionError:
            results += "\n--- Redirection Check ---\nConnection Error: Could not connect to the server.\n"
            app_logger.warning(f"Connection Error for {url_string}")
        except requests.exceptions.Timeout:
            results += "\n--- Redirection Check ---\nTimeout: The request timed out.\n"
            app_logger.warning(f"Timeout for {url_string}")
        except requests.exceptions.RequestException as e:
            results += f"\n--- Redirection Check ---\nRequest Error: {e}\n"
            app_logger.error(f"Request error for {url_string}: {e}")
    else:
        results += "\n--- Redirection Check ---\nSkipped due to initial parsing issues.\n"


    # Autres analyses possibles:
    # - Réputation de l'URL (nécessiterait des sources externes/API, donc hors scope)
    # - Vérification de la présence dans des listes de phishing (idem)
    # - Longueur de l'URL, présence de caractères suspects, etc.

    app_logger.info(f"URL analysis complete for: {url_string}")
    return results

if __name__ == '__main__':
    test_url_valid = "https://www.google.com/search?q=mxtools"
    test_url_redirect = "http://google.com" # Redirige vers https://www.google.com
    test_url_invalid_syntax = "htp:/badurl"
    test_url_nonexistent = "http://thissitedoesnotexist12345abc.com"

    print(analyze_url(test_url_valid))
    print("\n" + "="*20 + "\n")
    print(analyze_url(test_url_redirect))
    print("\n" + "="*20 + "\n")
    print(analyze_url(test_url_invalid_syntax))
    print("\n" + "="*20 + "\n")
    print(analyze_url(test_url_nonexistent))
    print("\n" + "="*20 + "\n")
    print(analyze_url(""))