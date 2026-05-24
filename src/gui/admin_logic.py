from gui.utils import set_dark_titlebar
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QLineEdit, QInputDialog, QSpinBox, QDoubleSpinBox
from PyQt5.QtCore import Qt
from db import show_masini, show_taxe, delete_taxa, delete_masina, add_taxa, update_taxa, count_cars_in_parking

class AdminMixin:
    def handle_show_masini(self):
        # Handler pentru butonul Masini - afiseaza toate inregistrarile din tabelul masini
        if hasattr(self, 'add_taxa_btn'):
            self.add_taxa_btn.hide()
            
        try:
            # Update car count
            self.update_car_count()
            
            rows = show_masini()
            if not rows:
                self.admin_results.clear()
                self.admin_results.setRowCount(1)
                self.admin_results.setColumnCount(1)
                self.admin_results.setHorizontalHeaderLabels(["Info"])
                self.admin_results.setItem(0, 0, QTableWidgetItem("(Nicio inregistrare gasita in tabelul 'masini')"))
                return

            # Set columns
            headers = ["Numar_inmatriculare", "Cod", "Ora_intrare", "Ora_platire", "Actiuni"]
            self.admin_results.clear()
            self.admin_results.setColumnCount(len(headers))
            self.admin_results.setHorizontalHeaderLabels(headers)
            self.admin_results.setRowCount(len(rows))

            for r_idx, r in enumerate(rows):
                numar, cod, ora_i, ora_p = r
                
                # Column 0: Numar_inmatriculare
                item = QTableWidgetItem(str(numar) if numar else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 0, item)
                
                # Column 1: Cod
                item = QTableWidgetItem(str(cod) if cod else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 1, item)
                
                # Column 2: Ora_intrare (format YYYY-MM-DD HH:MM:SS)
                time_str = ora_i.strftime("%Y-%m-%d %H:%M:%S") if ora_i else ""
                item = QTableWidgetItem(time_str)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 2, item)
                
                # Column 3: Ora_platire (format YYYY-MM-DD HH:MM:SS)
                time_str = ora_p.strftime("%Y-%m-%d %H:%M:%S") if ora_p else ""
                item = QTableWidgetItem(time_str)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 3, item)
                
                # Column 4: Actiuni (Buton DELETE)
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
                self.admin_results.setCellWidget(r_idx, 4, actions_widget)

            for row in range(len(rows)):
                self.admin_results.setRowHeight(row, 50)

            self.admin_results.resizeColumnsToContents()
            self.admin_results.setColumnWidth(4, 120)

        except Exception as e:
            self.admin_results.clear()
            self.admin_results.setRowCount(1)
            self.admin_results.setColumnCount(1)
            self.admin_results.setItem(0, 0, QTableWidgetItem(f"Eroare la preluarea masinilor: {e}"))

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
                # ID column
                item_id = QTableWidgetItem(str(tid))
                item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 0, item_id)
                
                # Durata column
                item_durata = QTableWidgetItem(str(durata))
                item_durata.setFlags(item_durata.flags() & ~Qt.ItemIsEditable)
                self.admin_results.setItem(r_idx, 1, item_durata)
                
                # Pret column
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

    def handle_add_taxa(self):
        # Handler pentru butonul ADD - permite adaugarea unei noi taxe.
        from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        set_dark_titlebar(dialog)
        dialog.setWindowTitle("Adauga Taxa Noua")
        dialog.setMinimumWidth(350)
        
        layout = QFormLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        durata_input = QLineEdit()
        durata_input.setPlaceholderText("ex: 60 (in minute)")
        layout.addRow("Durata (minute):", durata_input)
        
        pret_input = QLineEdit()
        pret_input.setPlaceholderText("ex: 15.50")
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
        #Handler pentru butonul EDIT - permite modificarea duratei si a pretului pentru o taxa
        
        # Obtine pretul curent si durata din tabel
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
        
        # Creare dialog personalizat
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

    def update_car_count(self):
        # Actualizeaza label-ul cu numarul de masini in parcare
        try:
            count = count_cars_in_parking()
            self.car_count_label.setText(f" Masini in parcare: {count}")
        except Exception as e:
            self.car_count_label.setText(f" Eroare la numarare: {e}")


