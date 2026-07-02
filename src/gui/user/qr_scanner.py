from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap

from gui.qr_scanner_thread import QRCodeScannerThread


class UserQRScannerMixin:
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

        enable_debug = self.debug_checkbox.isChecked() if hasattr(self, "debug_checkbox") else False
        self.qr_scanner_thread = QRCodeScannerThread(enable_debug=enable_debug)
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
