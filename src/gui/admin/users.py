from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QMessageBox, QPushButton, QTableWidgetItem, QWidget

from db import delete_user_by_id, fetch_users_for_admin
from gui.window_utils import set_dark_titlebar


class AdminUsersMixin:
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
