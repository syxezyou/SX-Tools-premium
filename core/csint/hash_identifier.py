import hashlib
import re
from utils.logger import app_logger

# Regex pour identifier les types de hash communs (basé sur la longueur et les caractères)
# C'est une heuristique, pas infaillible. Une librairie dédiée serait plus robuste.
HASH_REGEX = {
    "MD5": r"^[a-f0-9]{32}$",
    "SHA1": r"^[a-f0-9]{40}$",
    "SHA224": r"^[a-f0-9]{56}$",
    "SHA256": r"^[a-f0-9]{64}$",
    "SHA384": r"^[a-f0-9]{96}$",
    "SHA512": r"^[a-f0-9]{128}$",
    # D'autres pourraient être ajoutés (ex: NTLM, etc.)
}

def generate_hash(text, hash_type="sha256"):
    app_logger.info(f"Generating {hash_type} hash for input text.")
    try:
        h = hashlib.new(hash_type)
        h.update(text.encode('utf-8'))
        return h.hexdigest()
    except ValueError:
        app_logger.error(f"Unsupported hash type for generation: {hash_type}")
        return f"Error: Unsupported hash type '{hash_type}' for generation."
    except Exception as e:
        app_logger.error(f"Error generating hash: {e}", exc_info=True)
        return f"Error generating hash: {e}"

def identify_hash_type(hash_string):
    app_logger.info(f"Attempting to identify hash type for: {hash_string[:20]}...") # Log tronqué
    if not hash_string:
        return "Error: Hash string cannot be empty."
        
    hash_string_lower = hash_string.lower().strip()
    possible_types = []
    for hash_name, pattern in HASH_REGEX.items():
        if re.fullmatch(pattern, hash_string_lower):
            possible_types.append(hash_name)

    if possible_types:
        app_logger.info(f"Identified hash '{hash_string[:20]}...' as potentially: {', '.join(possible_types)}")
        return f"Input: {hash_string}\nPotential Type(s): {', '.join(possible_types)}"
    else:
        app_logger.info(f"Could not identify hash type for '{hash_string[:20]}...' based on common patterns.")
        return f"Input: {hash_string}\nCould not identify hash type based on common patterns (length/chars)."

if __name__ == '__main__':
    text_to_hash = "mxtools_test_string"
    
    print("--- Hash Generation ---")
    md5_hash = generate_hash(text_to_hash, "md5")
    print(f"MD5({text_to_hash}): {md5_hash}")
    sha256_hash = generate_hash(text_to_hash, "sha256")
    print(f"SHA256({text_to_hash}): {sha256_hash}")

    print("\n--- Hash Identification ---")
    print(identify_hash_type(md5_hash))
    print(identify_hash_type(sha256_hash))
    print(identify_hash_type("thisisnotavalidhash"))
    print(identify_hash_type("0123456789abcdef0123456789abcdef0123")) # SHA1 example