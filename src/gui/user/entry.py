import os

import qrcode
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from config import MAX_PARKING_SPACES
from db import count_cars_in_parking, enter_parking, fetch_user_by_plate, update_user_qr_path
from detector.debug_manager import debug_manager
from gui.entry_scanner_thread import LiveEntryScannerThread
from gui.window_utils import set_dark_titlebar


class UserEntryMixin:
    def set_entry_source_buttons(self, source):
        # Seteaza starea butoanelor pentru sursa de intrare selectata

        self.entry_source = source
        if hasattr(self, "entry_live_btn") and hasattr(self, "entry_video_btn"):
            self.entry_live_btn.setObjectName("actionBtnActive" if source == "live" else "actionBtn")
            self.entry_video_btn.setObjectName("actionBtnActive" if source == "video" else "actionBtn")

            self.entry_live_btn.style().unpolish(self.entry_live_btn)
            self.entry_live_btn.style().polish(self.entry_live_btn)
            self.entry_video_btn.style().unpolish(self.entry_video_btn)
            self.entry_video_btn.style().polish(self.entry_video_btn)

    def select_entry_source_live(self):
        # Opreste orice scanner activ si deschide dialogul pentru selectarea live-ului

        self.stop_entry_live_scanner()
        self.set_entry_source_buttons("live")
        self.start_entry_live_scanner()

    def select_entry_source_video(self):
        # Opreste orice scanner live activ si deschide dialogul pentru selectarea unui fisier video

        self.stop_entry_live_scanner()
        self.set_entry_source_buttons("video")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecteaza Video",
            "",
            "Video (*.mp4 *.avi *.mov *.mkv *.wmv);;Toate fisierele (*)"
        )

        if not file_path:
            return

        self.start_entry_video_scanner(file_path)

    def on_processing_finished(self, result_image, detected_text, _plate_region):
        # Handler pentru finalizarea procesarii

        if result_image is not None:
            self.display_result_image(result_image)

        if not detected_text:
            self._show_unreadable_plate_message()
            self.reset_timer.start(10000)
            return

        try:
            cod = enter_parking(detected_text)
        except ValueError as exc:
            self._show_qr_generation_error(detected_text, str(exc))
            self.reset_timer.start(10000)
            return

        if not cod:
            self._show_qr_generation_error(detected_text)
            self.reset_timer.start(10000)
            return

        self._save_detected_plate_qr(detected_text, cod)
        self.result_label.setText(f"  {detected_text}    |    QR Cod generat")
        self.result_label.setObjectName("statusSuccess")
        self.result_label.setStyle(self.result_label.style())
        self.enter_action_frame.hide()
        self.result_panel.setVisible(True)

        # Porneste timer-ul pentru resetare dupa 10 secunde
        self.reset_timer.start(10000)

    def _show_unreadable_plate_message(self):
        # Afiseaza mesaj de eroare cand textul detectat nu este lizibil
        self.result_label.setText("  TEXTUL NU ESTE LIZIBIL")
        self.result_label.setObjectName("statusErrorReadable")
        self.enter_action_frame.hide()
        self.result_panel.setVisible(True)

    def _show_qr_generation_error(self, detected_text, message="Eroare generare", warning=True):
        # Afiseaza mesaj de eroare cand nu se poate genera codul QR pentru textul detectat
        self.result_label.setText(f"  {detected_text}    |    {message}")
        self.result_label.setObjectName("statusWarning" if warning else "statusError")
        self.result_label.setStyle(self.result_label.style())
        self.enter_action_frame.hide()
        self.result_panel.setVisible(True)

    def _save_detected_plate_qr(self, detected_text, cod):
        # Genereaza cod QR pentru textul detectat si il salveaza in folderul corespunzator (users sau visitors)
        import time

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(cod)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Determina daca textul detectat apartine unui utilizator inregistrat sau unui vizitator
        user_row = fetch_user_by_plate(detected_text)
        qr_subfolder = "users" if user_row else "visitors"
        qr_folder = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'qrcodes', qr_subfolder)
        if not os.path.exists(qr_folder):
            os.makedirs(qr_folder)

        unique_id = int(time.time() * 1000)
        qr_filename = os.path.join(qr_folder, f"qr_{detected_text}_{unique_id}.png")
        qr_img.save(qr_filename)

        if user_row:
            old_qr_path = user_row[6]
            if old_qr_path and os.path.exists(os.path.abspath(old_qr_path)):
                try:
                    os.remove(os.path.abspath(old_qr_path))
                except Exception:
                    pass
            update_user_qr_path(user_row[0], os.path.abspath(qr_filename))

        debug_manager.log(f"QR generat si salvat la: {qr_filename}")

    def start_entry_live_scanner(self):
        # Porneste capturarea live pentru intrare

        # Verificam daca sunt locuri disponibile inainte de a porni scanarea
        try:
            current = count_cars_in_parking()
            if current >= MAX_PARKING_SPACES:
                # Afisam mesaj si nu pornim scanarea
                if hasattr(self, 'result_label'):
                    self.result_label.setText("Parcarea este plină. Toate locurile sunt ocupate.")
                return
        except Exception:
            # Daca nu se poate citi numarul, continuam si incercam sa pornim scanarea
            pass

        if getattr(self, "entry_source", "live") != "live":
            return

        if hasattr(self, "entry_scanner_thread") and self.entry_scanner_thread and self.entry_scanner_thread.isRunning():
            return

        # Opreste orice scanner live activ inainte de a porni unul nou
        self.stop_entry_live_scanner()

        self.set_entry_source_buttons("live")

        self.image_display.show()
        self.result_panel.setVisible(False)

        # Porneste scanarea live
        enable_debug = self.debug_checkbox.isChecked()
        self.entry_scanner_thread = LiveEntryScannerThread(enable_debug=enable_debug)
        self.entry_scanner_thread.frame_ready.connect(self.on_entry_frame_ready)
        self.entry_scanner_thread.plate_detected.connect(self.on_entry_plate_detected)
        self.entry_scanner_thread.error.connect(self.on_entry_scan_error)
        self.entry_scanner_thread.stopped.connect(self.on_entry_scanner_stopped)

        if not hasattr(self, "_entry_threads"):
            self._entry_threads = []
        self._entry_threads.append(self.entry_scanner_thread)

        self.entry_scanner_thread.start()

    def start_entry_video_scanner(self, video_path):
        # Porneste scanarea unui fisier video pentru intrare

        if not video_path:
            return

        # Verificam daca sunt locuri disponibile inainte de a porni scanarea video
        try:
            current = count_cars_in_parking()
            if current >= MAX_PARKING_SPACES:
                # Afisam mesaj; nu pornim scanarea video, dar pastram butonul Enter activ
                if hasattr(self, 'result_label'):
                    self.result_label.setText("Parcarea este plină. Toate locurile sunt ocupate.")
                return
        except Exception:
            pass

        self.last_entry_video_path = video_path

        if hasattr(self, "entry_scanner_thread") and self.entry_scanner_thread and self.entry_scanner_thread.isRunning():
            return

        # Opreste orice scanner live activ inainte de a porni scanarea video
        self.stop_entry_live_scanner()

        self.image_display.show()
        self.result_panel.setVisible(False)

        # Porneste scanarea video
        enable_debug = self.debug_checkbox.isChecked()
        self.entry_scanner_thread = LiveEntryScannerThread(enable_debug=enable_debug, video_path=video_path)
        self.entry_scanner_thread.frame_ready.connect(self.on_entry_frame_ready)
        self.entry_scanner_thread.plate_detected.connect(self.on_entry_plate_detected)
        self.entry_scanner_thread.error.connect(self.on_entry_scan_error)
        self.entry_scanner_thread.stopped.connect(self.on_entry_scanner_stopped)

        if not hasattr(self, "_entry_threads"):
            self._entry_threads = []
        self._entry_threads.append(self.entry_scanner_thread)

        self.entry_scanner_thread.start()

    def stop_entry_live_scanner(self):
        # Opreste capturarea live daca este activa

        if hasattr(self, "entry_scanner_thread") and self.entry_scanner_thread:
            if self.entry_scanner_thread.isRunning():
                self.entry_scanner_thread.stop()
                self.entry_scanner_thread.wait(2000)
                if self.entry_scanner_thread.isRunning():
                    return
            self.entry_scanner_thread = None

    def on_entry_frame_ready(self, q_image):
        # Actualizeaza preview-ul live pentru intrare

        pixmap = QPixmap.fromImage(q_image)
        target_w = self.image_frame.width() - 10
        target_h = self.image_frame.height() - 10
        if target_w <= 0 or target_h <= 0:
            return

        scaled_pixmap = pixmap.scaled(
            target_w,
            target_h,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        # Decupeaza pixmap-ul pentru a se potrivi exact in chenar
        if scaled_pixmap.width() > target_w or scaled_pixmap.height() > target_h:
            x_offset = max(0, (scaled_pixmap.width() - target_w) // 2)
            y_offset = max(0, (scaled_pixmap.height() - target_h) // 2)
            scaled_pixmap = scaled_pixmap.copy(x_offset, y_offset, target_w, target_h)

        self.image_display.setPixmap(scaled_pixmap)

    def on_entry_plate_detected(self, result_image, detected_text, plate_region):
        # Cand a fost detectata o placuta valida

        self.stop_entry_live_scanner()
        self.on_processing_finished(result_image, detected_text, plate_region)

    def on_entry_scan_error(self, error_message):
        # Eroare la capturarea live

        err_box = QMessageBox(self)
        set_dark_titlebar(err_box)
        err_box.setWindowTitle("Eroare camera")
        err_box.setText(error_message)
        err_box.exec_()

    def on_entry_scanner_stopped(self):
        sender = self.sender()
        if hasattr(self, "_entry_threads") and sender in self._entry_threads:
            self._entry_threads.remove(sender)
