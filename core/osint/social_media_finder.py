# MXTools/core/osint/social_media_finder.py
import requests
import threading
from queue import Queue
from utils.logger import app_logger

NUM_THREADS_SOCIAL = 10
social_q = Queue()

# Dictionnaire des sites et de leurs URLs de profil. Le {} sera remplacé par le nom d'utilisateur.
# On vérifie aussi le code de statut attendu si le profil n'existe pas (la plupart sont 404).
SOCIAL_MEDIA_SITES = {
    "Instagram": ("https://www.instagram.com/{}", 404),
    "Twitter / X": ("https://twitter.com/{}", 404),
    "GitHub": ("https://github.com/{}", 404),
    "Reddit": ("https://www.reddit.com/user/{}", 404),
    "Pinterest": ("https://www.pinterest.com/{}", 404),
    "TikTok": ("https://www.tiktok.com/@{}", 404),
    "Steam": ("https://steamcommunity.com/id/{}", 200), # Steam redirige, donc on vérifie si la page contient "The specified profile could not be found."
    "Twitch": ("https://www.twitch.tv/{}", 404),
    "YouTube": ("https://www.youtube.com/@{}", 404),
    "Vimeo": ("https://vimeo.com/{}", 404),
    "GitLab": ("https://gitlab.com/{}", 404),
}

def check_profile(site_name, url_template, not_found_status, username, found_profiles_list):
    """Vérifie l'existence d'un profil sur un site donné."""
    url = url_template.format(username)
    try:
        headers = {'User-Agent': 'SXTOOLS PREMIUM Social Finder/1.0'}
        response = requests.get(url, timeout=5, allow_redirects=True, headers=headers)

        # Logique de détection spécifique
        found = False
        if site_name == "Steam":
            if response.status_code == 200 and "The specified profile could not be found." not in response.text:
                found = True
        elif response.status_code != not_found_status and response.status_code < 400:
            found = True

        if found:
            app_logger.info(f"Found profile for '{username}' on {site_name}: {url}")
            found_profiles_list.append(f"[{site_name}] {url}")

    except requests.exceptions.Timeout:
        app_logger.warning(f"Timeout checking {url}")
    except requests.exceptions.RequestException as e:
        app_logger.debug(f"Request exception for {url}: {e}")

def social_worker(username, found_profiles_list):
    """Worker thread pour traiter la file d'attente des sites."""
    while not social_q.empty():
        site_name, (url_template, not_found_status) = social_q.get()
        check_profile(site_name, url_template, not_found_status, username, found_profiles_list)
        social_q.task_done()

def find_profiles(username):
    """
    Recherche des profils sur les réseaux sociaux pour un nom d'utilisateur donné.
    """
    app_logger.info(f"Starting social media profile search for username: {username}")
    if not username:
        return "Error: Username cannot be empty."

    # Remplir la queue avec les sites à vérifier
    for site, data in SOCIAL_MEDIA_SITES.items():
        social_q.put((site, data))

    found_profiles = []
    threads = []
    for _ in range(min(NUM_THREADS_SOCIAL, len(SOCIAL_MEDIA_SITES))):
        t = threading.Thread(target=social_worker, args=(username, found_profiles), daemon=True)
        threads.append(t)
        t.start()

    social_q.join() # Attendre que tous les threads aient fini

    result_str = f"Social Media Profiles for '{username}':\n"
    result_str += "----------------------------------------\n"
    if found_profiles:
        result_str += "\n".join(sorted(found_profiles))
    else:
        result_str += "No profiles found for this username on the checked sites."
    
    app_logger.info(f"Social media profile search finished for '{username}'.")
    return result_str