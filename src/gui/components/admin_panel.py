from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLabel, QPushButton, QTabWidget, QVBoxLayout, QWidget

from gui.components.tables import build_admin_table


def create_admin_panel(window):
    admin_panel = QWidget()
    admin_layout = QVBoxLayout(admin_panel)
    admin_layout.setContentsMargins(0, 0, 0, 0)
    admin_layout.setSpacing(20)

    window.car_count_label = QLabel()
    window.car_count_label.setObjectName("carCountLabel")
    window.car_count_label.setAlignment(Qt.AlignCenter)
    window.update_car_count()

    window.stats_timer = QTimer()
    window.stats_timer.timeout.connect(window.update_car_count)
    window.stats_timer.start(5000)
    admin_layout.addWidget(window.car_count_label)

    window.admin_tabs = QTabWidget()
    window.admin_tabs.currentChanged.connect(window.on_admin_tab_changed)

    _add_admin_tab(window, "admin_masini_table", "Masini")
    _add_admin_tab(window, "admin_taxe_table", "Taxe")
    _add_admin_tab(window, "admin_subscriptions_table", "Tip subscriptii")
    _add_admin_tab(window, "admin_user_subscriptions_table", "Abonamente")
    _add_admin_tab(window, "admin_users_table", "Useri")

    admin_layout.addWidget(window.admin_tabs)

    window.add_taxa_btn = QPushButton("Adauga Taxa Noua")
    window.add_taxa_btn.setObjectName("actionBtnActive")
    window.add_taxa_btn.setCursor(Qt.PointingHandCursor)
    window.add_taxa_btn.setMinimumHeight(40)
    window.add_taxa_btn.clicked.connect(window.handle_add_action)
    admin_layout.addWidget(window.add_taxa_btn)
    window.add_taxa_btn.hide()

    window.admin_results = window.admin_masini_table
    window.current_admin_tab = "masini"
    window.refresh_admin_tab()

    return admin_panel


def _add_admin_tab(window, table_attr, title):
    table = build_admin_table()
    setattr(window, table_attr, table)

    tab = QWidget()
    tab_layout = QVBoxLayout(tab)
    tab_layout.setContentsMargins(0, 0, 0, 0)
    tab_layout.addWidget(table)
    window.admin_tabs.addTab(tab, title)
