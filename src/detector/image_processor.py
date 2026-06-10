import cv2
import numpy as np
from .debug_manager import debug_manager


class ImageProcessor:
    
    def preprocess_image(self, image):
       # Preproceseaza imaginea pentru detectarea contururilor
        
        # Conversie la gri
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicam bilateralFilter pentru reducerea zgomotului pastrand marginile
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Detectarea marginilor cu Canny
        edges = cv2.Canny(filtered, 30, 200)
        
        return gray, edges
    
    def preprocess_plate_for_ocr(self, plate_image):
        # Preproceseaza regiunea placutei pentru OCR
        
        try:
            # Conversie la gri daca nu este deja
            if len(plate_image.shape) == 3:
                gray_plate = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_plate = plate_image.copy()
            
            # Detecteaza si elimina zona steagului EU (daca exista)
            gray_plate = self._remove_eu_flag_zone(gray_plate)
            
            # Redimensioneaza pentru OCR mai bun (de obicei mai mare este mai bine)
            height, width = gray_plate.shape
            scale_factor = max(3, 300 // width)  # Asigura latimea de cel putin 300px
            new_width = width * scale_factor
            new_height = height * scale_factor
            
            scaled = cv2.resize(gray_plate, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Aplicam blur pentru reducerea zgomotului
            blurred = cv2.GaussianBlur(scaled, (5, 5), 0)
            
            # Aplicam threshold pentru binarizare (text negru pe fundal alb)
            # Incercam mai multe metode
            _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Aplicam operatii morfologice pentru curatare
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            processed = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel) # umple gauri in litere
            processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel) # elimina puncte mici
            
            return processed
            
        except Exception as e:
            debug_manager.log(f"Eroare preprocesare OCR: {e}")
            return plate_image
    
    def _remove_eu_flag_zone(self, gray_plate):
        # Detecteaza si elimina zona steagului EU (partea stanga albastra cu RO)
        height, width = gray_plate.shape

        # Analizeaza zona stanga (primii 10% din latime)
        eu_zone_width = int(width * 0.1)
        left_zone = gray_plate[:, :eu_zone_width]
        right_zone = gray_plate[:, eu_zone_width:]
        
        # Calculeaza intensitatea medie in fiecare zona
        left_mean = np.mean(left_zone)
        right_mean = np.mean(right_zone)
        
        # Daca zona stanga e semnificativ mai intunecata (steagul albastru -> gri intunecat)
        darkness_threshold = 25  # Diferenta minima de intensitate
        if right_mean - left_mean > darkness_threshold:
            debug_manager.log(f"Zona EU detectata: stanga={left_mean:.1f}, dreapta={right_mean:.1f}")
            # Taie zona stanga si pastreaza doar partea cu text
            cut_width = int(width * 0.08)  # Taie primii 8% din latime
            cropped_plate = gray_plate[:, cut_width:]
            debug_manager.log(f"    Placuta taiata: {width}x{height} -> {cropped_plate.shape[1]}x{cropped_plate.shape[0]}\n")
            return cropped_plate
        
        return gray_plate
    
    def draw_detection_result(self, image, bbox, detected_text):
        # Deseneaza rezultatul detectiei pe imagine
     
        x, y, w, h = bbox
        result_image = image.copy()
        
        # Desenam chenarul verde in jurul placutei
        cv2.rectangle(result_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Adaugam textul detectat daca exista
        if detected_text:
            # Calculam pozitia textului
            text_x = max(0, x)
            text_y = max(30, y - 10)
            
            # Adaugam fundal pentru text pentru vizibilitate
            text_size = cv2.getTextSize(detected_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(result_image, (text_x, text_y - text_size[1] - 10), 
                         (text_x + text_size[0], text_y + 5), (0, 255, 0), -1)
            
            # Adaugam textul
            cv2.putText(result_image, detected_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        return result_image