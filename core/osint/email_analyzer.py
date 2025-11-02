import re
import hashlib
import requests
from utils.logger import app_logger

def is_valid_email_format(email):
    """Vérifie le format de base d'un email."""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.fullmatch(regex, email))

def get_gravatar_url(email):
    """Tente de récupérer l'URL Gravatar si publique."""
    email_lower = email.lower().strip()
    hash_obj = hashlib.md5(email_lower.encode('utf-8')).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{hash_obj}?d=404" # d=404 renvoie 404 si pas d'avatar

    try:
        response = requests.head(gravatar_url, timeout=5, allow_redirects=True) # HEAD pour ne pas dl l'image
        if response.status_code == 200:
            # Check content type to be sure it's an image and not a redirect to a placeholder service
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type:
                 # Construct the URL that would typically be used to display the image
                return f"https://www.gravatar.com/avatar/{hash_obj}"
            else: # It might be a gravatar redirect to a placeholder or non-image
                return "Gravatar exists but might be a placeholder or redirect."
        elif response.status_code == 404:
            return "No public Gravatar found (404)."
        else:
            return f"Gravatar check: Status {response.status_code}"
    except requests.exceptions.RequestException as e:
        app_logger.warning(f"Gravatar check failed for {email}: {e}")
        return f"Gravatar check failed: {e}"


def analyze_email(email):
    app_logger.info(f"Analyzing email: {email}")
    if not email:
        return "Error: Email address cannot be empty."

    results = f"Email Analysis for: {email}\n"
    results += "----------------------------------------\n"

    # 1. Format Validation
    is_valid = is_valid_email_format(email)
    results += f"Format Valid: {'Yes' if is_valid else 'No'}\n"
    if not is_valid:
        app_logger.warning(f"Invalid email format for: {email}")
        return results + "\nAnalysis stopped due to invalid format."

    # 2. Public Gravatar
    gravatar_info = get_gravatar_url(email)
    results += f"Gravatar: {gravatar_info}\n"

    # 3. Syntactic Analysis (Domain part, username part)
    try:
        username, domain = email.split('@', 1)
        results += f"Username Part: {username}\n"
        results += f"Domain Part: {domain}\n"
        # On pourrait ajouter des vérifications DNS sur le domaine ici (MX records)
        # mais ça relève plus du module DNS lookup.
    except ValueError:
        results += "Could not split email into username/domain (should have been caught by format validation).\n"

    app_logger.info(f"Email analysis complete for: {email}")
    return results

if __name__ == '__main__':
    test_email_valid = "test@example.com"
    test_email_gravatar = "beau@wordpress.com" # Un email avec un Gravatar connu
    test_email_invalid = "testexample.com"

    print(analyze_email(test_email_valid))
    print("\n" + "="*20 + "\n")
    print(analyze_email(test_email_gravatar))
    print("\n" + "="*20 + "\n")
    print(analyze_email(test_email_invalid))