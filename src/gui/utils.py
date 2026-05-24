import sys
import ctypes
import time
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

# Importam clasa care face efectiv detectia si pe cea de debug_manager 
from detector.license_plate_detector import LicensePlateDetector
from detector.image_processor import ImageProcessor
from detector.debug_manager import debug_manager


def set_dark_titlebar(window):
    # Seteaza titlebar-ul ferestrei in Dark Mode
    if sys.platform == "win32":
        try:
            hwnd = int(window.winId())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE_V2 = 19
            
            value = ctypes.c_int(2)  # 2 = enable
            res = ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            if res != 0:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_V2, ctypes.byref(value), ctypes.sizeof(value))
        except Exception as e:
            pass


class QRCodeDecoderThread(QThread):
    # Thread pentru decodarea unui QR dintr-o imagine selectata pentru Plata sau Iesire
    finished = pyqtSignal(str)
    """Semnal trimis cu textul decodat din QR."""

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


class QRCodeScannerThread(QThread):
    # Thread pentru scanarea codurilor QR in timp real din camera web
    frame_ready = pyqtSignal(object)
    code_detected = pyqtSignal(str)
    error = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, camera_index=1, motion_pixel_threshold=1000, motion_idle_seconds=3.0, roi_scale=0.6):
        super().__init__()
        self.camera_index = camera_index
        self._running = True
        self._cap = None
        self.motion_pixel_threshold = motion_pixel_threshold
        self.motion_idle_seconds = motion_idle_seconds
        self.roi_scale = roi_scale
        self._roi_size = None

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

                # Deseneaza colturile patratului pentru zona de scanare
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


class LiveEntryScannerThread(QThread):
    # Thread pentru capturare live si detectare placute cu motion detection in ROI
    frame_ready = pyqtSignal(object)
    plate_detected = pyqtSignal(object, str, object)
    error = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, camera_index=1, roi_scale=0.6, motion_pixel_threshold=4000,
                 processing_window_seconds=10.0, process_interval_seconds=0.3, enable_debug=False,
                 video_path=None):
        super().__init__()
        self.camera_index = camera_index
        self.roi_scale = roi_scale
        self.motion_pixel_threshold = motion_pixel_threshold
        self.processing_window_seconds = processing_window_seconds
        self.process_interval_seconds = process_interval_seconds
        self.enable_debug = enable_debug
        self.video_path = video_path
        self.stationary_trigger_seconds = 0.3
        self._running = True
        self._cap = None

    def stop(self):
        self._running = False

    def run(self):
        if self.video_path:
            cap = cv2.VideoCapture(self.video_path)
        elif sys.platform == "win32":
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(self.camera_index)
        self._cap = cap
        # Setam rezolutia pentru procesare optima
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not cap.isOpened():
            if self.video_path:
                self.error.emit("Video-ul nu poate fi accesat.")
            else:
                self.error.emit("Camera nu poate fi accesata.")
            self.stopped.emit()
            return

        detector = LicensePlateDetector()
        processor = ImageProcessor()
        debug_manager.set_debug_mode(self.enable_debug)

        # Variabile pentru detectia de miscare si controlul procesarii
        prev_gray = None
        last_process_time = 0.0
        found_plate = False
        last_motion_time = None
        in_stationary = False
        was_in_motion = None
        roi_debug_index = 0
        armed_by_motion = False
        motion_streak = 0
        motion_confirm_frames = 3

        # Loop de citire a cadrelor din camera si detectare placute
        try:
            while self._running:
                ret, frame = cap.read()
                if not ret:
                    if self.video_path:
                        if not found_plate:
                            self.error.emit("Video terminat fara detectie.")
                        break
                    self.error.emit("Nu se poate citi cadrul din camera.")
                    break

                frame = cv2.resize(frame, (1280, 720))

                # Setari ROI pentru detectia de miscare
                h, w = frame.shape[:2]
                roi_size = int(min(h, w) * self.roi_scale)
                roi_size = max(120, roi_size)
                roi_width = roi_size
                roi_height = max(80, int(roi_size * 0.35))
                roi_x = (w - roi_width) // 2
                roi_y = (h - roi_size) // 2 + (roi_size - roi_height)
                roi_frame = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]

                # Motion detection doar in ROI
                roi_gray, _ = processor.preprocess_image(roi_frame)
                motion_detected = False
                # Comparatie cu cadrul anterior pentru a detecta miscare in zona de interes
                if prev_gray is not None:
                    diff = cv2.absdiff(prev_gray, roi_gray)
                    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                    motion_pixels = cv2.countNonZero(thresh)
                    motion_detected = motion_pixels >= self.motion_pixel_threshold
                prev_gray = roi_gray

                now = time.time()
                # Logica pentru a decide cand sa ruleze detectia placutei bazat pe miscare si timp
                # Daca nu se mai detecteaza miscare, se ruleaza detectia placutei
                if motion_detected:
                    motion_streak = min(motion_confirm_frames, motion_streak + 1)
                    last_motion_time = now
                    in_stationary = False
                    if motion_streak >= motion_confirm_frames:
                        armed_by_motion = True
                    was_in_motion = True
                else:
                    motion_streak = 0
                    if last_motion_time is None:
                        last_motion_time = now
                    if not in_stationary and (now - last_motion_time) >= self.stationary_trigger_seconds:
                        in_stationary = True
                        last_process_time = 0.0
                    was_in_motion = False

                data = ""
                result_image = None
                plate_region = None

                # Daca suntem in fereastra de procesare dupa detectia de miscare, ruleaza detectia placutei
                if armed_by_motion and in_stationary and (now - last_process_time) >= self.process_interval_seconds:
                    last_process_time = now
                    if self.enable_debug and roi_debug_index % 10 == 0:
                        debug_manager.save_debug_image(roi_frame, f"roi_frame_{roi_debug_index:03d}.jpg")
                    roi_debug_index += 1
                    result_image, data, plate_region = detector.detect_and_read_license_plate(frame)
                    if data:
                        found_plate = True
                        armed_by_motion = False
                        self.plate_detected.emit(result_image, data, plate_region)
                        break

                # Deseneaza dreptunghiul ROI
                color = (217, 70, 166)
                thickness = 2
                cv2.rectangle(
                    frame,
                    (roi_x, roi_y),
                    (roi_x + roi_width, roi_y + roi_height),
                    color,
                    thickness
                )

                # Desenare preview
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ph, pw, ch = rgb.shape
                bytes_per_line = ch * pw
                q_image = QImage(rgb.data, pw, ph, bytes_per_line, QImage.Format_RGB888)
                self.frame_ready.emit(q_image)

                self.msleep(30)
        except Exception as e:
            self.error.emit(f"Eroare la scanarea live: {e}")
        finally:
            cap.release()
            self._cap = None
            self.stopped.emit()


