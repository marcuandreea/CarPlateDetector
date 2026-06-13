import sys
import os
import ctypes
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy,
                            QWidget, QPushButton, QLabel, QGridLayout,
                            QFrame, QMessageBox, QCheckBox, QLineEdit, QTableWidget, QTableWidgetItem, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

# Adaugam calea catre directorul src pentru a putea importa modulele
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gui.utils import QRCodeDecoderThread

from gui.admin_logic import AdminMixin
from gui.user_logic import UserLogicMixin

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
        from gui.utils import set_dark_titlebar
        set_dark_titlebar(self)
        
        self.load_stylesheet()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # TOP BAR: Mode Selector (User/Admin)
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(60)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        top_layout.addStretch()
        
        self.user_mode_btn = QPushButton("User Mode")
        self.user_mode_btn.setObjectName("modeBtnActive")
        self.user_mode_btn.clicked.connect(lambda: self.switch_mode("user"))
        self.user_mode_btn.setCursor(Qt.PointingHandCursor)
        top_layout.addWidget(self.user_mode_btn)
        
        self.admin_mode_btn = QPushButton("Admin Mode")
        self.admin_mode_btn.setObjectName("modeBtn")
        self.admin_mode_btn.clicked.connect(lambda: self.switch_mode("admin"))
        self.admin_mode_btn.setCursor(Qt.PointingHandCursor)
        top_layout.addWidget(self.admin_mode_btn)
        
        top_layout.addStretch()
        
        main_layout.addWidget(top_bar)
        
        # CONTENT AREA
        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 10, 30, 30)
        content_layout.setSpacing(0)
        
        self.panels_container = QWidget()
        panels_layout = QVBoxLayout(self.panels_container)
        panels_layout.setContentsMargins(0, 0, 0, 0)
        panels_layout.setSpacing(0)
        
        # USER PANEL 
        self.user_panel = QWidget()
        user_panel_layout = QVBoxLayout(self.user_panel)
        user_panel_layout.setContentsMargins(0, 0, 0, 0)
        user_panel_layout.setSpacing(0)
        
        # Action Buttons (Enter/Pay/Exit)
        action_buttons_frame = QFrame()
        action_buttons_layout = QHBoxLayout(action_buttons_frame)
        action_buttons_layout.setContentsMargins(0, 0, 0, 0)
        action_buttons_layout.addStretch()
        
        self.enter_btn = QPushButton("Enter Parking")
        self.enter_btn.setObjectName("actionBtnActive")
        self.enter_btn.clicked.connect(lambda: self.switch_action("enter"))
        self.enter_btn.setCursor(Qt.PointingHandCursor)
        action_buttons_layout.addWidget(self.enter_btn)
        
        self.pay_btn = QPushButton("Pay")
        self.pay_btn.setObjectName("actionBtn")
        self.pay_btn.clicked.connect(lambda: self.switch_action("pay"))
        self.pay_btn.setCursor(Qt.PointingHandCursor)
        action_buttons_layout.addWidget(self.pay_btn)
        
        self.exit_btn = QPushButton("Exit Parking")
        self.exit_btn.setObjectName("actionBtn")
        self.exit_btn.clicked.connect(lambda: self.switch_action("exit"))
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        action_buttons_layout.addWidget(self.exit_btn)
        
        action_buttons_layout.addStretch()
        user_panel_layout.addWidget(action_buttons_frame)
        
        self.action_content = QWidget()
        action_content_layout = QVBoxLayout(self.action_content)
        action_content_layout.setContentsMargins(0, 0, 0, 0)
        action_content_layout.setSpacing(0)
        
        # ENTER PARKING CONTENT
        self.enter_content = QWidget()
        enter_layout = QVBoxLayout(self.enter_content)
        enter_layout.setContentsMargins(0, 0, 0, 0)
        enter_layout.setSpacing(5)
        
        # Titlu Intrare
        enter_title = QLabel("Intrare")
        enter_title.setAlignment(Qt.AlignCenter)
        enter_title.setObjectName("sectionTitle")
        enter_layout.addWidget(enter_title)
        
        # Label locuri disponibile
        self.available_spots_label = QLabel("")
        self.available_spots_label.setAlignment(Qt.AlignCenter)
        self.available_spots_label.setObjectName("availableSpotsLabel")
        enter_layout.addWidget(self.available_spots_label)
        
        self.image_frame = QFrame()
        self.image_frame.setObjectName("imageFrame")
        self.image_frame.setFixedHeight(394) 
        
        image_frame_layout = QGridLayout(self.image_frame)
        image_frame_layout.setContentsMargins(0, 0, 0, 0)
        image_frame_layout.setSpacing(0)
        
        self.image_display = QLabel()
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setScaledContents(False)
        self.image_display.setObjectName("imageDisplay")
        
        image_frame_layout.addWidget(self.image_display, 0, 0)
        self.image_display.show()

        enter_layout.addWidget(self.image_frame)
        enter_layout.addSpacing(10)

        # Frame pentru butoanele de actiune 
        self.enter_action_frame = QFrame()
        enter_action_layout = QHBoxLayout(self.enter_action_frame)
        enter_action_layout.setContentsMargins(0, 0, 0, 0)
        enter_action_layout.addStretch()
        
        # Debug mode checkbox 
        self.debug_checkbox = QCheckBox("Enable Debug Mode (save images & logs)")
        self.debug_checkbox.setChecked(False)
        self.debug_checkbox.toggled.connect(self.on_debug_toggled)
        enter_action_layout.addWidget(self.debug_checkbox)
        
        enter_action_layout.addSpacing(12)

        self.entry_live_btn = QPushButton("Live Camera")
        self.entry_live_btn.setObjectName("actionBtnActive")
        self.entry_live_btn.setCursor(Qt.PointingHandCursor)
        self.entry_live_btn.clicked.connect(self.select_entry_source_live)
        enter_action_layout.addWidget(self.entry_live_btn)

        self.entry_video_btn = QPushButton("Upload Video")
        self.entry_video_btn.setObjectName("actionBtn")
        self.entry_video_btn.setCursor(Qt.PointingHandCursor)
        self.entry_video_btn.clicked.connect(self.select_entry_source_video)
        enter_action_layout.addWidget(self.entry_video_btn)

        enter_action_layout.addSpacing(12)
        
        enter_action_layout.addStretch()
        enter_layout.addWidget(self.enter_action_frame)

        self.result_panel = QFrame()
        self.result_panel.setStyleSheet("background: transparent;")
        result_layout = QHBoxLayout(self.result_panel)
        result_layout.setContentsMargins(0, 10, 0, 0)
        result_layout.addStretch()

        self.result_label = QLabel("")
        self.result_label.setObjectName("resultLabel")
        result_layout.addWidget(self.result_label)

        result_layout.addStretch()
        self.result_panel.setVisible(False)
        enter_layout.addWidget(self.result_panel)
        
        enter_layout.addStretch()
        
        action_content_layout.addWidget(self.enter_content)

        # PAY CONTENT 
        self.pay_content = QWidget()
        pay_layout = QVBoxLayout(self.pay_content)
        pay_layout.setContentsMargins(0, 0, 0, 0)
        pay_layout.setSpacing(10)
        
        # Titlu Plata
        pay_title = QLabel("Plata")
        pay_title.setAlignment(Qt.AlignCenter)
        pay_title.setObjectName("sectionTitle")
        pay_layout.addWidget(pay_title)
        
        # Preview live camera pentru Plata
        self.pay_qr_preview = QLabel()
        self.pay_qr_preview.setObjectName("qrPreview")
        self.pay_qr_preview.setAlignment(Qt.AlignCenter)
        self.pay_qr_preview.setMinimumHeight(394)
        self.pay_qr_preview.setFixedHeight(394)
        self.pay_qr_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.pay_qr_preview.hide()
        pay_layout.addWidget(self.pay_qr_preview)
        
        # Input cod 
        self.pay_code_input = QLineEdit()
        self.pay_code_input.setPlaceholderText("Codul unic din QR va aparea aici...")
        self.pay_code_input.setObjectName("codeInput")
        self.pay_code_input.setReadOnly(True)
        self.pay_code_input.setAlignment(Qt.AlignCenter)
        self.pay_code_input.hide()  # Ascuns pana avem poza
        pay_layout.addWidget(self.pay_code_input)
        
        # Label pentru mesaje de status
        self.pay_status_label = QLabel("")
        self.pay_status_label.setObjectName("resultLabel")
        self.pay_status_label.setAlignment(Qt.AlignCenter)
        self.pay_status_label.hide()
        pay_layout.addWidget(self.pay_status_label)
        
        # Afisare informatii plata
        self.pay_info_frame = QFrame()
        self.pay_info_frame.setObjectName("payInfoFrame")
        pay_info_layout = QVBoxLayout(self.pay_info_frame)
        pay_info_layout.setContentsMargins(20, 20, 20, 20)
        pay_info_layout.setSpacing(15)
        
        self.pay_minutes_label = QLabel("")
        self.pay_minutes_label.setObjectName("payMinutesLabel")
        self.pay_minutes_label.setAlignment(Qt.AlignCenter)
        pay_info_layout.addWidget(self.pay_minutes_label)
        
        self.pay_amount_label = QLabel("")
        self.pay_amount_label.setObjectName("payAmountLabel")
        self.pay_amount_label.setAlignment(Qt.AlignCenter)
        pay_info_layout.addWidget(self.pay_amount_label)
        
        self.pay_confirm_btn = QPushButton("Confirma Plata")
        self.pay_confirm_btn.setObjectName("payConfirmBtn")
        self.pay_confirm_btn.setCursor(Qt.PointingHandCursor)
        self.pay_confirm_btn.setMinimumHeight(45)
        self.pay_confirm_btn.clicked.connect(self.handle_confirm_payment)
        pay_info_layout.addWidget(self.pay_confirm_btn)
        
        pay_layout.addWidget(self.pay_info_frame)
        self.pay_info_frame.hide()
        
        pay_layout.addStretch()
        
        action_content_layout.addWidget(self.pay_content)
        self.pay_content.hide()
        
        # EXIT CONTENT 
        self.exit_content = QWidget()
        exit_layout = QVBoxLayout(self.exit_content)
        exit_layout.setContentsMargins(0, 0, 0, 0)
        exit_layout.setSpacing(10)
        
        # Titlu Iesire
        exit_title = QLabel("Iesire")
        exit_title.setAlignment(Qt.AlignCenter)
        exit_title.setObjectName("sectionTitle")
        exit_layout.addWidget(exit_title)

        # Preview live camera pentru Iesire
        self.leave_qr_preview = QLabel()
        self.leave_qr_preview.setObjectName("qrPreview")
        self.leave_qr_preview.setAlignment(Qt.AlignCenter)
        self.leave_qr_preview.setMinimumHeight(394)
        self.leave_qr_preview.setFixedHeight(394)
        self.leave_qr_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.leave_qr_preview.hide()
        exit_layout.addWidget(self.leave_qr_preview)

        # Input cod 
        self.leave_code_input = QLineEdit()
        self.leave_code_input.setPlaceholderText("Codul unic din QR va aparea aici...")
        self.leave_code_input.setObjectName("codeInput")
        self.leave_code_input.setReadOnly(True)
        self.leave_code_input.setAlignment(Qt.AlignCenter)
        self.leave_code_input.hide()
        exit_layout.addWidget(self.leave_code_input)
        
        # Buton Leave
        leave_button_layout = QHBoxLayout()
        leave_button_layout.addStretch()
        self.leave_execute_btn = QPushButton("Leave")
        self.leave_execute_btn.setObjectName("primaryBtn")
        self.leave_execute_btn.setMinimumHeight(45)
        self.leave_execute_btn.clicked.connect(self.handle_leave_parking)
        self.leave_execute_btn.hide()
        leave_button_layout.addWidget(self.leave_execute_btn)
        leave_button_layout.addStretch()
        exit_layout.addLayout(leave_button_layout)
        
        # Label pentru mesaje de status
        self.leave_status_label = QLabel("")
        self.leave_status_label.setObjectName("resultLabel")
        self.leave_status_label.setAlignment(Qt.AlignCenter)
        self.leave_status_label.hide()
        exit_layout.addWidget(self.leave_status_label)
        
        exit_layout.addStretch()
        
        action_content_layout.addWidget(self.exit_content)
        self.exit_content.hide()
        
        user_panel_layout.addWidget(self.action_content)
        panels_layout.addWidget(self.user_panel)
        
        # ADMIN PANEL 
        self.admin_panel = QWidget()
        admin_layout = QVBoxLayout(self.admin_panel)
        admin_layout.setContentsMargins(0, 0, 0, 0)
        admin_layout.setSpacing(20)

        self.car_count_label = QLabel()
        self.car_count_label.setObjectName("carCountLabel")
        self.car_count_label.setAlignment(Qt.AlignCenter)
        self.update_car_count()

        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_car_count)
        self.stats_timer.start(5000)
        admin_layout.addWidget(self.car_count_label)

        self.admin_tabs = QTabWidget()
        self.admin_tabs.currentChanged.connect(self.on_admin_tab_changed)

        # Functie pentru a construi tabelele din taburile admin cu setari comune
        def build_admin_table():
            table = QTableWidget()
            table.setObjectName("adminResults")
            table.setMinimumHeight(300)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(True)
            table.horizontalHeader().setStretchLastSection(True)
            table.verticalHeader().setVisible(False)
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            return table

        self.admin_masini_table = build_admin_table()
        masini_tab = QWidget()
        masini_layout = QVBoxLayout(masini_tab)
        masini_layout.setContentsMargins(0, 0, 0, 0)
        masini_layout.addWidget(self.admin_masini_table)
        self.admin_tabs.addTab(masini_tab, "Masini")

        self.admin_taxe_table = build_admin_table()
        taxe_tab = QWidget()
        taxe_layout = QVBoxLayout(taxe_tab)
        taxe_layout.setContentsMargins(0, 0, 0, 0)
        taxe_layout.addWidget(self.admin_taxe_table)
        self.admin_tabs.addTab(taxe_tab, "Taxe")

        self.admin_subscriptions_table = build_admin_table()
        subscriptions_tab = QWidget()
        subscriptions_layout = QVBoxLayout(subscriptions_tab)
        subscriptions_layout.setContentsMargins(0, 0, 0, 0)
        subscriptions_layout.addWidget(self.admin_subscriptions_table)
        self.admin_tabs.addTab(subscriptions_tab, "Abonamente")

        self.admin_user_subscriptions_table = build_admin_table()
        user_subscriptions_tab = QWidget()
        user_subscriptions_layout = QVBoxLayout(user_subscriptions_tab)
        user_subscriptions_layout.setContentsMargins(0, 0, 0, 0)
        user_subscriptions_layout.addWidget(self.admin_user_subscriptions_table)
        self.admin_tabs.addTab(user_subscriptions_tab, "Abonamente Useri")

        self.admin_users_table = build_admin_table()
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        users_layout.setContentsMargins(0, 0, 0, 0)
        users_layout.addWidget(self.admin_users_table)
        self.admin_tabs.addTab(users_tab, "Users")

        admin_layout.addWidget(self.admin_tabs)

        self.add_taxa_btn = QPushButton("Adauga Taxa Noua")
        self.add_taxa_btn.setObjectName("actionBtnActive")
        self.add_taxa_btn.setCursor(Qt.PointingHandCursor)
        self.add_taxa_btn.setMinimumHeight(40)
        self.add_taxa_btn.clicked.connect(self.handle_add_action)
        admin_layout.addWidget(self.add_taxa_btn)
        self.add_taxa_btn.hide()

        self.admin_results = self.admin_masini_table
        self.current_admin_tab = "masini"
        self.refresh_admin_tab()

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
