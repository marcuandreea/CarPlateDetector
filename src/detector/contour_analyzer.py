import cv2
import imutils

from .debug_manager import debug_manager


class ContourAnalyzer:
    # Analiza contururilor pentru detectarea placutelor
    
    def __init__(self):
        # Initializeaza detectorul cu parametrii din configuratie
        # Parametrii pentru detectarea placutei
        self.min_aspect_ratio = 4.0
        self.max_aspect_ratio = 5.25
        self.min_width_ratio = 0.10
        self.max_width_ratio = 0.35
        self.min_area_pixels = 1000
        self.min_area_ratio = 0.07
        
    def find_license_plate_contours(self, image, edges):
        # Gaseste contururile care ar putea fi placute de inmatriculare.
        
        debug_manager.log("Gasesc contururile...")
        
        # Gasirea contururilor
        cnts = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        
        # Sorteaza contururile dupa arie in ordine descrescatoare si pastreaza primele 10
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
        
        _, image_width = image.shape[:2]
        candidate_plates = []
        
        # Cream o copie a imaginii pentru debug
        debug_image = image.copy()
        
        debug_manager.log(f"    Procesez {len(cnts)} contururi\n")
        debug_manager.log(f"Constrangeri:\n"
                          f"    Aspect ratio tinta: {self.min_aspect_ratio}-{self.max_aspect_ratio}\n"
                          f"    Min area pixels: > {self.min_area_pixels}\n"
                          f"    Min area ratio: > {self.min_area_ratio}\n"
                          f"    Width ratio tinta: {self.min_width_ratio}-{self.max_width_ratio}\n")
                          
        
        # Analizeaza fiecare contur
        for i, contour in enumerate(cnts):
            # Aproximeaza conturul
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            aspect_ratio = w / h
            width_ratio = w / image_width
            bbox_area = w * h
            area_ratio = area / bbox_area if bbox_area > 0 else 0
            
            debug_manager.log(f"Contur #{i}: {w}x{h}, aspect={aspect_ratio:.2f}, area={area:.0f}, "
                              f"area_ratio={area_ratio:.2f}, width_ratio={width_ratio:.3f}")
            
            # Doar contururile cu aproximativ 4 puncte (dreptunghiulare)
            if len(approx) >= 4:
                # Verifica daca conturul indeplineste criteriile pentru o placuta
                if (self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio and
                    self.min_width_ratio <= width_ratio <= self.max_width_ratio and
                    area_ratio > self.min_area_ratio and
                    area > self.min_area_pixels):

                    candidate_plates.append({
                        'contour': contour,
                        'bbox': (x, y, w, h),
                        'aspect_ratio': aspect_ratio,
                        'area': cv2.contourArea(contour)
                    })
                    
                    # Deseneaza conturul valid cu verde si indexul
                    cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(debug_image, f"#{i}", (x+5, y+20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    debug_manager.log("     Candidat acceptat")
                else:
                    # Deseneaza conturul invalid cu rosu si indexul
                    cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(debug_image, f"#{i}", (x+5, y+20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Sorteaza candidatii dupa arie (cei mai mari primii)
        candidate_plates = sorted(candidate_plates, key=lambda x: x['area'], reverse=True)
        
        # Salveaza imaginea de debug cu toate contururile
        debug_manager.log("")
        debug_manager.save_debug_image(debug_image, "contours_analysis.jpg")
        
        return candidate_plates
