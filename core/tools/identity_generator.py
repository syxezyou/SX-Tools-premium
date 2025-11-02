# MXTools/core/tools/identity_generator.py
from faker import Faker
from utils.logger import app_logger
import random

# Initialiser Faker. On peut spécifier une locale si besoin, ex: Faker('fr_FR')
# Pour une identité plus "générique", on peut utiliser plusieurs locales ou laisser par défaut (en_US)
fake_en = Faker()
fake_fr = Faker('fr_FR')
# Tu peux ajouter d'autres locales pour plus de variété si tu veux
# fake_de = Faker('de_DE')
# fakers = [fake_en, fake_fr, fake_de]
fakers = [fake_en, fake_fr]


def generate_fake_identity(locale_choice="random"):
    """
    Génère une identité factice.
    locale_choice: 'random', 'en_US', 'fr_FR', etc.
    """
    app_logger.info(f"Generating fake identity with locale_choice: {locale_choice}")

    if locale_choice == "random":
        selected_faker = random.choice(fakers)
    elif locale_choice == "en_US":
        selected_faker = fake_en
    elif locale_choice == "fr_FR":
        selected_faker = fake_fr
    # elif locale_choice == "de_DE":
    #    selected_faker = fake_de
    else: # Par défaut ou si la locale n'est pas gérée explicitement ici
        selected_faker = fake_en 
        app_logger.warning(f"Locale {locale_choice} not explicitly handled, defaulting to en_US.")


    try:
        name = selected_faker.name()
        address = selected_faker.address().replace('\n', ', ')
        # Pour les numéros de téléphone, Faker peut générer des formats locaux.
        # Il est préférable de ne pas inclure de vrais formats de numéros pour éviter toute confusion.
        # On peut générer une chaîne aléatoire de chiffres ou un format plus générique.
        phone_number = selected_faker.numerify(text='(###) ###-####') # Format US
        if selected_faker.locale == 'fr_FR':
            phone_number = selected_faker.numerify(text='0#########')


        email_domain = selected_faker.free_email_domain()
        # Générer un username basé sur le nom, plus réaliste
        username_base = name.lower().replace(' ', '.').replace('-', '.')
        # Supprimer les titres comme M., Mme., Dr. etc. que Faker peut ajouter
        parts = username_base.split('.')
        if parts[0] in ['mr', 'ms', 'mrs', 'dr', 'prof']:
            username_base = '.'.join(parts[1:])
        username = f"{username_base}{selected_faker.numerify(text='##')}"
        email = f"{username}@{email_domain}"
        
        birthdate = selected_faker.date_of_birth(minimum_age=18, maximum_age=70).strftime('%Y-%m-%d')
        job = selected_faker.job()
        company = selected_faker.company()
        
        # Pour une "National ID" ou un "SSN", il faut être très prudent.
        # Il est préférable de générer une chaîne aléatoire sans format spécifique réel.
        national_id_placeholder = selected_faker.numerify(text='ID-#########')

        identity_details = [
            f"Name: {name}",
            f"Address: {address}",
            f"Phone: {phone_number}",
            f"Email: {email}",
            f"Username Suggestion: {username}",
            f"Birthdate: {birthdate}",
            f"Occupation: {job}",
            f"Company: {company}",
            f"User Agent: {selected_faker.user_agent()}",
            f"Credit Card (Dummy): {selected_faker.credit_card_full()}", # Génère un numéro, date, CVV factices
            f"National ID (Placeholder): {national_id_placeholder}"
        ]
        
        app_logger.info(f"Fake identity generated for locale {selected_faker.locales}")
        return "\n".join(identity_details)

    except Exception as e:
        app_logger.error(f"Error generating fake identity: {e}", exc_info=True)
        return f"Error generating identity: {e}"

if __name__ == '__main__':
    print("--- Random Locale Identity ---")
    print(generate_fake_identity())
    print("\n--- French Locale Identity ---")
    print(generate_fake_identity(locale_choice='fr_FR'))
    print("\n--- English (US) Locale Identity ---")
    print(generate_fake_identity(locale_choice='en_US'))