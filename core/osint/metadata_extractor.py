from PIL import Image
from PIL.ExifTags import TAGS
import PyPDF2
# Pour python-docx (fichiers .docx)
# from docx import Document
# from docx.opc.coreprops import CoreProperties
from utils.logger import app_logger
import os

def extract_image_metadata(filepath):
    """Extracts EXIF metadata from an image file."""
    metadata = {}
    try:
        with Image.open(filepath) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    metadata[str(tag_name)] = str(value)
            else:
                metadata["Info"] = "No EXIF data found."
    except Exception as e:
        metadata["Error"] = f"Could not read image metadata: {e}"
    return metadata

def extract_pdf_metadata(filepath):
    """Extracts metadata from a PDF file."""
    metadata = {}
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            doc_info = reader.metadata
            if doc_info:
                for key, value in doc_info.items():
                    # Les clés de PyPDF2 sont comme /Author, /Title. On les nettoie.
                    clean_key = key.lstrip('/')
                    metadata[clean_key] = str(value)
            else:
                metadata["Info"] = "No metadata found in PDF."
    except Exception as e:
        metadata["Error"] = f"Could not read PDF metadata: {e}"
    return metadata

# def extract_docx_metadata(filepath):
#     """Extracts metadata from a DOCX file."""
#     metadata = {}
#     try:
#         doc = Document(filepath)
#         props = doc.core_properties
#         prop_attrs = [
#             "author", "category", "comments", "content_status",
#             "created", "identifier", "keywords", "language",
#             "last_modified_by", "last_printed", "modified",
#             "revision", "subject", "title", "version"
#         ]
#         for attr in prop_attrs:
#             value = getattr(props, attr)
#             if value:
#                 metadata[attr.replace('_', ' ').capitalize()] = str(value)
#         if not metadata:
#              metadata["Info"] = "No core properties metadata found in DOCX."
#     except Exception as e:
#         metadata["Error"] = f"Could not read DOCX metadata: {e}"
#     return metadata

def extract_metadata_from_file(filepath):
    app_logger.info(f"Attempting to extract metadata from: {filepath}")
    if not filepath or not os.path.exists(filepath):
        app_logger.error(f"File not found or path is empty: {filepath}")
        return "Error: File not found or path is empty."

    _, extension = os.path.splitext(filepath.lower())
    extracted_data = {}

    if extension in ['.jpg', '.jpeg', '.png', '.gif', '.tiff']:
        extracted_data = extract_image_metadata(filepath)
    elif extension == '.pdf':
        extracted_data = extract_pdf_metadata(filepath)
    # elif extension == '.docx':
    #     # Décommentez si vous installez python-docx et importez les modules nécessaires
    #     app_logger.info("DOCX file detected. Install 'python-docx' to extract metadata.")
    #     extracted_data = {"Info": "DOCX metadata extraction requires 'python-docx'. Please install it."}
    #     # extracted_data = extract_docx_metadata(filepath) # Si python-docx est installé
    else:
        app_logger.warning(f"Unsupported file type for metadata extraction: {extension}")
        return f"Unsupported file type: {extension}. Supported: jpg, jpeg, png, gif, tiff, pdf." #, docx (if enabled)."

    if not extracted_data or "Error" in extracted_data or "Info" in extracted_data and len(extracted_data) == 1:
        output = f"Metadata for {os.path.basename(filepath)}:\n"
        output += "----------------------------------------\n"
        if "Error" in extracted_data:
            output += extracted_data["Error"]
            app_logger.error(f"Error extracting metadata from {filepath}: {extracted_data['Error']}")
        elif "Info" in extracted_data:
             output += extracted_data["Info"]
             app_logger.info(f"Info for metadata extraction from {filepath}: {extracted_data['Info']}")
        else:
            output += "No specific metadata could be extracted or file type not fully supported."
            app_logger.info(f"No specific metadata extracted from {filepath}")
    else:
        output = f"Metadata for {os.path.basename(filepath)}:\n"
        output += "----------------------------------------\n"
        for key, value in extracted_data.items():
            output += f"{key}: {value}\n"
        app_logger.info(f"Successfully extracted metadata from {filepath}")
    
    return output.strip()

if __name__ == '__main__':
    # Vous devrez créer des fichiers de test pour cela.
    # Exemple: un fichier image.jpg avec des données EXIF, un test.pdf
    
    # Test image (créez un fichier dummy.jpg ou utilisez une image existante)
    # try:
    #     from PIL import Image as PImage
    #     img = PImage.new('RGB', (60, 30), color = 'red')
    #     img.save('dummy.jpg', exif=b"Exif\x00\x00II*\x00\x08\x00\x00\x00\x01\x00\x0f\x01\x02\x00\x06\x00\x00\x00\x1a\x00\x00\x00Test\x00") # Minimal EXIF
    #     print("--- Image Metadata Test (dummy.jpg) ---")
    #     print(extract_metadata_from_file('dummy.jpg'))
    #     os.remove('dummy.jpg')
    # except ImportError:
    #     print("Pillow not installed, skipping image metadata test.")
    # except Exception as e:
    #     print(f"Error creating dummy image for test: {e}")


    # Test PDF (créez un fichier dummy.pdf)
    try:
        from reportlab.pdfgen import canvas # Pour créer un PDF de test rapidement
        c = canvas.Canvas("dummy.pdf")
        c.setTitle("Test PDF Title")
        c.setAuthor("MXTools Test Author")
        c.setSubject("Dummy PDF for testing metadata")
        c.drawString(100, 750, "This is a test PDF.")
        c.save()
        print("\n--- PDF Metadata Test (dummy.pdf) ---")
        print(extract_metadata_from_file('dummy.pdf'))
        os.remove('dummy.pdf')
    except ImportError:
        print("reportlab not installed, cannot create dummy.pdf for testing. Please create one manually.")
    except Exception as e:
        print(f"Error in PDF test: {e}")


    print("\n--- Non-existent file Test ---")
    print(extract_metadata_from_file('non_existent_file.xyz'))