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

from db import (
    create_subscription_plan,
    delete_subscription_plan,
    delete_user_subscription,
    fetch_subscription_plans,
    fetch_user_subscriptions,
    update_subscription_plan,
)
from gui.window_utils import set_dark_titlebar


class AdminSubscriptionsMixin:
    def handle_show_subscriptions(self):
        # Afiseaza planurile de abonament
        if hasattr(self, 'add_taxa_btn'):
            self.add_taxa_btn.setText("Adauga Abonament Nou")
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
