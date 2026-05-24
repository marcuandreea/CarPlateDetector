from gui.utils import set_dark_titlebar
import os
import cv2
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QRect
import qrcode

from db import enter_parking, pay_parking, leave_parking, create_database_connection
from gui.utils import QRCodeScannerThread, LiveEntryScannerThread
from detector.debug_manager import debug_manager

class UserLogicMixin:
    def set_entry_source_buttons(self, source):
        self.entry_source = source
        if hasattr(self, "entry_live_btn") and hasattr(self, "entry_video_btn"):
            self.entry_live_btn.setObjectName("actionBtnActive" if source == "live" else "actionBtn")
            self.entry_video_btn.setObjectName("actionBtnActive" if source == "video" else "actionBtn")

            self.entry_live_btn.style().unpolish(self.entry_live_btn)
            self.entry_live_btn.style().polish(self.entry_live_btn)
            self.entry_video_btn.style().unpolish(self.entry_video_btn)
            self.entry_video_btn.style().polish(self.entry_video_btn)

    def select_entry_source_live(self):
        self.stop_entry_live_scanner()
        self.set_entry_source_buttons("live")
        self.start_entry_live_scanner()

    def select_entry_source_video(self):
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

    def on_processing_finished(self, result_image, detected_text, plate_region):
        # Handler pentru finalizarea procesarii
        if result_image is not None:
            if hasattr(self, "enter_status_label"):
                self.enter_status_label.hide()
            self.display_result_image(result_image)
            
            if detected_text:
                # Apeleaza enter_parking automat cu numarul detectat
                cod = enter_parking(detected_text)
                if cod:
                    self.result_label.setText(f"  {detected_text}    |    QR Cod generat")
                    
                    # Generare QR
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(cod)
                    qr.make(fit=True)
                    
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Salvam QR-ul intr-un folder dedicat cu numele masinii
                    qr_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'qrcodes')
                    if not os.path.exists(qr_folder):
                        os.makedirs(qr_folder)
                    # Am inlocuit {cod} cu {detected_text} pt nume fisier masina
                    qr_filename = os.path.join(qr_folder, f"qr_{detected_text}.png")
                    qr_img.save(qr_filename)
                    
                    debug_manager.log(f"QR generat si salvat la: {qr_filename}")
                else:
                    self.result_label.setText(f"  {detected_text}    |    Eroare generare")
                self.result_panel.setVisible(True)
            else:
                self.result_label.setText("  TEXT NOT READABLE")
                self.result_label.setObjectName("statusErrorReadable")
                self.result_panel.setVisible(True)
        
        # Porneste timer-ul pentru resetare dupa 10 secunde
        self.reset_timer.start(10000)  # 10000 ms = 10 secunde
    
    def start_entry_live_scanner(self):
        # Porneste capturarea live pentru intrare
        if getattr(self, "entry_source", "live") != "live":
            return

        if hasattr(self, "entry_scanner_thread") and self.entry_scanner_thread and self.entry_scanner_thread.isRunning():
            return

        self.stop_entry_live_scanner()

        self.set_entry_source_buttons("live")

        self.image_display.show()
        self.result_panel.setVisible(False)
        if hasattr(self, "enter_status_label"):
            self.enter_status_label.setObjectName("statusWarning")
            self.enter_status_label.setText("  Scaneaza placuta...")
            self.enter_status_label.setStyle(self.enter_status_label.style())
            self.enter_status_label.show()

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
        if not video_path:
            return

        if hasattr(self, "entry_scanner_thread") and self.entry_scanner_thread and self.entry_scanner_thread.isRunning():
            return

        self.stop_entry_live_scanner()

        self.image_display.show()
        self.result_panel.setVisible(False)
        if hasattr(self, "enter_status_label"):
            self.enter_status_label.setObjectName("statusWarning")
            self.enter_status_label.setText("  Scaneaza placuta...")
            self.enter_status_label.setStyle(self.enter_status_label.style())
            self.enter_status_label.show()

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
        scaled_pixmap = pixmap.scaled(
            self.image_frame.width() - 10,
            self.image_frame.height() - 10,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_display.setPixmap(scaled_pixmap)

    def on_entry_plate_detected(self, result_image, detected_text, plate_region):
        # Cand a fost detectata o placuta valida
        self.stop_entry_live_scanner()
        self.on_processing_finished(result_image, detected_text, plate_region)

    def on_entry_scan_error(self, error_message):
        # Eroare la capturarea live
        if hasattr(self, "enter_status_label"):
            self.enter_status_label.setObjectName("statusError")
            self.enter_status_label.setText(f"  {error_message}")
            self.enter_status_label.setStyle(self.enter_status_label.style())
            self.enter_status_label.show()
        err_box = QMessageBox(self)
        set_dark_titlebar(err_box)
        err_box.setWindowTitle("Eroare camera")
        err_box.setText(error_message)
        err_box.exec_()

    def on_entry_scanner_stopped(self):
        sender = self.sender()
        if hasattr(self, "_entry_threads") and sender in self._entry_threads:
            self._entry_threads.remove(sender)

    def start_qr_scanner_for_pay(self):
        # Porneste scanarea QR in timp real pentru plata
        self.start_qr_scanner("pay")

    def start_qr_scanner_for_leave(self):
        # Porneste scanarea QR in timp real pentru iesire
        self.start_qr_scanner("leave")

    def start_qr_scanner(self, target):
        # Porneste scanarea QR in functie de target
        # Daca exista deja un scanner activ, opreste-l si seteaza target-ul in asteptare
        if hasattr(self, "qr_scanner_thread") and self.qr_scanner_thread and self.qr_scanner_thread.isRunning():
            self.pending_qr_target = target
            self.stop_qr_scanner()
            return

        self.stop_qr_scanner()
        self.current_qr_target = target

        if target == "pay":
            status_label = self.pay_status_label
            preview_label = self.pay_qr_preview
        else:
            status_label = self.leave_status_label
            preview_label = self.leave_qr_preview

        status_label.show()
        status_label.setObjectName("statusWarning")
        status_label.setText("  Scaneaza codul QR...")
        status_label.setStyle(status_label.style())
        preview_label.show()
        self.ensure_qr_preview_size(preview_label)

        self.qr_scanner_thread = QRCodeScannerThread()
        self.qr_scanner_thread.frame_ready.connect(self.on_qr_frame_ready)
        self.qr_scanner_thread.code_detected.connect(self.on_qr_code_detected)
        self.qr_scanner_thread.error.connect(self.on_qr_scan_error)
        self.qr_scanner_thread.stopped.connect(self.on_qr_scanner_stopped)

        if not hasattr(self, "_qr_threads"):
            self._qr_threads = []
        self._qr_threads.append(self.qr_scanner_thread)

        self.qr_scanner_thread.start()

    def stop_qr_scanner(self):
        # Opreste camera daca este activa
        if hasattr(self, "qr_scanner_thread") and self.qr_scanner_thread:
            if self.qr_scanner_thread.isRunning():
                self.qr_scanner_thread.stop()
                self.qr_scanner_thread.wait(2000)
                if self.qr_scanner_thread.isRunning():
                    return
            self.qr_scanner_thread = None

    def on_qr_frame_ready(self, q_image):
        # Actualizeaza preview-ul live al camerei
        if not hasattr(self, "current_qr_target"):
            return

        target_label = self.pay_qr_preview if self.current_qr_target == "pay" else self.leave_qr_preview

        # Validare dimensiuni
        if target_label.width() <= 0 or target_label.height() <= 0:
            return
        
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            target_label.width(),
            target_label.height(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        # Decupeaza pixmap-ul pentru a se potrivi exact in chenar
        if (scaled_pixmap.width() > target_label.width()) and (scaled_pixmap.height() > target_label.height()):
            x_offset = (scaled_pixmap.width() - target_label.width()) // 2
            y_offset = (scaled_pixmap.height() - target_label.height()) // 2
            scaled_pixmap = scaled_pixmap.copy(QRect(x_offset, y_offset, target_label.width(), target_label.height()))

        target_label.setPixmap(scaled_pixmap)

    def ensure_qr_preview_size(self, preview_label):
        # Adjustare dimensiuni zona scanare QR
        target_width = self.action_content.width()
        if target_width <= 0:
            target_width = 640
        preview_label.setMinimumWidth(target_width)

    def on_qr_code_detected(self, decoded_text):
        if not decoded_text:
            return

        if self.current_qr_target == "pay":
            self.pay_code_input.setText(decoded_text)
            self.pay_status_label.setText(" Cod QR detectat. Puteti efectua plata...")
            self.pay_status_label.setObjectName("statusSuccess")
            self.pay_code_input.show()
            self.pay_status_label.setStyle(self.pay_status_label.style())
            self.pay_qr_preview.hide()
            self.stop_qr_scanner()
            self.handle_check_payment()
        else:
            self.leave_code_input.setText(decoded_text)
            self.leave_status_label.setText(" Cod QR detectat. Puteti parasi parcarea...")
            self.leave_status_label.setObjectName("statusSuccess")
            self.leave_code_input.show()
            self.leave_execute_btn.show()
            self.leave_status_label.setStyle(self.leave_status_label.style())
            self.leave_qr_preview.hide()
            self.stop_qr_scanner()
            self.handle_leave_parking()

    def on_qr_scan_error(self, error_message):
        # Afiseaza erori la scanare si opreste camera
        if hasattr(self, "current_qr_target") and self.current_qr_target == "pay":
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusError")
            self.pay_status_label.setText(f" {error_message}")
            self.pay_status_label.setStyle(self.pay_status_label.style())
        else:
            self.leave_status_label.show()
            self.leave_status_label.setObjectName("statusError")
            self.leave_status_label.setText(f" {error_message}")
            self.leave_status_label.setStyle(self.leave_status_label.style())
        self.stop_qr_scanner()

    def on_qr_scanner_stopped(self):
        # Ascunde preview-ul cand camera s-a oprit
        sender = self.sender()
        if sender is not None and sender is not self.qr_scanner_thread:
            return
        if hasattr(self, "current_qr_target") and self.current_qr_target == "pay":
            self.pay_qr_preview.hide()
        else:
            self.leave_qr_preview.hide()
        self.current_qr_target = None

        # Reseteaza thread-ul si verifica daca exista o cerere in asteptare pentru scanare QR
        self.qr_scanner_thread = None
        if hasattr(self, "_qr_threads") and sender in self._qr_threads:
            self._qr_threads.remove(sender)
        if hasattr(self, "pending_qr_target") and self.pending_qr_target:
            next_target = self.pending_qr_target
            self.pending_qr_target = None
            self.start_qr_scanner(next_target)

    def handle_check_payment(self):
        # Handler pentru butonul Verifica - calculeaza si afiseaza suma de plata
        cod = self.pay_code_input.text().strip()
        if not cod:
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusWarning")
            self.pay_status_label.setText("  Introduceti codul masinii")
            self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh
            return

        # Nu inregistram plata inca, doar calculam
        conn = create_database_connection()
        if not conn:
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusError")
            self.pay_status_label.setText("  Nu s-a putut conecta la baza de date")
            self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ora_intrare, ora_platire FROM masini WHERE cod = %s
           """, (cod,))
            row = cursor.fetchone()
            
            if not row:
                self.pay_status_label.show()
                self.pay_status_label.setObjectName("statusError")
                self.pay_status_label.setText("  Codul introdus nu exista in sistem")
                self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh
                return
            
            ora_intrare, ora_platire = row
            ora_actuala = datetime.now()
            
            # Calculam timpul
            if ora_platire is None:
                diferenta_secunde = (ora_actuala - ora_intrare).total_seconds()
            else:
                diferenta_secunde = (ora_actuala - ora_platire).total_seconds()
            
            minute_totale = int(diferenta_secunde / 60)
            
            # Obtinem tarifele
            cursor.execute("""
                SELECT durata, pret FROM taxe ORDER BY durata ASC
           """)
            taxe_rows = cursor.fetchall()
            
            if not taxe_rows:
                self.pay_status_label.show()
                self.pay_status_label.setObjectName("statusError")
                self.pay_status_label.setText("  Nu exista tarife configurate in sistem")
                self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh
                return
            
            # Gasim primul tarif care depaseste sau este egal cu durata
            pret_de_plata = float(taxe_rows[-1][1])
            for durata_minuta, pret in taxe_rows:
                if minute_totale <= durata_minuta:
                    pret_de_plata = float(pret)
                    break
            
            # Afisam informatiile pe interfata
            self.pay_minutes_label.setText(f" Timp petrecut: {minute_totale} minute")
            self.pay_amount_label.setText(f" Total de plata: {pret_de_plata:.2f} RON")
            self.pay_info_frame.show()
            self.pay_status_label.hide()
            
            # Salvam codul pentru confirmare
            self.pending_payment_code = cod
            
        except Exception as e:
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusError")
            self.pay_status_label.setText(f"  Eroare la calcularea platii: {e}")
            self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def handle_confirm_payment(self):  
        # Handler pentru butonul Plata - confirma si inregistreaza plata
        if not hasattr(self, 'pending_payment_code') or not self.pending_payment_code:
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusWarning")
            self.pay_status_label.setText("  Verificati mai intai codul")
            self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh
            return
        
        success = pay_parking(self.pending_payment_code)
        if success:
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusSuccess")
            self.pay_status_label.setText("  Plata a fost inregistrata cu succes")
            self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh
            self.pay_code_input.clear()
            self.pay_info_frame.hide()
            self.pending_payment_code = None
            
            self.pay_code_input.hide()
            self.pay_qr_preview.hide()
        else:
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusError")
            self.pay_status_label.setText("  Plata nu a putut fi inregistrata. Verificati codul")
            self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh

    def handle_leave_parking(self):
        #Handler pentru Leave - apeleaza leave_parking din db
        cod = self.leave_code_input.text().strip()
        if not cod:
            self.leave_status_label.show()
            self.leave_status_label.setObjectName("statusWarning")
            self.leave_status_label.setText("  Introduceti codul masinii")
            self.leave_status_label.setStyle(self.leave_status_label.style())  # Force refresh
            return

        success, error_code = leave_parking(cod)
        if success:
            self.leave_status_label.show()
            self.leave_status_label.setObjectName("statusSuccess")
            self.leave_status_label.setText("  Drum bun!")
            self.leave_status_label.setStyle(self.leave_status_label.style())  # Force refresh
            self.leave_code_input.clear()
            
            # Resetam interfata
            self.leave_code_input.hide()
            self.leave_execute_btn.hide()
            self.leave_qr_preview.hide()
        else:
            if error_code == "not_paid":
                message = "  Va rugam efectuati plata"
            elif error_code == "expired":
                message = "  Plata expirata"
            elif error_code == "not_found":
                message = "  Codul introdus nu exista in sistem"
            else:
                message = "  Plecarea nu a putut fi inregistrata"
            
            self.leave_status_label.show()
            self.leave_status_label.setObjectName("statusError")
            self.leave_status_label.setText(message)
            self.leave_status_label.setStyle(self.leave_status_label.style())  # Force refresh
    
    def reset_interface(self):
        # Reseteaza interfata la starea initiala pentru o noua intrare
        self.image_display.clear()
        self.image_display.show()
        
        # Ascunde panoul de rezultate
        self.result_panel.setVisible(False)
        self.result_label.setText("")
        
        # Arata din nou butoanele de actiune
        self.enter_action_frame.show()
        
        # Opreste timer-ul daca mai ruleaza
        if self.reset_timer.isActive():
            self.reset_timer.stop()
    
    def display_result_image(self, cv_image):
        # Afiseaza imaginea cu rezultatul
        try:
            # Convert to RGB for display
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale pixmap sa se potriveasca in chenar (pastrand aspect ratio)
            scaled_pixmap = pixmap.scaled(
                self.image_frame.width() - 10,
                self.image_frame.height() - 10,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.image_display.setPixmap(scaled_pixmap)
            
        except Exception:
            pass


