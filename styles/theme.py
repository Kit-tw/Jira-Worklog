DARK = """
QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: "Segoe UI", "SF Pro Display", Arial, sans-serif;
    font-size: 13px;
}
QMainWindow { background-color: #0f172a; }

/* ── Inputs ──────────────────────────────── */
QLineEdit, QDateEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e2e8f0;
}
QLineEdit:focus, QDateEdit:focus { border-color: #6366f1; }
QLineEdit:disabled, QDateEdit:disabled { color: #475569; }

/* ── Buttons ─────────────────────────────── */
QPushButton {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
}
QPushButton:hover  { background-color: #818cf8; }
QPushButton:pressed { background-color: #4f46e5; }
QPushButton:disabled { background-color: #334155; color: #475569; }

QPushButton#secondary {
    background-color: #1e293b;
    color: #94a3b8;
    border: 1px solid #334155;
    font-weight: 400;
}
QPushButton#secondary:hover { background-color: #334155; color: #e2e8f0; }

QPushButton#link {
    background-color: transparent;
    color: #60a5fa;
    border: none;
    padding: 0;
    font-weight: 400;
    text-decoration: underline;
}
QPushButton#link:hover { color: #93c5fd; }

/* ── Combo ───────────────────────────────── */
QComboBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e2e8f0;
}
QComboBox:focus { border-color: #6366f1; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #e2e8f0;
    selection-background-color: #6366f1;
    outline: none;
}

/* ── Checkbox ────────────────────────────── */
QCheckBox { color: #e2e8f0; spacing: 8px; }
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #1e293b;
}
QCheckBox::indicator:checked { background-color: #6366f1; border-color: #6366f1; }
QCheckBox::indicator:hover   { border-color: #6366f1; }

/* ── Labels ──────────────────────────────── */
QLabel#title    { font-size: 18px; font-weight: 700; color: #f1f5f9; }
QLabel#subtitle { font-size: 13px; color: #94a3b8; }
QLabel#issueLink { color: #60a5fa; font-size: 13px; padding: 2px 0; }
QLabel#historyLabel { color: #94a3b8; font-size: 12px; }

/* ── Scrollbar ───────────────────────────── */
QScrollBar:vertical { background: #0f172a; width: 6px; border-radius: 3px; }
QScrollBar::handle:vertical { background: #475569; border-radius: 3px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #64748b; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Calendar popup ──────────────────────── */
QCalendarWidget { background-color: #1e293b; color: #e2e8f0; }
QCalendarWidget QToolButton { background-color: #1e293b; color: #e2e8f0; border: none; }
QCalendarWidget QAbstractItemView:enabled {
    background-color: #1e293b;
    color: #e2e8f0;
    selection-background-color: #6366f1;
    selection-color: #ffffff;
}
QCalendarWidget QAbstractItemView:disabled { color: #475569; }

/* ── Dialogs ─────────────────────────────── */
QMessageBox        { background-color: #1e293b; }
QMessageBox QLabel { color: #e2e8f0; }
QDialog            { background-color: #0f172a; }
"""
