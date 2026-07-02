import ctypes
import os
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout, QWidget

# Adaugam calea catre directorul src pentru a putea importa modulele
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from gui.components import create_admin_panel, create_top_bar, create_user_panel
from gui.admin import AdminMixin
from gui.user import UserLogicMixin
from gui.window_utils import set_dark_titlebar


class ParkingManagementGUI(QMainWindow, AdminMixin, UserLogicMixin):
    # Interfata grafica pentru sistemul de management parcare

    def __init__(self):
        super().__init__()
        self.current_mode = "user"
        self.current_action = "enter"
        self.entry_source = "live"

        # Timer pentru resetare dupa 10 secunde
        self.reset_timer = QTimer()
        self.reset_timer.setSingleShot(True)  # Se executa o singura data
        self.reset_timer.timeout.connect(self.reset_interface)

        self.init_ui()

        if hasattr(self, "start_entry_live_scanner") and self.entry_source == "live":
            self.start_entry_live_scanner()

    def init_ui(self):
        # Initializeaza interfata utilizator
        self.setWindowTitle("Parking Management System - License Plate Recognition")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)

        # Seteaza titlebar-ul in Dark Mode
        set_dark_titlebar(self)

        self.load_stylesheet()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(create_top_bar(self))

        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 10, 30, 0)
        content_layout.setSpacing(0)

        self.panels_container = QWidget()
        panels_layout = QVBoxLayout(self.panels_container)
        panels_layout.setContentsMargins(0, 0, 0, 0)
        panels_layout.setSpacing(0)

        self.user_panel = create_user_panel(self)
        panels_layout.addWidget(self.user_panel)

        self.admin_panel = create_admin_panel(self)
        panels_layout.addWidget(self.admin_panel)
        self.admin_panel.hide()

        content_layout.addWidget(self.panels_container)
        main_layout.addWidget(content_area)

    def load_stylesheet(self):
        # Incarca stylesheet-ul din fisierul CSS
        css_path = os.path.join(os.path.dirname(__file__), "styles.css")
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except Exception as ex:
            print(f"Eroare la incarcarea CSS: {ex}")
            self.setStyleSheet("QMainWindow { background-color: #1e1e1e; }")

    def switch_mode(self, mode):
        # Schimba intre User Mode si Admin Mode
        if self.current_mode == mode:
            return

        self.current_mode = mode

        if mode == "user":
            self.user_mode_btn.setObjectName("modeBtnActive")
            self.admin_mode_btn.setObjectName("modeBtn")
            self.user_panel.show()
            self.admin_panel.hide()
        else:
            self.user_mode_btn.setObjectName("modeBtn")
            self.admin_mode_btn.setObjectName("modeBtnActive")
            self.user_panel.hide()
            self.admin_panel.show()

        self.user_mode_btn.style().unpolish(self.user_mode_btn)
        self.user_mode_btn.style().polish(self.user_mode_btn)
        self.admin_mode_btn.style().unpolish(self.admin_mode_btn)
        self.admin_mode_btn.style().polish(self.admin_mode_btn)

    def switch_action(self, action):
        # Schimba intre Enter/Pay/Exit in User Mode
        if self.current_action == action:
            return

        self._stop_user_scanners()
        self.current_action = action

        self._set_action_button_state(action)
        self._show_action_content(action)
        self._reset_action_state(action)

    def _stop_user_scanners(self):
        if hasattr(self, "stop_qr_scanner"):
            self.stop_qr_scanner()
        if hasattr(self, "stop_entry_live_scanner"):
            self.stop_entry_live_scanner()

    def _set_action_button_state(self, action):
        self.enter_btn.setObjectName("actionBtnActive" if action == "enter" else "actionBtn")
        self.pay_btn.setObjectName("actionBtnActive" if action == "pay" else "actionBtn")
        self.exit_btn.setObjectName("actionBtnActive" if action == "exit" else "actionBtn")

        for btn in [self.enter_btn, self.pay_btn, self.exit_btn]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _show_action_content(self, action):
        self.enter_content.setVisible(action == "enter")
        self.pay_content.setVisible(action == "pay")
        self.exit_content.setVisible(action == "exit")

    def _reset_action_state(self, action):
        if action == "enter":
            if hasattr(self, "start_entry_live_scanner") and getattr(self, "entry_source", "live") == "live":
                self.start_entry_live_scanner()
        elif action == "pay":
            self.pay_qr_preview.hide()
            self.pay_code_input.clear()
            self.pay_code_input.hide()
            self.pay_status_label.hide()
            self.pay_info_frame.hide()
            if hasattr(self, 'pending_payment_code'):
                self.pending_payment_code = None
            if hasattr(self, "start_qr_scanner_for_pay"):
                self.start_qr_scanner_for_pay()
        elif action == "exit":
            self.leave_qr_preview.hide()
            self.leave_code_input.clear()
            self.leave_code_input.hide()
            self.leave_execute_btn.hide()
            self.leave_status_label.hide()
            if hasattr(self, "start_qr_scanner_for_leave"):
                self.start_qr_scanner_for_leave()

    def on_admin_tab_changed(self, index):
        # Sincronizeaza tabelul curent si reface continutul la schimbarea tabului
        tab_map = {
            0: ("masini", "admin_masini_table"),
            1: ("taxe", "admin_taxe_table"),
            2: ("subscriptions", "admin_subscriptions_table"),
            3: ("user_subscriptions", "admin_user_subscriptions_table"),
            4: ("users", "admin_users_table"),
        }

        current_tab, table_attr = tab_map.get(index, ("masini", "admin_masini_table"))
        current_table = getattr(self, table_attr, None)
        if current_table is None:
            return
        self.current_admin_tab = current_tab
        self.admin_results = current_table

        if hasattr(self, "refresh_admin_tab"):
            self.refresh_admin_tab()


def main():
    # Functia principala pentru pornirea interfetei GUI
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Setare iconita atat pe aplicatie (taskbar/dialoguri), cat si pe fereastra principala
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'parking.ico'))

    # Adaugare ID de aplicatie pentru ca Windows Taskbar sa retina iconita in mod consecvent
    if sys.platform == 'win32':
        myappid = 'mycompany.myproduct.subproduct.version' # ID arbitrar pentru aplicatie
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)

    window = ParkingManagementGUI()
    window.setWindowIcon(app_icon)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
