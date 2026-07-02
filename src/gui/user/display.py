import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap


class UserDisplayMixin:
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
            # Converteste imaginea din format OpenCV (BGR) in format RGB
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
