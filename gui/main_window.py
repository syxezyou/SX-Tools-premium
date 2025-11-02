# SXTOOLS PREMIUM/gui/main_window.py
import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image # Importer Image de Pillow
import os
import webbrowser
import threading

# Importer les modules core
from core.osint import ip_lookup, email_analyzer, phone_lookup, whois_dns, metadata_extractor, social_media_finder
from core.csint import port_scanner, subdomain_finder, hash_identifier, url_analyzer
from core.tools import identity_generator, crypter
from core.csint import connection_monitor # Ajout de l'import
from core.ano import anonymizer
from core.discord import discord_tools
from core.gaming import performance_booster

from utils.logger import app_logger
from utils.exporter import Exporter
from utils.config_manager import save_config, load_config, DEFAULT_CONFIG

class MainWindow(ctk.CTk):
    def __init__(self, config):
        super().__init__()

        self.config = config
        self.title("SXTOOLS PREMIUM - OSINT/CSINT Suite")
        self.geometry("1100x750")

        # Couleurs de base
        self.main_bg_color = "#1a1a1a"
        self.second_bg_color = "#0d0d0d"
        self.text_color = "#e0e0e0"
        
        # Initialisation des attributs de couleur et de thème
        self.accent_color = self.config.get("accent_color", DEFAULT_CONFIG["accent_color"])
        self.button_hover_color = self._calculate_hover_color(self.accent_color) 
        self.nav_button_active_fg_color = self.accent_color
        self.nav_button_active_text_color = self.second_bg_color
        self.nav_button_inactive_fg_color = "transparent"
        self.nav_button_inactive_text_color = self.text_color

        self.configure(fg_color=self.main_bg_color)

        self.current_category_button = None 
        self.nav_buttons = {} 
        self.category_frames = {}
        self.themed_buttons = [] 
        self.themed_entries_textboxes = [] 
        self.themed_option_menus = []
        self.themed_checkboxes = []
        self.themed_title_labels = [] 

        self._create_ui_structure() 
        self._create_module_widgets()
        self.logger = app_logger
        self.apply_accent_color_to_ui() 
        self.show_category_frame("OSINT")

    def _load_images(self):
        self.discord_logo = ctk.CTkImage(Image.open(os.path.join("assets", "discord_logo.png")), size=(24, 24))

    def _create_ui_structure(self):
        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color=self.second_bg_color, corner_radius=0, height=75) # Hauteur ajustée
        self.header_frame.pack(fill="x", pady=(0,2), side="top")
        self.header_frame.pack_propagate(False)

        logo_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        logo_container.pack(side="left", padx=20, pady=5, anchor="w")

        self.logo_label = ctk.CTkLabel(logo_container, text="SXTOOLS PREMIUM", font=("Consolas", 30, "bold")) # Couleur via thème
        self.logo_label.pack(pady=(0,0)) 

        # --- Bouton d'aide ---
        self.help_button = ctk.CTkButton(self.header_frame, text="❔ Help", font=("Segoe UI", 13, "bold"),
                                         width=80, command=self.show_help_popup)
        self.help_button.pack(side="right", padx=20, pady=10, anchor="e")

        self.subtitle_label = ctk.CTkLabel(logo_container, text="By Silencieux", font=("Consolas", 10, "italic"), text_color=self.text_color) 
        self.subtitle_label.pack(pady=(0,0), anchor="nw")

        # --- Main Container ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent") 
        self.main_container.pack(fill="both", expand=True, padx=5, pady=(0,5))

        # --- Panneau de Navigation ---
        self.navigation_frame = ctk.CTkFrame(self.main_container, width=200, fg_color=self.second_bg_color, corner_radius=8)
        self.navigation_frame.pack(side="left", fill="y", padx=(0, 5), pady=0)
        self.navigation_frame.pack_propagate(False)

        # --- Zone de Contenu ---
        self.content_area_frame = ctk.CTkFrame(self.main_container, fg_color="transparent") 
        self.content_area_frame.pack(side="left", fill="both", expand=True)
        
        self._load_images()

        self.categories = {
            "OSINT": {"text": "🕵️ OSINT", "image": None},
            "CSINT": {"text": "🛡️ CSINT", "image": None},
            "Network": {"text": "🌐 Network", "image": None},
            "Tools": {"text": "🛠️ Tools", "image": None},
            "Gaming": {"text": "🎮 Gaming", "image": None},
            "Discord": {"text": " Discord", "image": self.discord_logo},
            "ANO": {"text": "🎭 ANO", "image": None},
            "Settings": {"text": "⚙️ Settings", "image": None}
        }

        for cat_key, cat_data in self.categories.items():
            frame = ctk.CTkFrame(self.content_area_frame, fg_color="transparent", corner_radius=0)
            self.category_frames[cat_key] = frame 
            
            button = ctk.CTkButton(self.navigation_frame, text=cat_data["text"],
                                   image=cat_data["image"],
                                   command=lambda k=cat_key: self.show_category_frame(k),
                                   font=("Segoe UI", 14, "bold"), anchor="w", height=40, corner_radius=6,
                                   compound="left") # Affiche l'image à gauche du texte
            button.pack(fill="x", pady=6, padx=10)
            self.nav_buttons[cat_key] = button

    def _create_module_widgets(self):
        """Crée les widgets pour chaque module dans leur frame respective."""
        self.create_osint_widgets(self.category_frames["OSINT"])
        self.create_csint_widgets(self.category_frames["CSINT"])
        self.create_network_widgets(self.category_frames["Network"])
        self.create_tools_widgets(self.category_frames["Tools"])
        self.create_gaming_widgets(self.category_frames["Gaming"])
        self.create_discord_widgets(self.category_frames["Discord"])
        self.create_ano_widgets(self.category_frames["ANO"])
        self.create_settings_widgets(self.category_frames["Settings"])

    # =================================================================================
    # WIDGET CREATION - OSINT
    # =================================================================================
    def create_osint_widgets(self, parent_frame):
        main_scroll_frame = self.create_main_scrollable_frame(parent_frame)

        # --- Social Media Profile Finder ---
        social_frame, social_entry, social_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="Social Media Profile Finder",
            entry_placeholder="Enter username (e.g., 'johnsmith')",
            button_text="Find Profiles",
            button_command=lambda: self.run_in_thread(social_media_finder.find_profiles, social_entry.get(), social_results)
        )
        social_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- IP Lookup ---
        ip_frame, ip_entry, ip_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="IP Address Lookup",
            entry_placeholder="Enter IP Address (e.g., 8.8.8.8)",
            button_text="Lookup IP",
            button_command=lambda: self.run_in_thread(ip_lookup.lookup_ip, ip_entry.get(), ip_results)
        )
        ip_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- Email Analyzer ---
        email_frame, email_entry, email_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="Email Address Analyzer",
            entry_placeholder="Enter Email Address",
            button_text="Analyze Email",
            button_command=lambda: self.run_in_thread(email_analyzer.analyze_email, email_entry.get(), email_results)
        )
        email_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- Phone Number Lookup ---
        phone_frame = self.create_themed_frame(main_scroll_frame)
        phone_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(phone_frame, "Phone Number Lookup").pack(anchor="w", padx=10, pady=(5, 5))
        
        phone_input_frame = ctk.CTkFrame(phone_frame, fg_color="transparent")
        phone_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        phone_entry = self.create_themed_entry(phone_input_frame, placeholder_text="Enter Phone Number (e.g., +14155552671)")
        phone_entry.pack(side="left", fill="x", expand=True, ipady=4)
        
        phone_country_hint = self.create_themed_entry(phone_input_frame, placeholder_text="Hint (e.g., FR)", width=100)
        phone_country_hint.pack(side="left", padx=(5, 5))

        phone_results = self.create_themed_textbox(phone_frame)
        phone_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        phone_button = self.create_themed_button(
            phone_frame, "Lookup Phone",
            lambda: self.run_in_thread(phone_lookup.format_phone_number_info, phone_entry.get(), phone_results, phone_country_hint.get())
        )
        phone_button.pack(fill="x", padx=10, pady=(0, 10))

        # --- WHOIS & DNS ---
        whois_dns_frame, whois_dns_entry, whois_dns_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="WHOIS & DNS Lookup",
            entry_placeholder="Enter Domain or IP",
            button_text="Run WHOIS",
            button_command=lambda: self.run_in_thread(whois_dns.get_whois_info, whois_dns_entry.get(), whois_dns_results),
            second_button_text="Run DNS Lookup",
            second_button_command=lambda: self.run_in_thread(whois_dns.get_dns_records, whois_dns_entry.get(), whois_dns_results)
        )
        whois_dns_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- Metadata Extractor ---
        meta_frame = self.create_themed_frame(main_scroll_frame)
        meta_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(meta_frame, "File Metadata Extractor").pack(anchor="w", padx=10, pady=(5, 5))
        
        meta_results = self.create_themed_textbox(meta_frame)
        meta_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def select_file_and_extract():
            filepath = filedialog.askopenfilename()
            if filepath:
                self.run_in_thread(metadata_extractor.extract_metadata_from_file, filepath, meta_results)

        meta_button = self.create_themed_button(meta_frame, "Select File and Extract Metadata", select_file_and_extract)
        meta_button.pack(fill="x", padx=10, pady=(0, 10))

    # =================================================================================
    # WIDGET CREATION - CSINT & NETWORK
    # =================================================================================
    def create_csint_widgets(self, parent_frame):
        main_scroll_frame = self.create_main_scrollable_frame(parent_frame)

        # --- Hash Identifier ---
        hash_frame, hash_entry, hash_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="Hash Identifier & Generator",
            entry_placeholder="Enter hash or text to hash",
            button_text="Identify Hash",
            button_command=lambda: self.run_in_thread(hash_identifier.identify_hash_type, hash_entry.get(), hash_results),
            second_button_text="Generate Hashes",
            second_button_command=lambda: self.run_in_thread(hash_identifier.generate_hashes, hash_entry.get(), hash_results)
        )
        hash_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- URL Analyzer ---
        url_frame, url_entry, url_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="URL Analyzer",
            entry_placeholder="Enter full URL (e.g., https://example.com)",
            button_text="Analyze URL",
            button_command=lambda: self.run_in_thread(url_analyzer.analyze_url, url_entry.get(), url_results)
        )
        url_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

    def create_network_widgets(self, parent_frame):
        main_scroll_frame = self.create_main_scrollable_frame(parent_frame)

        # --- Port Scanner ---
        port_frame, port_entry, port_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="Port Scanner",
            entry_placeholder="Enter Domain or IP",
            button_text="Scan Ports",
            button_command=lambda: self.run_in_thread(port_scanner.scan_ports, port_entry.get(), port_results)
        )
        port_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- Subdomain Finder ---
        sub_frame, sub_entry, sub_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="Subdomain Finder",
            entry_placeholder="Enter Domain (e.g., google.com)",
            button_text="Find Subdomains",
            button_command=lambda: self.run_in_thread(subdomain_finder.find_subdomains, sub_entry.get(), sub_results)
        )
        sub_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- Connection Monitor ---
        conn_frame = self.create_themed_frame(main_scroll_frame)
        conn_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(conn_frame, "Suspicious Connection Monitor").pack(anchor="w", padx=10, pady=(5, 5))

        conn_info_label = ctk.CTkLabel(conn_frame, text="Detects potential DoS attacks by counting connections from each IP.", justify="left")
        conn_info_label.pack(fill="x", padx=10, pady=(0, 5))

        conn_results = self.create_themed_textbox(conn_frame)
        conn_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        conn_button = self.create_themed_button(conn_frame, "Scan Connections", lambda: self.run_in_thread(connection_monitor.monitor_connections, conn_results))
        conn_button.pack(fill="x", padx=10, pady=(0, 10))

    # =================================================================================
    # WIDGET CREATION - TOOLS
    # =================================================================================
    def create_tools_widgets(self, parent_frame):
        main_scroll_frame = self.create_main_scrollable_frame(parent_frame)

        # --- Identity Generator ---
        id_frame = self.create_themed_frame(main_scroll_frame)
        id_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(id_frame, "Fake Identity Generator").pack(anchor="w", padx=10, pady=(5, 5))
        
        id_results = self.create_themed_textbox(id_frame)
        id_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        id_button = self.create_themed_button(
            id_frame, "Generate New Identity",
            lambda: self.run_in_thread(identity_generator.generate_fake_identity, "random", id_results)
        )
        id_button.pack(fill="x", padx=10, pady=(0, 10))

        # --- Crypter ---
        crypter_frame = self.create_themed_frame(main_scroll_frame)
        crypter_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(crypter_frame, "Text Encrypter/Decrypter (AES)").pack(anchor="w", padx=10, pady=(5, 5))

        crypter_text_entry = self.create_themed_textbox(crypter_frame, height=100)
        crypter_text_entry.pack(fill="x", expand=True, padx=10, pady=5)
        crypter_text_entry.insert("1.0", "Enter text here...")

        crypter_pass_entry = self.create_themed_entry(crypter_frame, placeholder_text="Enter password")
        crypter_pass_entry.pack(fill="x", padx=10, pady=5)

        crypter_button_frame = ctk.CTkFrame(crypter_frame, fg_color="transparent")
        crypter_button_frame.pack(fill="x", padx=10, pady=(0, 10))

        encrypt_button = self.create_themed_button(crypter_button_frame, "Encrypt", lambda: self.run_in_thread(crypter.encrypt_text, crypter_text_entry.get("1.0", "end-1c"), crypter_pass_entry.get(), crypter_text_entry))
        encrypt_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        decrypt_button = self.create_themed_button(crypter_button_frame, "Decrypt", lambda: self.run_in_thread(crypter.decrypt_text, crypter_text_entry.get("1.0", "end-1c"), crypter_pass_entry.get(), crypter_text_entry))
        decrypt_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

    # =================================================================================
    # WIDGET CREATION - SETTINGS
    # =================================================================================
    def create_settings_widgets(self, parent_frame):
        main_scroll_frame = self.create_main_scrollable_frame(parent_frame)

        settings_frame = self.create_themed_frame(main_scroll_frame)
        settings_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(settings_frame, "UI Settings").pack(anchor="w", padx=10, pady=(5, 10))

        def choose_color():
            color_code = colorchooser.askcolor(title="Choose accent color", initialcolor=self.accent_color)
            if color_code and color_code[1]:
                self.accent_color = color_code[1]
                self.config["accent_color"] = self.accent_color
                self.apply_accent_color_to_ui()
                save_config(self.config)

        color_button = self.create_themed_button(settings_frame, "Change Accent Color", choose_color)
        color_button.pack(fill="x", padx=10, pady=10)

        # --- Thème (Mode d'apparence) ---
        appearance_frame = self.create_themed_frame(main_scroll_frame)
        appearance_frame.pack(fill="x", expand=True, pady=(15, 15), padx=5)
        self.create_themed_title_label(appearance_frame, "Appearance Mode").pack(anchor="w", padx=10, pady=(5, 10))

        def change_appearance_mode(new_mode):
            ctk.set_appearance_mode(new_mode)
            self.config["appearance_mode"] = new_mode
            save_config(self.config)

        appearance_menu = ctk.CTkOptionMenu(appearance_frame, values=["Light", "Dark", "System"],
                                            command=change_appearance_mode)
        appearance_menu.set(self.config.get("appearance_mode", "Dark").capitalize())
        self.themed_option_menus.append(appearance_menu)
        appearance_menu.pack(fill="x", padx=10, pady=(0, 10))

        # --- Gestion du Token Discord ---
        token_frame = self.create_themed_frame(main_scroll_frame)
        token_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(token_frame, "Discord Bot Token").pack(anchor="w", padx=10, pady=(5, 5))

        token_entry = self.create_themed_entry(token_frame, placeholder_text="Enter your Discord bot token")
        token_entry.insert(0, self.config.get("discord_bot_token", ""))
        token_entry.pack(fill="x", padx=10, pady=5)

        def save_token():
            self.config["discord_bot_token"] = token_entry.get()
            save_config(self.config)
            messagebox.showinfo("Token Saved", "Discord bot token has been saved successfully.")

        save_token_button = self.create_themed_button(token_frame, "Save Token", save_token)
        save_token_button.pack(fill="x", padx=10, pady=(0, 10))

        # --- Réinitialisation des paramètres ---
        reset_button = ctk.CTkButton(main_scroll_frame, text="Reset All Settings to Default", command=self.reset_settings_to_default, fg_color="#B22222", hover_color="#DC143C")
        reset_button.pack(fill="x", padx=5, pady=(15, 5))

    # =================================================================================
    # WIDGET CREATION - GAMING
    # =================================================================================
    def create_gaming_widgets(self, parent_frame):
        main_scroll_frame = self.create_main_scrollable_frame(parent_frame)

        # --- FPS Booster ---
        game_frame = self.create_themed_frame(main_scroll_frame)
        game_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(game_frame, "Performance Booster").pack(anchor="w", padx=10, pady=(5, 5))

        warning_label = ctk.CTkLabel(game_frame, text="⚠️ This feature modifies system settings like power plans. Use with caution.", text_color="#FFD700", wraplength=450, justify="left")
        warning_label.pack(fill="x", padx=10, pady=5)

        # --- Interrupteur FPS Boost ---
        fps_switch_var = ctk.StringVar(value="off")
        def fps_switch_event():
            if fps_switch_var.get() == "on":
                self.run_in_thread(performance_booster.apply_fps_boost, game_results)
            else:
                self.run_in_thread(performance_booster.revert_fps_boost, game_results)

        fps_switch = ctk.CTkSwitch(game_frame, text="FPS Boost (High Performance Plan & Temp Cleanup)", variable=fps_switch_var, onvalue="on", offvalue="off", command=fps_switch_event, font=("Segoe UI", 14, "bold"))
        self.themed_checkboxes.append(fps_switch) # Pour que la couleur s'applique
        fps_switch.pack(anchor="w", padx=10, pady=10)

        # --- Interrupteur Network Boost ---
        net_switch_var = ctk.StringVar(value="off")
        def net_switch_event():
            if net_switch_var.get() == "on":
                self.run_in_thread(performance_booster.apply_network_boost, game_results)
            else:
                self.run_in_thread(performance_booster.revert_network_boost, game_results)

        net_switch = ctk.CTkSwitch(game_frame, text="Network Boost (Lower Latency)", variable=net_switch_var, onvalue="on", offvalue="off", command=net_switch_event, font=("Segoe UI", 14, "bold"))
        self.themed_checkboxes.append(net_switch)
        net_switch.pack(anchor="w", padx=10, pady=(0, 10))

        game_results = self.create_themed_textbox(game_frame)
        game_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # =================================================================================
    # WIDGET CREATION - DISCORD
    # =================================================================================
    def create_discord_widgets(self, parent_frame):
        main_scroll_frame = self.create_main_scrollable_frame(parent_frame)

        # --- User Info Lookup ---
        user_frame, user_entry, user_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="Discord User Lookup",
            entry_placeholder="Enter User ID",
            button_text="Get User Info",
            button_command=lambda: self.run_in_thread(discord_tools.get_user_info, user_entry.get(), self.config.get("discord_bot_token"), user_results)
        )
        user_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- Token Checker ---
        token_frame, token_entry, token_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="Discord Token Checker",
            entry_placeholder="Enter Discord Token",
            button_text="Check Token",
            button_command=lambda: self.run_in_thread(discord_tools.check_token, token_entry.get(), token_results)
        )
        token_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- Invite Info ---
        invite_frame, invite_entry, invite_results = self.create_styled_widget_frame(
            parent=main_scroll_frame,
            title="Discord Invite Info",
            entry_placeholder="Enter Invite Code (e.g., discordgg)",
            button_text="Get Invite Info",
            button_command=lambda: self.run_in_thread(discord_tools.get_invite_info, invite_entry.get(), invite_results)
        )
        invite_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)

        # --- Webhook Sender ---
        wh_frame = self.create_themed_frame(main_scroll_frame)
        wh_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(wh_frame, "Webhook Sender").pack(anchor="w", padx=10, pady=(5, 5))
        
        wh_url_entry = self.create_themed_entry(wh_frame, placeholder_text="Enter Webhook URL")
        wh_url_entry.pack(fill="x", padx=10, pady=5, ipady=4)
        
        wh_msg_box = self.create_themed_textbox(wh_frame, height=80)
        wh_msg_box.pack(fill="x", expand=True, padx=10, pady=5)
        wh_msg_box.insert("1.0", "Your message here...")

        wh_button = self.create_themed_button(wh_frame, "Send Message", lambda: self.run_in_thread(discord_tools.send_webhook_message, wh_url_entry.get(), wh_msg_box.get("1.0", "end-1c"), wh_msg_box))
        wh_button.pack(fill="x", padx=10, pady=(0, 10))

    # =================================================================================
    # WIDGET CREATION - ANO
    # =================================================================================
    def create_ano_widgets(self, parent_frame):
        main_scroll_frame = self.create_main_scrollable_frame(parent_frame)

        # --- Anonymizer ---
        ano_frame = self.create_themed_frame(main_scroll_frame)
        ano_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(ano_frame, "System Anonymizer").pack(anchor="w", padx=10, pady=(5, 5))

        warning_label = ctk.CTkLabel(ano_frame, text="⚠️ WARNING: This feature modifies system settings and requires administrator rights. A restart is required for some changes. Use with caution.", text_color="#FFD700", wraplength=450, justify="left")
        warning_label.pack(fill="x", padx=10, pady=5)

        reboot_note_label = ctk.CTkLabel(ano_frame, text="Note: The PC name change will only be applied after a full system restart.", font=("Segoe UI", 12, "italic"), text_color=self.text_color)
        reboot_note_label.pack(fill="x", padx=10, pady=(0, 5))

        ano_results = self.create_themed_textbox(ano_frame)
        ano_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def confirm_and_run_anonymizer(): # type: ignore
            """Affiche une boîte de dialogue de confirmation avant de lancer l'anonymisation."""
            response = messagebox.askyesno(
                "Confirm Action",
                "Are you sure you want to change the system hostname and MAC address?\n\n"
                "This action requires a restart to fully apply and is not easily reversible.",
                icon='warning'
            )
            if response: # Si l'utilisateur clique sur "Oui"
                self.run_in_thread(anonymizer.change_all, ano_results)

        ano_button = self.create_themed_button(ano_frame, "Change All (Hostname & MAC)", confirm_and_run_anonymizer)
        ano_button.pack(fill="x", padx=10, pady=(0, 10))

        # --- Effaceur de journaux ---
        logs_frame = self.create_themed_frame(main_scroll_frame)
        logs_frame.pack(fill="x", expand=True, pady=(15, 15), padx=5)
        self.create_themed_title_label(logs_frame, "Trace Cleaner").pack(anchor="w", padx=10, pady=(5, 5))

        logs_warning = ctk.CTkLabel(logs_frame, text="⚠️ DANGER: This will irreversibly delete all Windows Event Logs.", text_color="#FF4500", wraplength=450, justify="left")
        logs_warning.pack(fill="x", padx=10, pady=5)

        def confirm_and_clear_logs():
            response = messagebox.askyesno(
                "Confirm IRREVERSIBLE Action",
                "Are you absolutely sure you want to delete all Windows Event Logs?\n\nThis action cannot be undone and will erase all system, security, and application logs.",
                icon='warning'
            )
            if response:
                self.run_in_thread(anonymizer.clear_event_logs, ano_results) # Affiche le résultat dans la même boîte

        logs_button = ctk.CTkButton(logs_frame, text="Clear All Event Logs", command=confirm_and_clear_logs, fg_color="#B22222", hover_color="#DC143C")
        self.themed_buttons.append(logs_button) # Pour que le thème de couleur ne l'écrase pas
        logs_button.pack(fill="x", padx=10, pady=(0, 10))

        # --- Anti-Télémétrie ---
        telemetry_frame = self.create_themed_frame(main_scroll_frame)
        telemetry_frame.pack(fill="x", expand=True, pady=(0, 15), padx=5)
        self.create_themed_title_label(telemetry_frame, "Anti-Telemetry").pack(anchor="w", padx=10, pady=(5, 5))

        telemetry_btn_frame = ctk.CTkFrame(telemetry_frame, fg_color="transparent")
        telemetry_btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        disable_telemetry_btn = self.create_themed_button(telemetry_btn_frame, "Disable Telemetry", lambda: self.run_in_thread(anonymizer.toggle_telemetry, False, ano_results))
        disable_telemetry_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        enable_telemetry_btn = self.create_themed_button(telemetry_btn_frame, "Re-enable Telemetry", lambda: self.run_in_thread(anonymizer.toggle_telemetry, True, ano_results))
        enable_telemetry_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

    # =================================================================================
    # UI HELPERS & THEMING
    # =================================================================================
    def _calculate_hover_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 25)
        g = min(255, g + 25)
        b = min(255, b + 25)
        return f"#{r:02x}{g:02x}{b:02x}"

    def apply_accent_color_to_ui(self):
        self.button_hover_color = self._calculate_hover_color(self.accent_color)
        self.nav_button_active_fg_color = self.accent_color
        self.logo_label.configure(text_color=self.accent_color)

        for button in self.themed_buttons:
            button.configure(fg_color=self.accent_color, hover_color=self.button_hover_color)
        for widget in self.themed_entries_textboxes:
            widget.configure(border_color=self.accent_color)
        for widget in self.themed_option_menus:
            widget.configure(fg_color=self.accent_color, button_color=self.accent_color, button_hover_color=self.button_hover_color)
        for widget in self.themed_checkboxes:
            widget.configure(fg_color=self.accent_color)
        for label in self.themed_title_labels:
            label.configure(text_color=self.accent_color)
        
        # Rafraîchir la vue de la catégorie actuelle, mais seulement si elle a déjà été définie
        if self.current_category_button:
            self.show_category_frame(self.current_category_button.category_key)

    def show_category_frame(self, category_key):
        for key, frame in self.category_frames.items():
            if key == category_key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

        for key, button in self.nav_buttons.items():
            if key == category_key:
                button.configure(fg_color=self.nav_button_active_fg_color, text_color=self.nav_button_active_text_color)
                button.category_key = key # Stocker la clé de catégorie sur le bouton
                self.current_category_button = button
            else:
                button.configure(fg_color=self.nav_button_inactive_fg_color, text_color=self.nav_button_inactive_text_color)

    def create_main_scrollable_frame(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
        return scroll_frame

    def create_styled_widget_frame(self, parent, title, entry_placeholder, button_text, button_command, second_button_text=None, second_button_command=None):
        frame = self.create_themed_frame(parent)
        self.create_themed_title_label(frame, title).pack(anchor="w", padx=10, pady=(5, 5))
        entry = self.create_themed_entry(frame, placeholder_text=entry_placeholder)
        entry.pack(fill="x", padx=10, pady=5, ipady=4)
        results_box = self.create_themed_textbox(frame)
        results_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        if second_button_text:
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(0, 10))
            btn1 = self.create_themed_button(btn_frame, button_text, button_command)
            btn1.pack(side="left", fill="x", expand=True, padx=(0, 5))
            btn2 = self.create_themed_button(btn_frame, second_button_text, second_button_command)
            btn2.pack(side="left", fill="x", expand=True, padx=(5, 0))
        else:
            btn = self.create_themed_button(frame, button_text, button_command)
            btn.pack(fill="x", padx=10, pady=(0, 10))
            
        return frame, entry, results_box

    def create_themed_frame(self, parent):
        return ctk.CTkFrame(parent, fg_color=self.second_bg_color, corner_radius=8)

    def create_themed_title_label(self, parent, text):
        label = ctk.CTkLabel(parent, text=text, font=("Consolas", 16, "bold"))
        self.themed_title_labels.append(label)
        return label

    def create_themed_entry(self, parent, placeholder_text, width=None):
        # Si width n'est pas spécifié (None), CTkEntry peut lever une erreur.
        # On s'assure de passer une valeur numérique. 140 est la valeur par défaut de CTkEntry.
        effective_width = width if width is not None else 140
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder_text, fg_color="#2b2b2b", border_width=1, text_color=self.text_color, width=effective_width)
        self.themed_entries_textboxes.append(entry)
        return entry

    def create_themed_textbox(self, parent, height=200):
        textbox = ctk.CTkTextbox(parent, fg_color="#2b2b2b", border_width=1, text_color=self.text_color, height=height, wrap="word")
        self.themed_entries_textboxes.append(textbox)
        return textbox

    def create_themed_button(self, parent, text, command):
        button = ctk.CTkButton(parent, text=text, command=command, font=("Segoe UI", 13, "bold"), height=35, corner_radius=6)
        self.themed_buttons.append(button)
        return button

    def display_results(self, result_text, result_widget):
        if isinstance(result_widget, ctk.CTkTextbox):
            result_widget.configure(state="normal")
            result_widget.delete("1.0", "end")
            result_widget.insert("1.0", result_text)
            result_widget.configure(state="disabled")
        elif isinstance(result_widget, ctk.CTkEntry):
            result_widget.delete(0, "end")
            result_widget.insert(0, result_text)

    def run_in_thread(self, target_func, *args):
        result_widget = args[-1]
        thread_args = args[:-1]
        
        def task_wrapper():
            try:
                self.display_results("Running...", result_widget)
                result = target_func(*thread_args)
                self.after(0, self.display_results, result, result_widget)
            except Exception as e:
                error_msg = f"An error occurred in the tool:\n{type(e).__name__}: {e}"
                self.logger.error(error_msg, exc_info=True)
                self.after(0, self.display_results, error_msg, result_widget)

        threading.Thread(target=task_wrapper, daemon=True).start()

    def show_help_popup(self):
        """Affiche une fenêtre d'aide avec des informations et un lien Discord."""
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help & Information")
        help_window.geometry("550x450")
        help_window.transient(self) # Garde la fenêtre au-dessus de la principale
        help_window.grab_set() # Bloque les interactions avec la fenêtre principale
        help_window.resizable(False, False)

        help_text = """
Bienvenue dans SXTOOLS PREMIUM !

Ceci est une suite d'outils pour l'OSINT (Renseignement en Sources Ouvertes) et le CSINT (Cyber Security Intelligence).

Comment l'utiliser ?
1.  Sélectionnez une catégorie dans le menu de gauche (OSINT, Discord, etc.).
2.  Choisissez un outil dans la fenêtre principale.
3.  Remplissez le champ de saisie avec l'information demandée.
4.  Cliquez sur le bouton d'action pour lancer l'analyse.

Points importants :

● Catégorie ANO : Ces outils modifient les paramètres système. Vous devez lancer SXTOOLS PREMIUM en tant qu'administrateur pour qu'ils fonctionnent. Un redémarrage est nécessaire pour appliquer le changement de nom du PC.

● Discord User Lookup : Cet outil nécessite un token de bot Discord valide. Vous devez l'ajouter dans le fichier `mxtools_config.json` à la ligne "discord_bot_token".

Des questions ? Besoin d'aide ?
Rejoignez notre communauté sur Discord !
"""

        label = ctk.CTkLabel(help_window, text=help_text, justify="left", font=("Segoe UI", 13), wraplength=500)
        label.pack(pady=20, padx=20, fill="x")

        def open_discord():
            webbrowser.open_new("https://discord.gg/inconnu")

        discord_button = ctk.CTkButton(help_window, text="Rejoindre le Discord", command=open_discord, font=("Segoe UI", 13, "bold"))
        discord_button.pack(pady=10)

        ok_button = ctk.CTkButton(help_window, text="OK", command=help_window.destroy, width=100)
        ok_button.pack(pady=(10, 20))

    def reset_settings_to_default(self):
        """Réinitialise la configuration aux valeurs par défaut."""
        response = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset all settings to their default values?\n\nThe application will need to be restarted to apply all changes.",
            icon='warning'
        )
        if response:
            self.config = DEFAULT_CONFIG.copy()
            save_config(self.config)
            messagebox.showinfo(
                "Settings Reset",
                "Settings have been reset to default. Please restart the application."
            )