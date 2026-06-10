"""
Program pentru detectarea si citirea placutelor de inmatriculare
folosind doar OpenCV si pytesseract (fara modele de machine learning).

Versiune modulara care contine EXACT functionalitatea din main.py original de 300 de linii.

Autor: Sistem de detectare placute
Data: 2025-01-28
"""

import argparse
import os

from detector.license_plate_detector import LicensePlateDetector
from detector.debug_manager import debug_manager


def get_image_path_from_args():
    """Obtine calea imaginii din argumentele liniei de comanda sau cauta automat."""
    parser = argparse.ArgumentParser(
        description="Detecteaza si citeste placutele de inmatriculare din imagini"
    )
    parser.add_argument(
        "image_path", 
        nargs="?",  # Face argumentul optional
        help="Calea catre imaginea de procesat"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Activeaza modul debug (genereaza log si imagini debug)"
    )
    
    args = parser.parse_args()
    
    # Activeaza debug mode in debug_manager
    debug_manager.set_debug_mode(args.debug)
    
    # Daca s-a specificat o imagine, verifica daca exista
    if args.image_path:
        if os.path.exists(args.image_path):
            return args.image_path
        else:
            debug_manager.log(f"Imaginea {args.image_path} nu exista")
            return None

    return None


def main():
    """Functia principala a programului."""
    
    # Obtine calea imaginii
    image_path = get_image_path_from_args()
    
    if not image_path:
        return
    
    # Initializam detectorul
    detector = LicensePlateDetector()
    
    # Detectam si citim placuta
    result_image, detected_text, _ = detector.detect_and_read_license_plate(image_path)
    
    # Afisam rezultatul folosind detectorul
    detector.display_result(result_image, detected_text)
    
if __name__ == "__main__":
    main()