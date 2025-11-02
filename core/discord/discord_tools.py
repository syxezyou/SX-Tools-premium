# MXTools/core/discord/discord_tools.py
import requests
import json
from utils.logger import app_logger
from datetime import datetime

BASE_API_URL = "https://discord.com/api/v9"

def get_user_info(user_id: str, bot_token: str):
    """Récupère les informations publiques d'un utilisateur Discord via son ID."""
    app_logger.info(f"Fetching Discord user info for ID: {user_id}")
    if not user_id.isdigit():
        return "Error: Invalid Discord User ID. It should be a sequence of numbers."
    
    if not bot_token:
        return "Error: Discord Bot Token is not configured. Please add it in mxtools_config.json."

    headers = {'Authorization': f'Bot {bot_token}'}
    try:
        response = requests.get(f"{BASE_API_URL}/users/{user_id}", headers=headers)
        response.raise_for_status()
        user_data = response.json()

        # Calcul de la date de création du compte à partir de l'ID
        creation_timestamp = ((int(user_id) >> 22) + 1420070400000) / 1000
        creation_date = datetime.utcfromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

        result = f"--- Discord User Info for {user_data.get('username')}#{user_data.get('discriminator')} ---\n"
        result += f"ID: {user_data.get('id')}\n"
        result += f"Username: {user_data.get('username')}\n"
        result += f"Discriminator: {user_data.get('discriminator')}\n"
        result += f"Global Name: {user_data.get('global_name', 'N/A')}\n"
        result += f"Account Created: {creation_date}\n"
        result += f"Is Bot: {'Yes' if user_data.get('bot') else 'No'}\n"
        
        avatar_hash = user_data.get('avatar')
        if avatar_hash:
            result += f"Avatar URL: https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png\n"
        
        banner_hash = user_data.get('banner')
        if banner_hash:
            result += f"Banner URL: https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.png\n"

        return result

    except requests.exceptions.HTTPError as e:
        app_logger.error(f"HTTP Error fetching user info for {user_id}: {e}")
        if e.response.status_code == 404:
            return "Error: User not found."
        return f"Error: An HTTP error occurred ({e.response.status_code}). Check if your bot token is valid and has permissions."
    except Exception as e:
        app_logger.error(f"Error fetching user info for {user_id}: {e}")
        return f"An unexpected error occurred: {e}"

def check_token(token: str):
    """Vérifie un token Discord et affiche les informations du compte associé."""
    app_logger.info(f"Checking Discord token.")
    if not token:
        return "Error: Token cannot be empty."

    headers = {'Authorization': token}
    try:
        response = requests.get(f"{BASE_API_URL}/users/@me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            result = "--- Valid Discord Token Info ---\n"
            result += f"ID: {user_data.get('id')}\n"
            result += f"Username: {user_data.get('username')}#{user_data.get('discriminator')}\n"
            result += f"Email: {user_data.get('email', 'N/A')}\n"
            result += f"Phone: {user_data.get('phone', 'N/A')}\n"
            result += f"MFA Enabled: {'Yes' if user_data.get('mfa_enabled') else 'No'}\n"
            result += f"Verified: {'Yes' if user_data.get('verified') else 'No'}\n"
            return result
        else:
            return "--- Invalid or Expired Token ---\n"

    except Exception as e:
        app_logger.error(f"Error checking token: {e}")
        return f"An unexpected error occurred: {e}"

def send_webhook_message(webhook_url: str, message: str, username: str = "SXTOOLS PREMIUM Webhook"):
    """Envoie un message via un webhook Discord."""
    app_logger.info(f"Sending message to webhook.")
    if not webhook_url or not message:
        return "Error: Webhook URL and message cannot be empty."

    payload = {
        "content": message,
        "username": username
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return "Webhook message sent successfully!"
    except requests.exceptions.MissingSchema:
        return "Error: Invalid Webhook URL. It should start with 'http://' or 'https://'."
    except requests.exceptions.HTTPError as e:
        app_logger.error(f"HTTP Error sending webhook: {e}")
        return f"Error sending webhook (HTTP {e.response.status_code}): {e.response.text}"
    except Exception as e:
        app_logger.error(f"Error sending webhook: {e}")
        return f"An unexpected error occurred: {e}"

def get_invite_info(invite_code: str):
    """Récupère les informations d'une invitation Discord."""
    app_logger.info(f"Fetching info for invite code: {invite_code}")
    if not invite_code:
        return "Error: Invite code cannot be empty."

    try:
        response = requests.get(f"{BASE_API_URL}/invites/{invite_code}?with_counts=true")
        response.raise_for_status()
        data = response.json()
        guild = data.get('guild', {})
        result = f"--- Invite Info for '{guild.get('name')}' ---\n"
        result += f"Server ID: {guild.get('id')}\n"
        result += f"Server Name: {guild.get('name')}\n"
        result += f"Description: {guild.get('description', 'N/A')}\n"
        result += f"Members: {data.get('approximate_member_count', 'N/A')}\n"
        result += f"Online: {data.get('approximate_presence_count', 'N/A')}\n"
        result += f"Verification Level: {guild.get('verification_level')}\n"
        return result
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return "Error: Invalid or expired invite code."
        return f"Error fetching invite info (HTTP {e.response.status_code})."
    except Exception as e:
        app_logger.error(f"Error fetching invite info: {e}")
        return f"An unexpected error occurred: {e}"