from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db import add_taxa, delete_taxa, show_taxe, update_taxa
from gui.window_utils import set_dark_titlebar


class AdminFeesMixin:
    def handle_show_taxe(self):
        #Handler pentru butonul Taxe - afiseaza toate inregistrarile din tabelul taxe
        if hasattr(self, 'add_taxa_btn'):
            self.add_taxa_btn.show()

        try:
            rows = show_taxe()
            if not rows:
                self.admin_results.clear()
                self.admin_results.setRowCount(1)
                self.admin_results.setColumnCount(1)
                self.admin_results.setHorizontalHeaderLabels(["Info"])
                self.admin_results.setItem(0, 0, QTableWidgetItem("(Nicio inregistrare gasita in tabelul 'taxe')"))
                return

            headers = ["ID", "Durata", "Pret", "Actiuni"]
            self.admin_results.clear()
            self.admin_results.setColumnCount(len(headers))
            self.admin_results.setHorizontalHeaderLabels(headers)
            self.admin_results.setRowCount(len(rows))

            for r_idx, r in enumerate(rows):
                tid, durata, pret = r
                # ID coloana
                item_id = QTableWidgetItem(str(tid))
                item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 0, item_id)

                # Durata coloana
                item_durata = QTableWidgetItem(str(durata))
                item_durata.setFlags(item_durata.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 1, item_durata)

                # Pret coloana
                item_pret = QTableWidgetItem(str(pret))
                item_pret.setFlags(item_pret.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 2, item_pret)

                # Actions in Actiuni column
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5) # Am adaugat putin padding sus-jos ca sa aiba spatiu sa respire
                actions_layout.setAlignment(Qt.AlignCenter)
                actions_layout.setSpacing(10)

                edit_btn = QPushButton("EDIT")
                edit_btn.setObjectName("tableActionBtn")
                edit_btn.setCursor(Qt.PointingHandCursor)
                edit_btn.setMinimumHeight(35)
                edit_btn.clicked.connect(lambda checked, row_id=tid: self.handle_edit_price(row_id))

                delete_btn = QPushButton("DELETE")
                delete_btn.setObjectName("tableActionBtn")
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setMinimumHeight(35)
                delete_btn.clicked.connect(lambda checked, row_id=tid: self.handle_delete_taxa(row_id))

                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)

                self.admin_results.setCellWidget(r_idx, 3, actions_widget)

            for row in range(len(rows)):
                self.admin_results.setRowHeight(row, 50)

            self.admin_results.resizeColumnsToContents()
            # Setez o latime fixa pentru coloana de actiuni
            self.admin_results.setColumnWidth(3, 160)

            # Arata butonul Add Taxa
            if hasattr(self, 'add_taxa_btn'):
                self.add_taxa_btn.show()

        except Exception as e:
            self.admin_results.clear()
            self.admin_results.setRowCount(1)
            self.admin_results.setColumnCount(1)
            self.admin_results.setItem(0, 0, QTableWidgetItem(f"Eroare la preluarea taxelor: {e}"))

    def handle_delete_taxa(self, tax_id):
        # Handler pentru butonul DELETE - permite stergerea unei taxe
        msg_box = QMessageBox(self)
        set_dark_titlebar(msg_box)
        msg_box.setWindowTitle("Confirmare")
        msg_box.setText(f"Esti sigur ca vrei sa stergi taxa ID {tax_id}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            success = delete_taxa(tax_id)

            res_box = QMessageBox(self)
            set_dark_titlebar(res_box)

            if success:
                res_box.setWindowTitle("Succes")
                res_box.setText("Taxa a fost stearsa cu succes!")
                res_box.exec_()
                self.handle_show_taxe()  # refacem lista
            else:
                res_box.setWindowTitle("Eroare")
                res_box.setText("Nu s-a putut sterge taxa din baza de date.")
                res_box.exec_()

    def handle_add_taxa(self):
        # Handler pentru butonul ADD - permite adaugarea unei noi taxe.
        dialog = QDialog(self)
        set_dark_titlebar(dialog)
        dialog.setWindowTitle("Adauga Taxa Noua")
        dialog.setMinimumWidth(350)

        layout = QFormLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        durata_input = QLineEdit()
        layout.addRow("Durata (minute):", durata_input)

        pret_input = QLineEdit()
        layout.addRow("Pret (RON):", pret_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)

        # Stilizam butoanele interne OK si Cancel
        # QDialogButtonBox foloseste niste text-uri default pt butoane
        buttons.button(QDialogButtonBox.Ok).setText("OK")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancel")

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec_() == QDialog.Accepted:
            try:
                durata_val = int(durata_input.text().strip())
                pret_val = float(pret_input.text().strip())

                success = add_taxa(durata_val, pret_val)

                res_box = QMessageBox(self)
                set_dark_titlebar(res_box)

                if success:
                    res_box.setWindowTitle("Succes")
                    res_box.setText("Taxa a fost adaugata!")
                    res_box.exec_()
                    self.handle_show_taxe()
                else:
                    res_box.setWindowTitle("Eroare")
                    res_box.setText("Nu s-a putut adauga taxa.")
                    res_box.exec_()
            except ValueError:
                warn_box = QMessageBox(self)
                set_dark_titlebar(warn_box)
                warn_box.setWindowTitle("Avertisment")
                warn_box.setText("Te rog introdu valori numerice valide pentru Durata si Pret.")
                warn_box.exec_()

    def handle_edit_price(self, tax_id):
        current_durata, current_price = self._get_tax_values_for_edit(tax_id)

        dialog = QDialog(self)
        set_dark_titlebar(dialog)
        dialog.setWindowTitle(f"Modificare Taxa (ID: {tax_id})")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        # Input pentru durata
        durata_spinbox = QSpinBox()
        durata_spinbox.setRange(0, 999999)
        durata_spinbox.setValue(int(current_durata) if current_durata else 0)
        form_layout.addRow("Durata noua (minute):", durata_spinbox)

        # Input pentru pret
        pret_spinbox = QDoubleSpinBox()
        pret_spinbox.setRange(0.0, 999999.99)
        pret_spinbox.setDecimals(2)
        pret_spinbox.setValue(float(current_price) if current_price else 0.0)
        form_layout.addRow("Pret nou (RON):", pret_spinbox)

        layout.addLayout(form_layout)

        # Butoane de Ok / Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            new_durata = durata_spinbox.value()
            new_price = pret_spinbox.value()

            # Actualizeaza in baza de date
            success = update_taxa(tax_id, new_durata, new_price)

            res_box = QMessageBox(self)
            set_dark_titlebar(res_box)
            if success:
                res_box.setWindowTitle("Succes")
                res_box.setText(f"Taxa a fost actualizata:\nDurata: {new_durata} min\nPret: {new_price:.2f} RON")
                res_box.exec_()
                self.handle_show_taxe()
            else:
                res_box.setWindowTitle("Eroare")
                res_box.setText("Nu s-a putut actualiza taxa in baza de date.")
                res_box.exec_()

    def _get_tax_values_for_edit(self, tax_id):
        # Preia durata si pret pentru taxa cu ID-ul specificat
        current_durata = None
        current_price = None

        for row in range(self.admin_results.rowCount()):
            id_item = self.admin_results.item(row, 0)
            if id_item and int(id_item.text()) == tax_id:
                durata_item = self.admin_results.item(row, 1)
                if durata_item:
                    current_durata = durata_item.text()
                price_item = self.admin_results.item(row, 2)
                if price_item:
                    current_price = price_item.text()
                break

        return current_durata, current_price
