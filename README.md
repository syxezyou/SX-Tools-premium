# 🔥 SXTOOLS PREMIUM 🔥

**Une suite d'outils de bureau pour l'OSINT, le CSINT, la Sécurité et le Gaming.**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the_badge)
![Status](https://img.shields.io/badge/Status-En%20Développement-orange?style=for-the-badge)

---

## 🚀 À Propos du Projet

**SXTOOLS PREMIUM** est une application de bureau multi-fonctions conçue pour les passionnés de cybersécurité, les enquêteurs OSINT et les gamers. Elle rassemble une collection d'outils puissants dans une interface graphique moderne et facile à utiliser, construite avec CustomTkinter.
---

## ✨ Fonctionnalités Principales

L'application est organisée en plusieurs catégories logiques :

### 🕵️ OSINT (Renseignement en Sources Ouvertes)
- **Social Media Finder** : Trouve des profils sur les réseaux sociaux à partir d'un nom d'utilisateur.
- **IP Address Lookup** : Obtient des informations détaillées sur une adresse IP.
- **Email Analyzer** : Analyse la validité et le domaine d'une adresse e-mail.
- **Phone Number Lookup** : Récupère des informations sur un numéro de téléphone.
- **WHOIS & DNS Lookup** : Obtient les informations d'enregistrement et les enregistrements DNS d'un domaine.
- **Metadata Extractor** : Extrait les métadonnées EXIF des fichiers image et PDF.

### 🛡️ CSINT & Network
- **Port Scanner** : Scanne les ports ouverts sur une cible.
- **Subdomain Finder** : Découvre les sous-domaines d'un domaine à l'aide d'une wordlist.
- **Hash Identifier & Generator** : Identifie le type d'un hash et en génère de nouveaux.
- **URL Analyzer** : Analyse la structure d'une URL et détecte les redirections.
- **Suspicious Connection Monitor** : Détecte les activités réseau suspectes (potentielles attaques DoS) en comptant les connexions par IP.

### 🎮 Gaming
- **FPS Boost** : Optimise le système pour de meilleures performances en jeu (mode d'alimentation, nettoyage des fichiers temporaires).
- **Network Boost** : Réduit la latence en jeu en désactivant l'algorithme de Nagle et en vidant le cache DNS.

### 💬 Discord
- **User Lookup** : Obtient des informations publiques sur un utilisateur Discord via son ID.
- **Token Checker** : Vérifie la validité d'un token Discord.
- **Invite Info** : Affiche les informations d'un serveur à partir d'un code d'invitation.
- **Webhook Sender** : Envoie des messages via une URL de webhook.

### 🎭 ANO (Anonymat & Confidentialité)
- **System Anonymizer** : Change le nom d'hôte du PC et l'adresse MAC de l'interface réseau.
- **Trace Cleaner** : Efface de manière irréversible tous les journaux d'événements Windows.
- **Anti-Telemetry** : Désactive/réactive les services de collecte de données de Windows.

### 🛠️ Outils
- **Fake Identity Generator** : Crée une fausse identité complète pour des tests.
- **Text Encrypter/Decrypter** : Chiffre et déchiffre du texte avec un mot de passe (AES).

### ⚙️ Settings
- **Personnalisation** : Changez la couleur d'accentuation et le thème de l'application (Light/Dark/System).
- **Configuration** : Gérez votre token de bot Discord directement depuis l'interface.
- **Réinitialisation** : Restaurez tous les paramètres par défaut.

---

## ⚙️ Installation

Ce projet nécessite **Python 3.10** ou une version plus récente.

**1. Clonez le dépôt :**
```bash
git clone https://github.com/VOTRE_NOM_UTILISATEUR/VOTRE_REPO.git
cd VOTRE_REPO
```

**2. Installez les dépendances :**
Il est recommandé d'utiliser un environnement virtuel.
```bash
# Créez un environnement virtuel (optionnel mais recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installez les paquets requis
pip install -r requirements.txt
```
*(Assurez-vous d'avoir un fichier `requirements.txt` avec les dépendances comme `customtkinter`, `requests`, `psutil`, `Pillow`, `pycryptodome`, `faker`, `phonenumbers`)*

**3. Configuration Initiale :**
- **Token Discord** : Pour utiliser l'outil "Discord User Lookup", vous devez fournir un token de bot. Allez dans `Settings`, collez votre token dans le champ approprié et cliquez sur "Save Token".

**4. Lancez l'application :**

> **⚠️ IMPORTANT**
> Pour que les catégories **ANO** et **Gaming** fonctionnent, vous devez lancer l'application avec des **privilèges d'administrateur**.

Sur Windows, faites un clic droit sur le script `main.py` et sélectionnez "Exécuter en tant qu'administrateur".

```bash
python main.py
```

Pour lancer l'application sans la fenêtre de console en arrière-plan, utilisez `main.pyw`.

---

## 📜 Disclaimer

Les outils fournis dans **SXTOOLS PREMIUM** sont destinés à des fins **éducatives, éthiques et de recherche en sécurité uniquement**.

- L'utilisation de ces outils sur des systèmes ou des réseaux pour lesquels vous n'avez pas d'autorisation explicite est **illégale**.
- Les fonctionnalités de la catégorie "ANO" modifient en profondeur les paramètres du système. L'effacement des journaux d'événements est **irréversible**.
- L'auteur n'est pas responsable de toute utilisation abusive ou de tout dommage causé par ce programme. **Utilisez-le à vos propres risques.**

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Si vous avez des idées d'amélioration ou de nouvelles fonctionnalités, n'hésitez pas à ouvrir une *issue* ou à soumettre une *pull request*.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
