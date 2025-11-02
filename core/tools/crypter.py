# SXTOOLS PREMIUM/core/tools/crypter.py
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib # Pour dériver une clé si l'utilisateur ne veut pas de sel
from utils.logger import app_logger

SALT_SIZE = 16
KEY_SIZE = 32  # AES-256

def generate_salt():
    return get_random_bytes(SALT_SIZE)

def derive_key(password, salt, use_salt=True):
    """Dérive une clé à partir d'un mot de passe et d'un sel (optionnel)."""
    if use_salt:
        # PBKDF2 est une bonne fonction de dérivation de clé
        key = PBKDF2(password.encode('utf-8'), salt, dkLen=KEY_SIZE, count=1000000)
    else:
        # Moins sécurisé, mais une option si aucun sel n'est utilisé.
        # Utilise SHA-256 du mot de passe directement comme clé.
        # Ce n'est PAS recommandé pour une haute sécurité sans sel.
        key = hashlib.sha256(password.encode('utf-8')).digest()
        # S'assurer que la clé a la bonne taille (32 bytes pour AES-256)
        # Si la clé dérivée est plus courte, elle sera paddée ou tronquée.
        # Ici, sha256 produit 32 bytes, donc c'est bon.
    return key

def encrypt_text(plain_text, password, use_salt=True):
    app_logger.info(f"Attempting to encrypt text (use_salt: {use_salt})")
    try:
        salt = generate_salt() if use_salt else b'' # Sel vide si non utilisé
        key = derive_key(password, salt, use_salt)
        
        cipher = AES.new(key, AES.MODE_CBC) # Utilisation du mode CBC
        plain_text_bytes = plain_text.encode('utf-8')
        padded_text = pad(plain_text_bytes, AES.block_size)
        cipher_text_bytes = cipher.encrypt(padded_text)
        
        # Concaténer le sel (si utilisé) et l'IV avec le texte chiffré
        # IV est généré par AES.new en mode CBC et est disponible via cipher.iv
        iv = cipher.iv
        
        # Encoder en Base64 pour la lisibilité et le stockage
        if use_salt:
            # Format: salt + iv + ciphertext
            encrypted_data = salt + iv + cipher_text_bytes
        else:
            # Format: iv + ciphertext
            encrypted_data = iv + cipher_text_bytes
            
        encrypted_text_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        app_logger.info("Text encryption successful.")
        return encrypted_text_b64
    except Exception as e:
        app_logger.error(f"Encryption failed: {e}", exc_info=True)
        return f"Encryption Error: {e}"

def decrypt_text(cipher_text_b64, password, use_salt=True):
    app_logger.info(f"Attempting to decrypt text (use_salt: {use_salt})")
    try:
        encrypted_data = base64.b64decode(cipher_text_b64.encode('utf-8'))
        
        salt = b''
        iv_offset = 0 # Où commence l'IV dans encrypted_data

        if use_salt:
            if len(encrypted_data) < SALT_SIZE + AES.block_size: # Sel + taille IV minimum
                raise ValueError("Ciphertext is too short to contain salt and IV.")
            salt = encrypted_data[:SALT_SIZE]
            iv_offset = SALT_SIZE
        else: # Pas de sel
            if len(encrypted_data) < AES.block_size: # Taille IV minimum
                raise ValueError("Ciphertext is too short to contain IV.")
        
        key = derive_key(password, salt, use_salt)
        
        iv = encrypted_data[iv_offset : iv_offset + AES.block_size]
        cipher_text_bytes = encrypted_data[iv_offset + AES.block_size:]
        
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        decrypted_padded_bytes = cipher.decrypt(cipher_text_bytes)
        
        try:
            decrypted_bytes = unpad(decrypted_padded_bytes, AES.block_size)
        except ValueError as e:
            # Souvent une erreur de padding indique un mauvais mot de passe ou des données corrompues
            app_logger.error(f"Unpadding failed, likely incorrect password or corrupted data: {e}")
            return "Decryption Error: Unpadding failed. Likely incorrect password or data corruption."

        decrypted_text = decrypted_bytes.decode('utf-8')
        
        app_logger.info("Text decryption successful.")
        return decrypted_text
    except ValueError as ve: # Attraper les erreurs de base64 ou de longueur
        app_logger.error(f"Decryption failed (ValueError): {ve}", exc_info=True)
        return f"Decryption Error: {ve}. Check input format or if 'Use Salt' matches encryption."
    except Exception as e:
        app_logger.error(f"Decryption failed: {e}", exc_info=True)
        return f"Decryption Error: {e}. Ensure the password is correct and 'Use Salt' setting matches the encryption method."

if __name__ == '__main__':
    password_test = "mysecretpassword"
    text_to_encrypt = "This is a super secret message!"

    print("--- Test with Salt ---")
    encrypted_with_salt = encrypt_text(text_to_encrypt, password_test, use_salt=True)
    print(f"Encrypted (salt): {encrypted_with_salt}")
    decrypted_with_salt = decrypt_text(encrypted_with_salt, password_test, use_salt=True)
    print(f"Decrypted (salt): {decrypted_with_salt}")
    assert decrypted_with_salt == text_to_encrypt

    print("\n--- Test without Salt ---")
    encrypted_no_salt = encrypt_text(text_to_encrypt, password_test, use_salt=False)
    print(f"Encrypted (no salt): {encrypted_no_salt}")
    decrypted_no_salt = decrypt_text(encrypted_no_salt, password_test, use_salt=False)
    print(f"Decrypted (no salt): {decrypted_no_salt}")
    assert decrypted_no_salt == text_to_encrypt
    
    print("\n--- Test Decryption Failure (wrong password) ---")
    decrypted_fail = decrypt_text(encrypted_with_salt, "wrongpassword", use_salt=True)
    print(f"Decrypted (fail): {decrypted_fail}")

    print("\n--- Test Decryption Failure (mismatched salt option) ---")
    decrypted_fail_salt_option = decrypt_text(encrypted_with_salt, password_test, use_salt=False)
    print(f"Decrypted (fail salt): {decrypted_fail_salt_option}")