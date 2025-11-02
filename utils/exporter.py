import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from datetime import datetime
import os
import html # Pour échapper les caractères HTML

class Exporter:
    def __init__(self, default_export_dir="exports"):
        self.default_export_dir = default_export_dir
        if not os.path.exists(self.default_export_dir):
            os.makedirs(self.default_export_dir)

    def _get_save_path(self, base_filename, extension):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.{extension}"
        filepath = filedialog.asksaveasfilename(
            initialdir=self.default_export_dir,
            initialfile=filename,
            defaultextension=f".{extension}",
            filetypes=[(f"{extension.upper()} files", f"*.{extension}"), ("All files", "*.*")]
        )
        return filepath

    def export_to_txt(self, content, base_filename="export"):
        filepath = self._get_save_path(base_filename, "txt")
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Export Successful", f"Data exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export to TXT: {e}")

    def export_to_html(self, content, base_filename="export"):
        filepath = self._get_save_path(base_filename, "html")
        if filepath:
            try:
                # Échapper le contenu pour l'insérer en toute sécurité dans <pre>
                escaped_content = html.escape(content)
                html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{base_filename}</title>
    <style>
        body {{ font-family: 'Courier New', Courier, monospace; background-color: #0d0d0d; color: #e0e0e0; padding: 20px; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; background-color: #1a1a1a; border: 1px solid #ff0000; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Results: {base_filename}</h1>
    <pre>{escaped_content}</pre>
</body>
</html>
"""
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)
                messagebox.showinfo("Export Successful", f"Data exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export to HTML: {e}")

    # def export_to_pdf(self, content, base_filename="export"):
    #     # Nécessite une librairie comme reportlab ou fpdf2
    #     messagebox.showwarning("Not Implemented", "PDF export is not yet implemented.")
    #     # filepath = self._get_save_path(base_filename, "pdf")
    #     # if filepath:
    #     #     try:
    #     #         # Logique de création PDF ici
    #     #         messagebox.showinfo("Export Successful", f"Data exported to {filepath}")
    #     #     except Exception as e:
    #     #         messagebox.showerror("Export Error", f"Failed to export to PDF: {e}")