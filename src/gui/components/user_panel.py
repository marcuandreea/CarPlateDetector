from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def create_user_panel(window):
    user_panel = QWidget()
    user_panel_layout = QVBoxLayout(user_panel)
    user_panel_layout.setContentsMargins(0, 0, 0, 0)
    user_panel_layout.setSpacing(0)

    action_buttons_frame = QFrame()
    action_buttons_layout = QHBoxLayout(action_buttons_frame)
    action_buttons_layout.setContentsMargins(0, 0, 0, 0)
    action_buttons_layout.addStretch()

    window.enter_btn = QPushButton("Enter Parking")
    window.enter_btn.setObjectName("actionBtnActive")
    window.enter_btn.clicked.connect(lambda: window.switch_action("enter"))
    window.enter_btn.setCursor(Qt.PointingHandCursor)
    action_buttons_layout.addWidget(window.enter_btn)

    window.pay_btn = QPushButton("Pay")
    window.pay_btn.setObjectName("actionBtn")
    window.pay_btn.clicked.connect(lambda: window.switch_action("pay"))
    window.pay_btn.setCursor(Qt.PointingHandCursor)
    action_buttons_layout.addWidget(window.pay_btn)

    window.exit_btn = QPushButton("Exit Parking")
    window.exit_btn.setObjectName("actionBtn")
    window.exit_btn.clicked.connect(lambda: window.switch_action("exit"))
    window.exit_btn.setCursor(Qt.PointingHandCursor)
    action_buttons_layout.addWidget(window.exit_btn)

    action_buttons_layout.addStretch()
    user_panel_layout.addWidget(action_buttons_frame)

    window.action_content = QWidget()
    action_content_layout = QVBoxLayout(window.action_content)
    action_content_layout.setContentsMargins(0, 0, 0, 0)
    action_content_layout.setSpacing(0)

    _add_enter_content(window, action_content_layout)
    _add_pay_content(window, action_content_layout)
    _add_exit_content(window, action_content_layout)

    user_panel_layout.addWidget(window.action_content)
    return user_panel


def _add_enter_content(window, action_content_layout):
    window.enter_content = QWidget()
    enter_layout = QVBoxLayout(window.enter_content)
    enter_layout.setContentsMargins(0, 0, 0, 0)
    enter_layout.setSpacing(5)

    enter_title = QLabel("Intrare")
    enter_title.setAlignment(Qt.AlignCenter)
    enter_title.setObjectName("sectionTitle")
    enter_layout.addWidget(enter_title)

    window.available_spots_label = QLabel("")
    window.available_spots_label.setAlignment(Qt.AlignCenter)
    window.available_spots_label.setObjectName("availableSpotsLabel")
    enter_layout.addWidget(window.available_spots_label)

    window.image_frame = QFrame()
    window.image_frame.setObjectName("imageFrame")
    window.image_frame.setFixedHeight(394)

    image_frame_layout = QGridLayout(window.image_frame)
    image_frame_layout.setContentsMargins(0, 0, 0, 0)
    image_frame_layout.setSpacing(0)

    window.image_display = QLabel()
    window.image_display.setAlignment(Qt.AlignCenter)
    window.image_display.setScaledContents(False)
    window.image_display.setObjectName("imageDisplay")

    image_frame_layout.addWidget(window.image_display, 0, 0)
    window.image_display.show()

    enter_layout.addWidget(window.image_frame)
    enter_layout.addSpacing(10)

    window.enter_action_frame = QFrame()
    enter_action_layout = QHBoxLayout(window.enter_action_frame)
    enter_action_layout.setContentsMargins(0, 0, 0, 0)
    enter_action_layout.addStretch()

    window.debug_checkbox = QCheckBox("Enable Debug Mode (save images & logs)")
    window.debug_checkbox.setChecked(False)
    window.debug_checkbox.toggled.connect(window.on_debug_toggled)
    enter_action_layout.addWidget(window.debug_checkbox)

    enter_action_layout.addSpacing(12)

    window.entry_live_btn = QPushButton("Live Camera")
    window.entry_live_btn.setObjectName("actionBtnActive")
    window.entry_live_btn.setCursor(Qt.PointingHandCursor)
    window.entry_live_btn.clicked.connect(window.select_entry_source_live)
    enter_action_layout.addWidget(window.entry_live_btn)

    window.entry_video_btn = QPushButton("Upload Video")
    window.entry_video_btn.setObjectName("actionBtn")
    window.entry_video_btn.setCursor(Qt.PointingHandCursor)
    window.entry_video_btn.clicked.connect(window.select_entry_source_video)
    enter_action_layout.addWidget(window.entry_video_btn)

    enter_action_layout.addSpacing(12)

    enter_action_layout.addStretch()
    enter_layout.addWidget(window.enter_action_frame)

    window.result_panel = QFrame()
    window.result_panel.setStyleSheet("background: transparent;")
    result_layout = QHBoxLayout(window.result_panel)
    result_layout.setContentsMargins(0, 165, 0, 0)
    result_layout.addStretch()

    window.result_label = QLabel("")
    window.result_label.setObjectName("resultLabel")
    result_layout.addWidget(window.result_label)

    result_layout.addStretch()
    window.result_panel.setVisible(False)

    enter_layout.addWidget(window.result_panel)
    enter_layout.addStretch()

    action_content_layout.addWidget(window.enter_content)


def _add_pay_content(window, action_content_layout):
    window.pay_content = QWidget()
    pay_layout = QVBoxLayout(window.pay_content)
    pay_layout.setContentsMargins(0, 0, 0, 0)
    pay_layout.setSpacing(10)

    pay_title = QLabel("Plata")
    pay_title.setAlignment(Qt.AlignCenter)
    pay_title.setObjectName("sectionTitle")
    pay_layout.addWidget(pay_title)

    window.pay_qr_preview = QLabel()
    window.pay_qr_preview.setObjectName("qrPreview")
    window.pay_qr_preview.setAlignment(Qt.AlignCenter)
    window.pay_qr_preview.setMinimumHeight(394)
    window.pay_qr_preview.setFixedHeight(394)
    window.pay_qr_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    window.pay_qr_preview.hide()
    pay_layout.addWidget(window.pay_qr_preview)

    window.pay_code_input = QLineEdit()
    window.pay_code_input.setPlaceholderText("Codul unic din QR va aparea aici...")
    window.pay_code_input.setObjectName("codeInput")
    window.pay_code_input.setReadOnly(True)
    window.pay_code_input.setAlignment(Qt.AlignCenter)
    window.pay_code_input.hide()
    pay_layout.addWidget(window.pay_code_input)

    window.pay_status_label = QLabel("")
    window.pay_status_label.setObjectName("resultLabel")
    window.pay_status_label.setAlignment(Qt.AlignCenter)
    window.pay_status_label.hide()
    pay_layout.addWidget(window.pay_status_label)

    window.pay_info_frame = QFrame()
    window.pay_info_frame.setObjectName("payInfoFrame")
    pay_info_layout = QVBoxLayout(window.pay_info_frame)
    pay_info_layout.setContentsMargins(20, 20, 20, 20)
    pay_info_layout.setSpacing(15)

    window.pay_minutes_label = QLabel("")
    window.pay_minutes_label.setObjectName("payMinutesLabel")
    window.pay_minutes_label.setAlignment(Qt.AlignCenter)
    pay_info_layout.addWidget(window.pay_minutes_label)

    window.pay_amount_label = QLabel("")
    window.pay_amount_label.setObjectName("payAmountLabel")
    window.pay_amount_label.setAlignment(Qt.AlignCenter)
    pay_info_layout.addWidget(window.pay_amount_label)

    window.pay_confirm_btn = QPushButton("Confirma Plata")
    window.pay_confirm_btn.setObjectName("payConfirmBtn")
    window.pay_confirm_btn.setCursor(Qt.PointingHandCursor)
    window.pay_confirm_btn.setMinimumHeight(45)
    window.pay_confirm_btn.clicked.connect(window.handle_confirm_payment)
    pay_info_layout.addWidget(window.pay_confirm_btn)

    pay_layout.addWidget(window.pay_info_frame)
    window.pay_info_frame.hide()

    pay_layout.addStretch()

    action_content_layout.addWidget(window.pay_content)
    window.pay_content.hide()


def _add_exit_content(window, action_content_layout):
    window.exit_content = QWidget()
    exit_layout = QVBoxLayout(window.exit_content)
    exit_layout.setContentsMargins(0, 0, 0, 0)
    exit_layout.setSpacing(10)

    exit_title = QLabel("Iesire")
    exit_title.setAlignment(Qt.AlignCenter)
    exit_title.setObjectName("sectionTitle")
    exit_layout.addWidget(exit_title)

    window.leave_qr_preview = QLabel()
    window.leave_qr_preview.setObjectName("qrPreview")
    window.leave_qr_preview.setAlignment(Qt.AlignCenter)
    window.leave_qr_preview.setMinimumHeight(394)
    window.leave_qr_preview.setFixedHeight(394)
    window.leave_qr_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    window.leave_qr_preview.hide()
    exit_layout.addWidget(window.leave_qr_preview)

    window.leave_code_input = QLineEdit()
    window.leave_code_input.setPlaceholderText("Codul unic din QR va aparea aici...")
    window.leave_code_input.setObjectName("codeInput")
    window.leave_code_input.setReadOnly(True)
    window.leave_code_input.setAlignment(Qt.AlignCenter)
    window.leave_code_input.hide()
    exit_layout.addWidget(window.leave_code_input)

    leave_button_layout = QHBoxLayout()
    leave_button_layout.addStretch()
    window.leave_execute_btn = QPushButton("Leave")
    window.leave_execute_btn.setObjectName("primaryBtn")
    window.leave_execute_btn.setMinimumHeight(45)
    window.leave_execute_btn.clicked.connect(window.handle_leave_parking)
    window.leave_execute_btn.hide()
    leave_button_layout.addWidget(window.leave_execute_btn)
    leave_button_layout.addStretch()
    exit_layout.addLayout(leave_button_layout)

    window.leave_status_label = QLabel("")
    window.leave_status_label.setObjectName("resultLabel")
    window.leave_status_label.setAlignment(Qt.AlignCenter)
    window.leave_status_label.hide()
    exit_layout.addWidget(window.leave_status_label)

    exit_layout.addStretch()

    action_content_layout.addWidget(window.exit_content)
    window.exit_content.hide()
