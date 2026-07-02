import sys

import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

from detector.image_processor import ImageProcessor


class QRCodeScannerThread(QThread):
    # Thread pentru scanarea codurilor QR in timp real din camera web

    frame_ready = pyqtSignal(object)
    code_detected = pyqtSignal(str)
    error = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, camera_index=0, motion_pixel_threshold=1000, motion_idle_seconds=3.0, roi_scale=0.6,
                 enable_debug=False):
        super().__init__()
        self.camera_index = camera_index
        self._running = True
        self._cap = None
        self.motion_pixel_threshold = motion_pixel_threshold
        self.motion_idle_seconds = motion_idle_seconds
        self.roi_scale = roi_scale
        self._roi_size = None
        self.enable_debug = enable_debug

    def stop(self):
        self._running = False

    def run(self):
        if sys.platform == "win32":
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(self.camera_index)
        self._cap = cap
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        if not cap.isOpened():
            self.error.emit("Camera nu poate fi accesata.")
            self.stopped.emit()
            return

        detector = cv2.QRCodeDetector()
        processor = ImageProcessor()
        prev_gray = None
        last_motion_time = None

        # Loop de citire a cadrelor din camera si detectare QR
        try:
            while self._running:
                ret, frame = cap.read()
                if not ret:
                    self.error.emit("Nu se poate citi cadrul din camera.")
                    break

                # Detectie miscare pentru a porni scanarea QR
                gray_full, _ = processor.preprocess_image(frame)
                motion_detected = False
                if prev_gray is not None:
                    diff = cv2.absdiff(prev_gray, gray_full)
                    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                    motion_pixels = cv2.countNonZero(thresh)
                    motion_detected = motion_pixels >= self.motion_pixel_threshold

                prev_gray = gray_full

                if motion_detected:
                    last_motion_time = cv2.getTickCount() / cv2.getTickFrequency()
                    #print (f"Miscare detectata: {motion_pixels} pixeli schimbati")

                in_active_window = False
                if last_motion_time is not None:
                    now_time = cv2.getTickCount() / cv2.getTickFrequency()
                    in_active_window = (now_time - last_motion_time) <= self.motion_idle_seconds

                # Setari zona de scanare QR
                h, w = gray_full.shape
                if self._roi_size is None:
                    roi_size = int(min(h, w) * self.roi_scale)
                    roi_size = max(120, roi_size)
                    self._roi_size = roi_size
                roi_size = min(self._roi_size, min(h, w))
                roi_x = (w - roi_size) // 2
                roi_y = (h - roi_size) // 2
                roi_frame = frame[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size]

                data = ""
                if in_active_window:
                    # Porneste detectia QR in zona patratului
                    processed_roi = processor.preprocess_plate_for_ocr(roi_frame)
                    data, _, _ = detector.detectAndDecode(processed_roi)

                    if not data:
                        data, _, _ = detector.detectAndDecode(roi_frame)

                # Deseneaza colturile patratului pentru zona de scanare doar in debug
                if self.enable_debug:
                    corner_len = max(12, int(roi_size * 0.08))
                    color = (166, 70, 217)
                    thickness = 2

                    # Stanga sus
                    cv2.line(frame, (roi_x, roi_y), (roi_x + corner_len, roi_y), color, thickness)
                    cv2.line(frame, (roi_x, roi_y), (roi_x, roi_y + corner_len), color, thickness)
                    # Dreapta sus
                    cv2.line(frame, (roi_x + roi_size, roi_y), (roi_x + roi_size - corner_len, roi_y), color, thickness)
                    cv2.line(frame, (roi_x + roi_size, roi_y), (roi_x + roi_size, roi_y + corner_len), color, thickness)
                    # Stanga jos
                    cv2.line(frame, (roi_x, roi_y + roi_size), (roi_x + corner_len, roi_y + roi_size), color, thickness)
                    cv2.line(frame, (roi_x, roi_y + roi_size), (roi_x, roi_y + roi_size - corner_len), color, thickness)
                    # Dreapta jos
                    cv2.line(frame, (roi_x + roi_size, roi_y + roi_size), (roi_x + roi_size - corner_len, roi_y + roi_size), color, thickness)
                    cv2.line(frame, (roi_x + roi_size, roi_y + roi_size), (roi_x + roi_size, roi_y + roi_size - corner_len), color, thickness)

                # Convertim cadrul la format QImage pentru a fi afisat in GUI
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_ready.emit(q_image)

                if data:
                    self.code_detected.emit(data)
                    break

                self.msleep(120 if not in_active_window else 30)
        except Exception as e:
            self.error.emit(f"Eroare la scanarea QR: {e}")
        finally:
            cap.release()
            self._cap = None
            self.stopped.emit()
