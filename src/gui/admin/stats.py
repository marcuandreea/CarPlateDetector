from config import MAX_PARKING_SPACES
from db import count_cars_in_parking


class AdminStatsMixin:
    def update_car_count(self):
        # Actualizeaza label-ul cu numarul de masini in parcare
        try:
            count = count_cars_in_parking()
            self.car_count_label.setText(f" Masini in parcare: {count}")

            # Actualizam si afisarea locurilor disponibile in pagina de Intrare, daca exista
            available = MAX_PARKING_SPACES - count
            if available < 0:
                available = 0
            if hasattr(self, 'available_spots_label'):
                if available > 0:
                    self.available_spots_label.setText(f"Locuri disponibile: {available} / {MAX_PARKING_SPACES}")
                else:
                    self.available_spots_label.setText("Parcarea este plină. Toate locurile sunt ocupate.")

            # Daca suntem in modul 'enter' si nu mai sunt locuri, oprim detectia live
            if available <= 0 and getattr(self, 'current_action', None) == 'enter':
                if hasattr(self, 'stop_entry_live_scanner'):
                    try:
                        self.stop_entry_live_scanner()
                    except Exception:
                        pass
        except Exception as e:
            self.car_count_label.setText(f" Eroare la numarare: {e}")
