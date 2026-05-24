import os
import re
import pytesseract

from .debug_manager import debug_manager


class OCREngine:
    # Motorul OCR pentru extragerea textului din placute
    
    def __init__(self):
        # Initializeaza motorul OCR cu configuratia din config
        # Configuratia pentru pytesseract din config
        self.ocr_config = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' # o singura linie de text
        
        # Seteaza calea catre executabilul Tesseract din config
        tesseract_path = r"C:\Program Files\tesseract-ocr\tesseract.exe"
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Mesaj informativ daca calea nu exista
        if not os.path.exists(tesseract_path):
            debug_manager.log(f"Nu gasesc Tesseract la: {tesseract_path}")
        
    def extract_text_with_ocr(self, plate_image):
    
        # Extrage textul dintr-o imagine de placuta folosind pytesseract.
       
        debug_manager.log("Aplic OCR pentru text...")
        
        try:
            # Incearca sa detecteze textul
            raw_text = pytesseract.image_to_string(plate_image, config=self.ocr_config)
            
            if raw_text:
                # Curata textul (elimina spatii, caractere speciale etc.)
                cleaned_text = raw_text.strip().replace(' ', '').replace('\n', '').upper()
                
                # Elimina caracterele care nu sunt litere sau cifre
                cleaned_text = re.sub(r'[^A-Z0-9]', '', cleaned_text)

                if cleaned_text and len(cleaned_text) >= 6:
                    debug_manager.log(f"    Text: {cleaned_text}")
                    return cleaned_text
                else:
                    debug_manager.log("     Text invalid sau prea scurt")
                    return ""
            else:
                debug_manager.log("Nu s-a detectat text")
                return ""
                
        except pytesseract.TesseractNotFoundError:
            debug_manager.log("Tesseract nu este instalat")
            return "[TESSERACT_MISSING]"
        except Exception as e:
            debug_manager.log(f"Eroare OCR: {e}")
            return ""
