# Stylesheet definitions for native dark theme

STYLE_SHEET = """
QMainWindow {
    background-color: #070712;
}

/* Sidebar Styling */
#sidebar {
    background-color: #0b0c16;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

#brand_name {
    font-size: 20px;
    font-weight: 800;
    color: #ffffff;
}

#brand_subtitle {
    font-size: 11px;
    color: #64748b;
    font-weight: 600;
}

.nav-section-title {
    font-size: 11px;
    color: #64748b;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 10px;
}

/* Sidebar Nav Buttons */
#sidebar QPushButton {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
    border-radius: 12px;
}

#sidebar QPushButton:hover {
    color: #f8fafc;
    background-color: rgba(255, 255, 255, 0.03);
}

#sidebar QPushButton#nav-dashboard:checked {
    background-color: rgba(59, 130, 246, 0.12);
    border-left: 4px solid #3b82f6;
    color: #3b82f6;
}

#sidebar QPushButton#nav-math:checked {
    background-color: rgba(0, 229, 255, 0.12);
    border-left: 4px solid #00e5ff;
    color: #00e5ff;
}

#sidebar QPushButton#nav-physics:checked {
    background-color: rgba(189, 0, 255, 0.12);
    border-left: 4px solid #bd00ff;
    color: #bd00ff;
}

#sidebar QPushButton#nav-chemistry:checked {
    background-color: rgba(0, 255, 136, 0.12);
    border-left: 4px solid #00ff88;
    color: #00ff88;
}

/* Header & Top Bar */
#header_bar {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    background-color: transparent;
}

#current-tab-title {
    font-size: 24px;
    font-weight: 700;
    color: #f8fafc;
}

#current-tab-description {
    font-size: 14px;
    color: #94a3b8;
}

/* Glassmorphism panels */
.glass-panel {
    background-color: rgba(20, 21, 38, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
}

/* Form Controls & Inputs */
QComboBox, QLineEdit, QDoubleSpinBox, QSpinBox {
    background-color: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
    font-size: 13px;
}

QComboBox:focus, QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border-color: rgba(255, 255, 255, 0.25);
    background-color: rgba(0, 0, 0, 0.5);
}

QComboBox QAbstractItemView {
    background-color: #0f1020;
    color: #f8fafc;
    selection-background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Sliders styled with vibrant gradient backgrounds and polished knobs */
QSlider:horizontal {
    height: 24px;
    background: transparent;
}

QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #8b5cf6);
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #3b82f6;
    width: 14px;
    height: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #3b82f6;
    border: 2px solid #ffffff;
}

/* Sub-tabs buttons base styling */
#subtab_bar QPushButton {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 8px;
    margin: 2px;
}

#subtab_bar QPushButton:hover {
    color: #f8fafc;
    background: rgba(255, 255, 255, 0.02);
}

/* Physics sub-tabs checked */
#subtab_bar QPushButton#subtab-proj:checked,
#subtab_bar QPushButton#subtab-pend:checked,
#subtab_bar QPushButton#subtab-dbl:checked,
#subtab_bar QPushButton#subtab-opt:checked,
#subtab_bar QPushButton#subtab-orbit:checked {
    color: #bd00ff;
    background: rgba(189, 0, 255, 0.12);
    border-bottom: 2px solid #bd00ff;
}

/* Mathematics sub-tabs checked */
#subtab_bar QPushButton#subtab-calc:checked,
#subtab_bar QPushButton#subtab-matrix:checked,
#subtab_bar QPushButton#subtab-vector:checked,
#subtab_bar QPushButton#subtab-fourier:checked,
#subtab_bar QPushButton#subtab-galton:checked {
    color: #00e5ff;
    background: rgba(0, 229, 255, 0.12);
    border-bottom: 2px solid #00e5ff;
}

/* Chemistry sub-tabs checked */
#subtab_bar QPushButton#subtab-bohr:checked,
#subtab_bar QPushButton#subtab-titr:checked,
#subtab_bar QPushButton#subtab-gas:checked,
#subtab_bar QPushButton#subtab-periodic:checked,
#subtab_bar QPushButton#subtab-kinetics:checked {
    color: #00ff88;
    background: rgba(0, 255, 136, 0.12);
    border-bottom: 2px solid #00ff88;
}

/* Modern translucent Scrollbars */
QScrollBar:vertical {
    border: none;
    background: rgba(0, 0, 0, 0.2);
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.12);
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.22);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: rgba(0, 0, 0, 0.2);
    height: 6px;
    margin: 0px;
    border-radius: 3px;
}

QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.12);
    min-width: 20px;
    border-radius: 3px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(255, 255, 255, 0.22);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Generic buttons */
QPushButton.btn-primary {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
}

QPushButton.btn-primary:hover {
    background-color: #2563eb;
}

QPushButton.btn-outline {
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #f8fafc;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton.btn-outline:hover {
    border-color: rgba(255, 255, 255, 0.25);
    background-color: rgba(255, 255, 255, 0.03);
}

QPushButton.btn-text {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    padding: 6px 12px;
}

QPushButton.btn-text:hover {
    color: #f8fafc;
}

QLabel {
    color: #f8fafc;
}

/* Constants cards */
.constant-card {
    background-color: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

.constant-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
    background-color: rgba(255, 255, 255, 0.04);
}
"""
