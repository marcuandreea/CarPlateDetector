from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget


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
