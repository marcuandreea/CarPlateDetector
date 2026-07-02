from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton


def create_top_bar(window):
    top_bar = QFrame()
    top_bar.setObjectName("topBar")
    top_bar.setFixedHeight(60)
    top_layout = QHBoxLayout(top_bar)
    top_layout.setContentsMargins(0, 0, 0, 0)

    top_layout.addStretch()

    window.user_mode_btn = QPushButton("User Mode")
    window.user_mode_btn.setObjectName("modeBtnActive")
    window.user_mode_btn.clicked.connect(lambda: window.switch_mode("user"))
    window.user_mode_btn.setCursor(Qt.PointingHandCursor)
    top_layout.addWidget(window.user_mode_btn)

    window.admin_mode_btn = QPushButton("Admin Mode")
    window.admin_mode_btn.setObjectName("modeBtn")
    window.admin_mode_btn.clicked.connect(lambda: window.switch_mode("admin"))
    window.admin_mode_btn.setCursor(Qt.PointingHandCursor)
    top_layout.addWidget(window.admin_mode_btn)

    top_layout.addStretch()
    return top_bar
