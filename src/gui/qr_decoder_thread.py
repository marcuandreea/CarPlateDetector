import cv2
from PyQt5.QtCore import QThread, pyqtSignal


class QRCodeDecoderThread(QThread):
    # Thread pentru decodarea unui QR dintr-o imagine selectata pentru Plata sau Iesire

    finished = pyqtSignal(str)
    # Semnal pentru a transmite codul decodat inapoi la GUI

    def __init__(self, qr_image_path):
        super().__init__()
        self.qr_image_path = qr_image_path

    def run(self):

        try:
            # Citeste folosind OpenCV si QrCodeDetector intern
            qr_img = cv2.imread(self.qr_image_path)
            if qr_img is None:
                self.finished.emit("")
                return

            detector = cv2.QRCodeDetector()
            data, vertices, _ = detector.detectAndDecode(qr_img)

            self.finished.emit(data if data else "")
        except Exception as e:
            print(f"Eroare la decodare QR {e}")
            self.finished.emit("")
