from gui.utils import set_dark_titlebar
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QLineEdit, QInputDialog, QSpinBox, QDoubleSpinBox
from PyQt5.QtCore import Qt
from db import (
    show_masini,
    show_taxe,
    delete_taxa,
    delete_masina,
    add_taxa,
    update_taxa,
    count_cars_in_parking,
    fetch_subscription_plans,
    create_subscription_plan,
    update_subscription_plan,
    delete_subscription_plan,
    fetch_user_subscriptions,
    delete_user_subscription,
    fetch_users_for_admin,
    delete_user_by_id,
)
from config import MAX_PARKING_SPACES

ADD_SUBSCRIPTION_PLAN_TEXT = 'Adauga Abonament Nou'

class AdminMixin:
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

    def refresh_admin_tab(self):
        # Reincarca continutul tabului admin curent
        current_tab = getattr(self, 'current_admin_tab', 'masini')

        if hasattr(self, 'add_taxa_btn'):
            if current_tab == 'taxe':
                self.add_taxa_btn.setText('Adauga Taxa Noua')
                self.add_taxa_btn.show()
            elif current_tab == 'subscriptions':
                self.add_taxa_btn.setText(ADD_SUBSCRIPTION_PLAN_TEXT)
                self.add_taxa_btn.show()
            else:
                self.add_taxa_btn.hide()

        if current_tab == 'masini':
            self.handle_show_masini()
        elif current_tab == 'taxe':
            self.handle_show_taxe()
        elif current_tab == 'subscriptions':
            self.handle_show_subscriptions()
        elif current_tab == 'user_subscriptions':
            self.handle_show_user_subscriptions()
        elif current_tab == 'users':
            self.handle_show_users()

    def handle_add_action(self):
        # Dispatch pentru butonul de adaugare in functie de tabul activ
        current_tab = getattr(self, 'current_admin_tab', 'masini')
        if current_tab == 'taxe':
            self.handle_add_taxa()
        elif current_tab == 'subscriptions':
            self.handle_add_subscription_plan()

    def handle_show_subscriptions(self):
        # Afiseaza planurile de abonament
        if hasattr(self, 'add_taxa_btn'):
            self.add_taxa_btn.setText(ADD_SUBSCRIPTION_PLAN_TEXT)
            self.add_taxa_btn.show()

        table = self.admin_results
        try:
            rows = fetch_subscription_plans()
            if not rows:
                table.clear()
                table.setRowCount(1)
                table.setColumnCount(1)
                table.setHorizontalHeaderLabels(['Info'])
                table.setItem(0, 0, QTableWidgetItem("(Nicio inregistrare gasita in tabelul 'subscriptions')"))
                return

            headers = ['ID', 'Nume', 'Pret', 'Durata', 'Actiuni']
            table.clear()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setRowCount(len(rows))

            for r_idx, r in enumerate(rows):
                plan_id, nume, price, duration = r

                item = QTableWidgetItem(str(plan_id))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 0, item)

                item = QTableWidgetItem(str(nume) if nume else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 1, item)

                item = QTableWidgetItem(f"{float(price):.2f}" if price is not None else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 2, item)

                item = QTableWidgetItem(str(duration) if duration is not None else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 3, item)

                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setAlignment(Qt.AlignCenter)
                actions_layout.setSpacing(10)

                edit_btn = QPushButton('EDIT')
                edit_btn.setObjectName('tableActionBtn')
                edit_btn.setCursor(Qt.PointingHandCursor)
                edit_btn.setMinimumHeight(35)
                edit_btn.clicked.connect(lambda checked, pid=plan_id: self.handle_edit_subscription_plan(pid))

                delete_btn = QPushButton('DELETE')
                delete_btn.setObjectName('tableActionBtn')
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setMinimumHeight(35)
                delete_btn.clicked.connect(lambda checked, pid=plan_id: self.handle_delete_subscription_plan(pid))

                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                table.setCellWidget(r_idx, 4, actions_widget)

            for row in range(len(rows)):
                table.setRowHeight(row, 50)

            table.resizeColumnsToContents()
            table.setColumnWidth(4, 160)
        except Exception as e:
            table.clear()
            table.setRowCount(1)
            table.setColumnCount(1)
            table.setItem(0, 0, QTableWidgetItem(f"Eroare la preluarea abonamentelor: {e}"))

    def handle_show_user_subscriptions(self):
        # Afiseaza abonamentele utilizatorilor
        if hasattr(self, 'add_taxa_btn'):
            self.add_taxa_btn.hide()

        table = self.admin_results
        try:
            rows = fetch_user_subscriptions()
            if not rows:
                table.clear()
                table.setRowCount(1)
                table.setColumnCount(1)
                table.setHorizontalHeaderLabels(['Info'])
                table.setItem(0, 0, QTableWidgetItem("(Nicio inregistrare gasita in tabelul 'user_subscriptions')"))
                return

            headers = ['User_ID', 'Start_date', 'End_date', 'Plan_ID', 'Active', 'Actiuni']
            table.clear()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setRowCount(len(rows))

            for r_idx, r in enumerate(rows):
                record_id, user_id, start_date, end_date, plan_id, active = r

                item = QTableWidgetItem(str(user_id) if user_id is not None else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 0, item)

                start_str = start_date.strftime('%Y-%m-%d %H:%M:%S') if start_date else ''
                item = QTableWidgetItem(start_str)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 1, item)

                end_str = end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else ''
                item = QTableWidgetItem(end_str)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 2, item)

                item = QTableWidgetItem(str(plan_id) if plan_id is not None else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 3, item)

                item = QTableWidgetItem('Da' if active else 'Nu')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 4, item)

                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setAlignment(Qt.AlignCenter)

                delete_btn = QPushButton('DELETE')
                delete_btn.setObjectName('tableActionBtn')
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setMinimumHeight(35)
                delete_btn.clicked.connect(lambda checked, rid=record_id: self.handle_delete_user_subscription(rid))

                actions_layout.addWidget(delete_btn)
                table.setCellWidget(r_idx, 5, actions_widget)

            for row in range(len(rows)):
                table.setRowHeight(row, 50)

            table.resizeColumnsToContents()
            table.setColumnWidth(5, 120)
        except Exception as e:
            table.clear()
            table.setRowCount(1)
            table.setColumnCount(1)
            table.setItem(0, 0, QTableWidgetItem(f"Eroare la preluarea abonamentelor utilizatorilor: {e}"))

    def handle_show_users(self):
        # Afiseaza userii
        if hasattr(self, 'add_taxa_btn'):
            self.add_taxa_btn.hide()

        table = self.admin_results
        try:
            rows = fetch_users_for_admin()
            if not rows:
                table.clear()
                table.setRowCount(1)
                table.setColumnCount(1)
                table.setHorizontalHeaderLabels(['Info'])
                table.setItem(0, 0, QTableWidgetItem("(Nicio inregistrare gasita in tabelul 'users')"))
                return

            headers = ['ID', 'Nume', 'Prenume', 'Email', 'Nr_inmatriculare', 'Actiuni']
            table.clear()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setRowCount(len(rows))

            for r_idx, r in enumerate(rows):
                user_id, nume, prenume, email, numar = r

                item = QTableWidgetItem(str(user_id) if user_id is not None else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 0, item)

                item = QTableWidgetItem(str(nume) if nume else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 1, item)

                item = QTableWidgetItem(str(prenume) if prenume else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 2, item)

                item = QTableWidgetItem(str(email) if email else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 3, item)

                item = QTableWidgetItem(str(numar) if numar else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r_idx, 4, item)

                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setAlignment(Qt.AlignCenter)

                delete_btn = QPushButton('DELETE')
                delete_btn.setObjectName('tableActionBtn')
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setMinimumHeight(35)
                delete_btn.clicked.connect(lambda checked, uid=user_id: self.handle_delete_user(uid))

                actions_layout.addWidget(delete_btn)
                table.setCellWidget(r_idx, 5, actions_widget)

            for row in range(len(rows)):
                table.setRowHeight(row, 50)

            table.resizeColumnsToContents()
            table.setColumnWidth(5, 120)
        except Exception as e:
            table.clear()
            table.setRowCount(1)
            table.setColumnCount(1)
            table.setItem(0, 0, QTableWidgetItem(f"Eroare la preluarea userilor: {e}"))

    def handle_add_subscription_plan(self):
        # Adauga un plan nou de abonament
        dialog = QDialog(self)
        set_dark_titlebar(dialog)
        dialog.setWindowTitle('Adauga Abonament Nou')
        dialog.setMinimumWidth(360)

        layout = QFormLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        nume_input = QLineEdit()
        layout.addRow('Nume:', nume_input)

        price_input = QLineEdit()
        layout.addRow('Price (RON):', price_input)

        durata_input = QLineEdit()
        layout.addRow('Duration (zile):', durata_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)
        buttons.button(QDialogButtonBox.Ok).setText('OK')
        buttons.button(QDialogButtonBox.Cancel).setText('Cancel')
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec_() == QDialog.Accepted:
            try:
                nume_val = nume_input.text().strip()
                price_val = float(price_input.text().strip())
                durata_val = int(durata_input.text().strip())
                if not nume_val:
                    raise ValueError('Numele este obligatoriu')

                success = create_subscription_plan(nume_val, price_val, durata_val)

                res_box = QMessageBox(self)
                set_dark_titlebar(res_box)
                if success:
                    res_box.setWindowTitle('Succes')
                    res_box.setText('Abonamentul a fost adaugat!')
                    res_box.exec_()
                    self.handle_show_subscriptions()
                else:
                    res_box.setWindowTitle('Eroare')
                    res_box.setText('Nu s-a putut adauga abonamentul.')
                    res_box.exec_()
            except ValueError:
                warn_box = QMessageBox(self)
                set_dark_titlebar(warn_box)
                warn_box.setWindowTitle('Avertisment')
                warn_box.setText('Te rog introdu valori valide pentru nume, price si duration.')
                warn_box.exec_()

    def handle_edit_subscription_plan(self, plan_id):
        # preia valorile curente pentru planul selectat si le afiseaza intr-un dialog de editare
        current_name, current_price, current_duration = self._get_subscription_plan_values_for_edit(plan_id)

        dialog = QDialog(self)
        set_dark_titlebar(dialog)
        dialog.setWindowTitle(f'Modificare Abonament (ID: {plan_id})')
        dialog.setMinimumWidth(320)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_input = QLineEdit(current_name or '')
        form_layout.addRow('Nume nou:', name_input)

        price_spinbox = QDoubleSpinBox()
        price_spinbox.setRange(0.0, 999999.99)
        price_spinbox.setDecimals(2)
        price_spinbox.setValue(float(current_price) if current_price else 0.0)
        form_layout.addRow('Price nou (RON):', price_spinbox)

        duration_spinbox = QSpinBox()
        duration_spinbox.setRange(1, 999999)
        duration_spinbox.setValue(int(current_duration) if current_duration else 30)
        form_layout.addRow('Duration noua (zile):', duration_spinbox)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            new_name = name_input.text().strip()
            new_price = price_spinbox.value()
            new_duration = duration_spinbox.value()

            if not new_name:
                QMessageBox.warning(self, 'Avertisment', 'Numele nu poate fi gol.')
                return

            success = update_subscription_plan(plan_id, new_name, new_price, new_duration)
            res_box = QMessageBox(self)
            set_dark_titlebar(res_box)
            if success:
                res_box.setWindowTitle('Succes')
                res_box.setText(f'Abonamentul a fost actualizat:\nNume: {new_name}\nPrice: {new_price:.2f} RON\nDuration: {new_duration} zile')
                res_box.exec_()
                self.handle_show_subscriptions()
            else:
                res_box.setWindowTitle('Eroare')
                res_box.setText('Nu s-a putut actualiza abonamentul.')
                res_box.exec_()

    def _get_subscription_plan_values_for_edit(self, plan_id):
        # Preia numele, pretul si durata planului selectat
        current_name = None
        current_price = None
        current_duration = None

        for row in range(self.admin_results.rowCount()):
            id_item = self.admin_results.item(row, 0)
            if id_item and int(id_item.text()) == plan_id:
                name_item = self.admin_results.item(row, 1)
                if name_item:
                    current_name = name_item.text()
                price_item = self.admin_results.item(row, 2)
                if price_item:
                    current_price = price_item.text()
                duration_item = self.admin_results.item(row, 3)
                if duration_item:
                    current_duration = duration_item.text()
                break

        return current_name, current_price, current_duration

    def handle_delete_subscription_plan(self, plan_id):
        # Sterge un plan de abonament
        msg_box = QMessageBox(self)
        set_dark_titlebar(msg_box)
        msg_box.setWindowTitle('Confirmare')
        msg_box.setText(f'Esti sigur ca vrei sa stergi abonamentul ID {plan_id}?')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        if msg_box.exec_() == QMessageBox.Yes:
            success = delete_subscription_plan(plan_id)
            res_box = QMessageBox(self)
            set_dark_titlebar(res_box)
            if success:
                res_box.setWindowTitle('Succes')
                res_box.setText('Abonamentul a fost sters cu succes!')
                res_box.exec_()
                self.handle_show_subscriptions()
            else:
                res_box.setWindowTitle('Eroare')
                res_box.setText('Nu s-a putut sterge abonamentul din baza de date.')
                res_box.exec_()

    def handle_delete_user_subscription(self, record_id):
        # Sterge un abonament al unui user
        msg_box = QMessageBox(self)
        set_dark_titlebar(msg_box)
        msg_box.setWindowTitle('Confirmare')
        msg_box.setText(f'Esti sigur ca vrei sa stergi abonamentul userului cu ID {record_id}?')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        if msg_box.exec_() == QMessageBox.Yes:
            success = delete_user_subscription(record_id)
            res_box = QMessageBox(self)
            set_dark_titlebar(res_box)
            if success:
                res_box.setWindowTitle('Succes')
                res_box.setText('Abonamentul userului a fost sters cu succes!')
                res_box.exec_()
                self.handle_show_user_subscriptions()
            else:
                res_box.setWindowTitle('Eroare')
                res_box.setText('Nu s-a putut sterge abonamentul userului.')
                res_box.exec_()

    def handle_delete_user(self, user_id):
        # Sterge un user
        msg_box = QMessageBox(self)
        set_dark_titlebar(msg_box)
        msg_box.setWindowTitle('Confirmare')
        msg_box.setText(f'Esti sigur ca vrei sa stergi userul ID {user_id}?')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        if msg_box.exec_() == QMessageBox.Yes:
            success = delete_user_by_id(user_id)
            res_box = QMessageBox(self)
            set_dark_titlebar(res_box)
            if success:
                res_box.setWindowTitle('Succes')
                res_box.setText('Userul a fost sters cu succes!')
                res_box.exec_()
                self.handle_show_users()
            else:
                res_box.setWindowTitle('Eroare')
                res_box.setText('Nu s-a putut sterge userul din baza de date.')
                res_box.exec_()

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


