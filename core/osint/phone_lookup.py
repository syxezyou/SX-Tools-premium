# MXTools/core/osint/phone_lookup.py
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from utils.logger import app_logger

def format_phone_number_info(phone_number_str, country_code_hint=None):
    """
    Analyzes a phone number using the phonenumbers library.
    country_code_hint: Optional e.g., "FR" for France, "US" for USA.
                       Helps parse numbers without an explicit country code.
    """
    app_logger.info(f"Analyzing phone number: {phone_number_str} (Hint: {country_code_hint})")
    if not phone_number_str:
        return "Error: Phone number cannot be empty."

    try:
        # Parse the number. If no country code is provided in the number itself,
        # the library might need a hint.
        parsed_number = phonenumbers.parse(phone_number_str, country_code_hint)
        
        results = f"Phone Number Analysis for: {phone_number_str}\n"
        results += "----------------------------------------\n"

        if not phonenumbers.is_valid_number(parsed_number):
            results += "Status: Invalid phone number format or number.\n"
            if country_code_hint:
                 results += f"(Tried with country hint: {country_code_hint})\n"
            else:
                 results += "(No country hint provided. Try adding one like 'US' or 'FR' if it's a local number without a country code.)\n"

            # Try to get some info even if not fully valid (e.g., country code)
            if parsed_number.country_code:
                results += f"Detected Country Code: +{parsed_number.country_code}\n"
            if parsed_number.national_number:
                results += f"National Number: {parsed_number.national_number}\n"
            app_logger.warning(f"Invalid phone number: {phone_number_str}")
            return results

        results += "Status: Valid phone number\n"
        results += f"International Format: {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}\n"
        results += f"National Format: {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)}\n"
        results += f"E.164 Format: {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)}\n"
        
        country = geocoder.description_for_number(parsed_number, "en")
        results += f"Country: {country}\n"

        # Carrier information (might not always be available or accurate)
        # Requires `phonenumbers[carrier]` which often means installing `phonenumbers` with extras
        # or it might be bundled.
        try:
            service_provider = carrier.name_for_number(parsed_number, "en")
            if service_provider:
                results += f"Carrier: {service_provider}\n"
            else:
                results += "Carrier: Information not available\n"
        except Exception as e:
            results += f"Carrier: Could not retrieve carrier info ({e})\n"
            app_logger.debug(f"Could not retrieve carrier for {phone_number_str}: {e}")

        # Time zone information
        try:
            time_zones = timezone.time_zones_for_number(parsed_number)
            if time_zones:
                results += f"Time Zone(s): {', '.join(time_zones)}\n"
            else:
                results += "Time Zone(s): Information not available\n"
        except Exception as e:
            results += f"Time Zone(s): Could not retrieve timezone info ({e})\n"
            app_logger.debug(f"Could not retrieve timezone for {phone_number_str}: {e}")


        app_logger.info(f"Phone number analysis complete for: {phone_number_str}")
        return results

    except phonenumbers.NumberParseException as e:
        app_logger.error(f"Failed to parse phone number '{phone_number_str}': {e}")
        return f"Error: Could not parse phone number '{phone_number_str}'. Invalid format. {e}"
    except Exception as e:
        app_logger.error(f"Unexpected error analyzing phone number {phone_number_str}: {e}", exc_info=True)
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    # Test cases
    print(format_phone_number_info("+14155552671")) # Valid US number
    print("\n" + "="*20 + "\n")
    print(format_phone_number_info("+442079460958")) # Valid UK number
    print("\n" + "="*20 + "\n")
    print(format_phone_number_info("0612345678", "FR")) # French number without +33, needs hint
    print("\n" + "="*20 + "\n")
    print(format_phone_number_info("12345")) # Invalid
    print("\n" + "="*20 + "\n")
    print(format_phone_number_info("")) # Empty