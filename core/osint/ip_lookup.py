import requests
import json
from utils.logger import app_logger

def lookup_ip(ip_address):
    """
    Looks up IP information using ip-api.com (no API key needed for free tier).
    """
    app_logger.info(f"Performing IP lookup for: {ip_address}")
    if not ip_address:
        return "Error: IP address cannot be empty."
    try:
        # Utiliser ip-api.com qui est généralement plus permissif sans clé
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
        data = response.json()

        if data.get("status") == "success":
            output = f"IP Lookup Results for: {data.get('query', ip_address)}\n"
            output += "----------------------------------------\n"
            fields = ['country', 'countryCode', 'regionName', 'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as']
            for field in fields:
                if data.get(field):
                    output += f"{field.replace('as', 'ASN').capitalize()}: {data.get(field)}\n"
            app_logger.info(f"IP lookup successful for {ip_address}")
            return output
        else:
            app_logger.warning(f"IP lookup failed for {ip_address}: {data.get('message', 'Unknown error')}")
            return f"Error: Could not retrieve information for {ip_address}. Message: {data.get('message', 'Unknown error from API')}"

    except requests.exceptions.RequestException as e:
        app_logger.error(f"IP lookup request failed for {ip_address}: {e}")
        return f"Error: Request failed - {e}"
    except json.JSONDecodeError:
        app_logger.error(f"Failed to decode JSON response for IP lookup of {ip_address}")
        return f"Error: Invalid response from server for {ip_address}."
    except Exception as e:
        app_logger.error(f"An unexpected error occurred during IP lookup for {ip_address}: {e}", exc_info=True)
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    # Test
    test_ip = "8.8.8.8"
    print(lookup_ip(test_ip))
    test_ip_fail = "invalid"
    print(lookup_ip(test_ip_fail))