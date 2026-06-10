import cv2

from .image_processor import ImageProcessor
from .contour_analyzer import ContourAnalyzer
from .ocr_engine import OCREngine
from .debug_manager import debug_manager


class LicensePlateDetector:
    
    def __init__(self):
        # Initializeaza detectorul cu componentele necesare

        self.image_processor = ImageProcessor()
        self.contour_analyzer = ContourAnalyzer()
        self.ocr_engine = OCREngine()
    
    def detect_and_read_license_plate(self, image, edges=None):
        # Preprocesarea imaginii - obtine marginile pentru detectie

        if image is None:
            return None, "", None
        
        if edges is None:
            _ , edges = self.image_processor.preprocess_image(image)

        # Gasirea candidatilor pentru placute
        candidate_plates = self.contour_analyzer.find_license_plate_contours(image, edges)

        if not candidate_plates:
            debug_manager.log("Nu am gasit nicio placuta")
            return image, "", None

        debug_manager.log(f"Gasit {len(candidate_plates)} candidati")

        # Procesam primul candidat (cel mai probabil sa fie o placuta)
        best_candidate = candidate_plates[0]
        _, _, w, h = best_candidate['bbox']

        debug_manager.log(f"    Cel mai bun candidat: {w}x{h}, aspect={best_candidate['aspect_ratio']:.2f}, "
                          f"area={best_candidate['area']:.0f}, area_ratio={best_candidate['area'] / (w * h):.2f}, "
                          f"width_ratio={w / image.shape[1]:.2f}\n")

        # Extragem textul si desenam rezultatul
        detected_text, result_image = self._process_plate_candidate(image, best_candidate)

        # Extragem regiunea pentru compatibilitate
        x, y, w, h = best_candidate['bbox']
        plate_region = image[y:y+h, x:x+w]

        return result_image, detected_text, plate_region
    
    def _process_plate_candidate(self, image, candidate):
        # Proceseaza candidatul si deseneaza rezultatul
        x, y, w, h = candidate['bbox']
        
        # Extragem regiunea placutei
        plate_region = image[y:y+h, x:x+w]
        
        # Preproceseaza regiunea pentru OCR
        processed_plate = self.image_processor.preprocess_plate_for_ocr(plate_region)
        
        # Salveaza imaginea procesata pentru debug
        debug_manager.save_debug_image(processed_plate, "plate_for_ocr.jpg")
        
        # Aplicam OCR pe regiunea placutei
        detected_text = self.ocr_engine.extract_text_with_ocr(processed_plate)
        
        debug_manager.log("\n" + "="*40)
        if detected_text:
            debug_manager.log(f"Placuta detectata: {detected_text}")
        else:
            debug_manager.log("Placuta detectata dar textul nu a fost detectat")
            
        # Termina cronometrarea
        debug_manager.log_time()
        debug_manager.log("="*40)
        
        # Desenam rezultatul folosind image_processor
        result_image = self.image_processor.draw_detection_result(image, candidate['bbox'], detected_text)
        
        return detected_text, result_image