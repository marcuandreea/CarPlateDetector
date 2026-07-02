from db import fetch_active_subscription_plan_by_plate, get_parking_fee, pay_parking


class UserPaymentMixin:
    def handle_check_payment(self):
        # Handler pentru butonul Verifica - calculeaza si afiseaza suma de plata

        cod = self.pay_code_input.text().strip()
        if not cod:
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusWarning")
            self.pay_status_label.setText("  Introduceti codul masinii")
            self.pay_status_label.setStyle(self.pay_status_label.style())  # Force refresh
            return

        try:
            fee = get_parking_fee(cod=cod)
            if not fee:
                self.pay_status_label.show()
                self.pay_status_label.setObjectName("statusError")
                self.pay_status_label.setText("  Codul introdus nu exista in sistem")
                self.pay_status_label.setStyle(self.pay_status_label.style())
                return

            user_subscription = fetch_active_subscription_plan_by_plate(
                fee["license_plate"]
            )
            if user_subscription:
                self.pay_status_label.show()
                self.pay_status_label.setObjectName("statusSuccess")
                self.pay_status_label.setText("  Aveti abonament activ. Indreptati-va catre iesire.")
                self.pay_status_label.setStyle(self.pay_status_label.style())
                self.pay_code_input.clear()
                self.pay_code_input.hide()
                self.pay_info_frame.hide()
                self.pending_payment_code = None
                return

            self.pay_minutes_label.setText(
                f" Timp petrecut: {fee['parked_minutes']} minute"
            )
            self.pay_amount_label.setText(
                f" Total de plata: {fee['amount']:.2f} RON"
            )
            self.pay_info_frame.show()
            self.pay_status_label.hide()

            self.pending_payment_code = fee["parking_code"]

        except Exception as e:
            self.pay_status_label.show()
            self.pay_status_label.setObjectName("statusError")
            self.pay_status_label.setText(f"  Eroare la calcularea platii: {e}")
            self.pay_status_label.setStyle(self.pay_status_label.style())

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
