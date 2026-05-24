import os
import time
import cv2
from datetime import datetime


class DebugManager:
    # Manager pentru logging si debugging al sistemului de detectie placute
    
    def __init__(self, log_file_path="debug_output/debug_log.txt"):
        
        # Initializeaza managerul de debug.
        
        self.log_file_path = log_file_path
        self.debug_enabled = False  # Debug dezactivat implicit
        
    def set_debug_mode(self, enabled):
        # Activeaza sau dezactiveaza modul debug.
        
        self.debug_enabled = enabled
        if enabled:
            # Creaza directorul debug_output daca nu exista
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            
            # Initializeaza fisierul de log 
            self._initialize_log()
            
            # Initializeaza cronometrarea
            self.start_time = time.time()
    
    def _initialize_log(self):
        # Reseteaza fisierul de log la fiecare rulare noua
        try:
            # Reseteaza complet fisierul de log (suprascrie continutul)
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("DETECTOR PLACUTE DE INMATRICULARE\n")
                f.write("="*60 + "\n\n")
        except Exception as e:
            # Fallback la print daca nu se poate scrie in fisier
            print(f"Eroare la initializarea log-ului: {e}")
    
    def log(self, message):
        # Scrie un mesaj in fisierul de log doar daca debug este activat.
        
        if not self.debug_enabled:
            return
            
        try:
            log_entry = f"{message}\n"
            
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
        except Exception as e:
            # Fallback la print doar daca nu se poate scrie in fisier
            print(f"Eroare la logging: {e}")
    
    def log_time(self):
         # Termina cronometrarea si afiseaza timpul de executie doar daca debug este activat.
        
        if not self.debug_enabled:
            return
            
        if self.start_time is None:
            self.log("Eroare: Cronometrarea nu a fost pornita")
            return
        
        end_time = time.time()
        execution_time = end_time - self.start_time
        time_str = f"{execution_time:.2f} secunde"
        
        self.log(f"Timp executie: {time_str}")
    
    def save_debug_image(self, image, filename):
        # Salveaza o imagine debug doar daca modul debug este activat.
        
        if not self.debug_enabled:
            return
            
        try:
            filepath = f"debug_output/{filename}"
            cv2.imwrite(filepath, image)
            self.log(f"Salvez imagine debug: {filename}\n")
        except Exception as e:
            self.log(f"Eroare salvare debug: {e}")
    

# Instanta globala pentru a fi utilizata in toate modulele
debug_manager = DebugManager()