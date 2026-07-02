from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QMessageBox, QPushButton, QTableWidgetItem, QWidget

from db import delete_masina, show_masini
from gui.window_utils import set_dark_titlebar


class AdminCarsMixin:
    def handle_show_masini(self):
        # Handler pentru butonul Masini - afiseaza toate inregistrarile din tabelul masini
        if hasattr(self, 'add_taxa_btn'):
            self.add_taxa_btn.hide()

        try:
            # Updateaza numarul de masini in parcare
            self.update_car_count()

            rows = show_masini()
            if not rows:
                self.admin_results.clear()
                self.admin_results.setRowCount(1)
                self.admin_results.setColumnCount(1)
                self.admin_results.setHorizontalHeaderLabels(["Info"])
                self.admin_results.setItem(0, 0, QTableWidgetItem("(Nicio inregistrare gasita in tabelul 'masini')"))
                return

            # Seteaza  numarul de coloane pentru tabel
            headers = ["Numar_inmatriculare", "Cod", "Ora_intrare", "Ora_platire", "Status", "Actiuni"]
            self.admin_results.clear()
            self.admin_results.setColumnCount(len(headers))
            self.admin_results.setHorizontalHeaderLabels(headers)
            self.admin_results.setRowCount(len(rows))

            for r_idx, r in enumerate(rows):
                numar, cod, ora_i, ora_p, status = r

                # Coloana 0: Numar_inmatriculare
                item = QTableWidgetItem(str(numar) if numar else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 0, item)

                # Coloana 1: Cod
                item = QTableWidgetItem(str(cod) if cod else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 1, item)

                # Coloana 2: Ora_intrare (format YYYY-MM-DD HH:MM:SS)
                time_str = ora_i.strftime("%Y-%m-%d %H:%M:%S") if ora_i else ""
                item = QTableWidgetItem(time_str)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 2, item)

                # Coloana 3: Ora_platire (format YYYY-MM-DD HH:MM:SS)
                time_str = ora_p.strftime("%Y-%m-%d %H:%M:%S") if ora_p else ""
                item = QTableWidgetItem(time_str)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 3, item)

                # Coloana 4: Status
                item = QTableWidgetItem(str(status) if status else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 4, item)

                # Coloana 5: Actiuni (Buton DELETE)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setAlignment(Qt.AlignCenter)

                delete_btn = QPushButton("DELETE")
                delete_btn.setObjectName("tableActionBtn")
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setMinimumHeight(35)
                delete_btn.setFixedWidth(80)
                delete_btn.clicked.connect(lambda checked, nr=numar: self.handle_delete_masina(nr))

                actions_layout.addWidget(delete_btn)
                self.admin_results.setCellWidget(r_idx, 5, actions_widget)

            for row in range(len(rows)):
                self.admin_results.setRowHeight(row, 50)

            self.admin_results.resizeColumnsToContents()
            self.admin_results.setColumnWidth(5, 120)

        except Exception as e:
            self.admin_results.clear()
            self.admin_results.setRowCount(1)
            self.admin_results.setColumnCount(1)
            self.admin_results.setItem(0, 0, QTableWidgetItem(f"Eroare la preluarea masinilor: {e}"))

    def handle_delete_masina(self, numar_inmatriculare):
        # Handler pentru butonul DELETE - permite stergerea unei masini din tabelul masini
        # Cream un QMessageBox personalizat ca sa aiba styling corespunzator
        msg_box = QMessageBox(self)
        set_dark_titlebar(msg_box)
        msg_box.setWindowTitle("Confirmare")
        msg_box.setText(f"Esti sigur ca vrei sa stergi masina cu numarul {numar_inmatriculare}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            success = delete_masina(numar_inmatriculare)
            if success:
                # Si un mesaj de succes vizualizat
                success_msg = QMessageBox(self)
                set_dark_titlebar(success_msg)
                success_msg.setWindowTitle("Succes")
                success_msg.setText(f"Masina {numar_inmatriculare} a fost stearsa cu succes!")
                success_msg.exec_()

                self.handle_show_masini()  # refacem lista (updateaza si car_count intern)
            else:
                err_msg = QMessageBox(self)
                set_dark_titlebar(err_msg)
                err_msg.setWindowTitle("Eroare")
                err_msg.setText("Nu s-a putut sterge masina din baza de date.")
                err_msg.exec_()
