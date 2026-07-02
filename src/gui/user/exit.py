from db import leave_parking


class UserExitMixin:
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
