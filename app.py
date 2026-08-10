import sys
import os
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, 
                             QStackedWidget, QComboBox, QButtonGroup)

# Add local directory to import path just in case
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from native_modules.styles import STYLE_SHEET
from native_modules.translations import TRANSLATIONS
from native_modules.dashboard import DashboardView
from native_modules.math_studio import MathStudioView
from native_modules.physics_sandbox import PhysicsSandboxView
from native_modules.chemistry_lab import ChemistryLabView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = 'en'
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SciMath Visual Studio - Desktop Console")
        self.resize(1280, 820)
        self.setMinimumSize(1024, 720)

        # Set style sheet globally
        self.setStyleSheet(STYLE_SHEET)

        # Main horizontal container splitting Sidebar and Content Area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Frame
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 25, 20, 20)
        sidebar_layout.setSpacing(10)

        # Brand header
        self.brand_title = QLabel("SciMath")
        self.brand_title.setObjectName("brand_name")
        self.brand_title.setFont(QFont("Outfit", 20, QFont.Bold))

        self.brand_subtitle = QLabel("Visual Studio")
        self.brand_subtitle.setObjectName("brand_subtitle")
        self.brand_subtitle.setFont(QFont("Outfit", 10))

        sidebar_layout.addWidget(self.brand_title)
        sidebar_layout.addWidget(self.brand_subtitle)
        
        # Spacer
        sidebar_layout.addSpacing(15)

        # Navigation section title
        self.sec_title = QLabel("SOLVERS & LABS")
        self.sec_title.setProperty("class", "nav-section-title")
        self.sec_title.setFont(QFont("Outfit", 9, QFont.Bold))
        sidebar_layout.addWidget(self.sec_title)

        # Navigation Buttons
        self.btn_dash = QPushButton("  Dashboard")
        self.btn_dash.setObjectName("nav-dashboard")
        self.btn_dash.setCheckable(True)
        self.btn_dash.setChecked(True)

        self.btn_math = QPushButton("  Mathematics Studio")
        self.btn_math.setObjectName("nav-math")
        self.btn_math.setCheckable(True)

        self.btn_phys = QPushButton("  Physics Sandbox")
        self.btn_phys.setObjectName("nav-physics")
        self.btn_phys.setCheckable(True)

        self.btn_chem = QPushButton("  Chemistry Lab")
        self.btn_chem.setObjectName("nav-chemistry")
        self.btn_chem.setCheckable(True)

        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.addButton(self.btn_dash)
        self.nav_button_group.addButton(self.btn_math)
        self.nav_button_group.addButton(self.btn_phys)
        self.nav_button_group.addButton(self.btn_chem)

        for btn in [self.btn_dash, self.btn_math, self.btn_phys, self.btn_chem]:
            btn.setCursor(Qt.PointingHandCursor)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Sidebar footer widgets (Language selection dropdown & Clock)
        sidebar_layout.addWidget(QLabel("LANGUAGE / භාෂාව / தமிழ்:"))
        
        self.lang_box = QComboBox()
        self.lang_box.addItems(["English", "සිංහල", "தமிழ்"])
        self.lang_box.currentIndexChanged.connect(self.change_language)
        sidebar_layout.addWidget(self.lang_box)

        # Dynamic digital clock widget (non-flickering, solid layout width)
        self.clock_lbl = QLabel()
        self.clock_lbl.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
        self.clock_lbl.setStyleSheet("""
            color: #64748b; 
            background: rgba(0, 0, 0, 0.2); 
            padding: 8px; 
            border-radius: 8px; 
            border: 1px solid rgba(255, 255, 255, 0.03); 
            margin-top: 10px;
        """)
        self.clock_lbl.setAlignment(Qt.AlignCenter)
        self.clock_lbl.setFixedWidth(220)  # Avoid layout shifts when seconds character widths change slightly
        sidebar_layout.addWidget(self.clock_lbl)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

        self.lbl_status = QLabel("Offline Engine Active")
        self.lbl_status.setStyleSheet("color: #64748b; font-size: 11px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.lbl_status)

        main_layout.addWidget(self.sidebar)

        # 2. Main Content Frame (Header Bar + View Stack)
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Header Bar panel
        header_bar = QFrame()
        header_bar.setObjectName("header_bar")
        hl = QVBoxLayout(header_bar)
        hl.setContentsMargins(0, 0, 0, 10)
        hl.setSpacing(4)

        self.header_title = QLabel("Dashboard")
        self.header_title.setObjectName("current-tab-title")
        self.header_title.setFont(QFont("Outfit", 22, QFont.Bold))

        self.header_desc = QLabel("OFFLINE DESKTOP LAB")
        self.header_desc.setObjectName("current-tab-description")
        self.header_desc.setFont(QFont("Outfit", 12))

        hl.addWidget(self.header_title)
        hl.addWidget(self.header_desc)
        content_layout.addWidget(header_bar)

        # QStackedWidget Content switching
        self.stack = QStackedWidget()
        self.dash_view = DashboardView()
        self.math_view = MathStudioView()
        self.phys_view = PhysicsSandboxView()
        self.chem_view = ChemistryLabView()

        self.stack.addWidget(self.dash_view)
        self.stack.addWidget(self.math_view)
        self.stack.addWidget(self.phys_view)
        self.stack.addWidget(self.chem_view)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_frame, 1)

        # Connect button triggers
        self.btn_dash.clicked.connect(lambda: self.switch_view(0))
        self.btn_math.clicked.connect(lambda: self.switch_view(1))
        self.btn_phys.clicked.connect(lambda: self.switch_view(2))
        self.btn_chem.clicked.connect(lambda: self.switch_view(3))

        # Dashboard internal launch triggers
        self.dash_view.change_tab_signal.connect(self.dashboard_tab_launch)

        # Apply initial language setup
        self.apply_translations()

    def update_clock(self):
        now = QDateTime.currentDateTime()
        self.clock_lbl.setText(now.toString("hh:mm:ss AP"))

    def change_language(self, index):
        langs = ['en', 'si', 'ta']
        self.current_lang = langs[index]
        self.apply_translations()

    def apply_translations(self):
        trans = TRANSLATIONS[self.current_lang]
        
        # Update left menus
        self.brand_title.setText(trans.get('app_title', 'SciMath'))
        self.brand_subtitle.setText(trans.get('app_subtitle', 'Visual Studio'))
        self.sec_title.setText(trans.get('nav_sec_title', 'SOLVERS & LABS'))
        
        self.btn_dash.setText("  " + trans.get('nav_dash', 'Dashboard'))
        self.btn_math.setText("  " + trans.get('nav_math', 'Mathematics Studio'))
        self.btn_phys.setText("  " + trans.get('nav_physics', 'Physics Sandbox'))
        self.btn_chem.setText("  " + trans.get('nav_chemistry', 'Chemistry Lab'))
        
        self.lbl_status.setText(trans.get('footer_status', 'Offline Engine Active'))

        # Let the dashboard view refresh its quote and cards titles too!
        self.dash_view.translate_ui(trans)

        # Refresh header title
        self.update_header(self.stack.currentIndex(), trans)

    def update_header(self, index, trans=None):
        if not trans:
            trans = TRANSLATIONS[self.current_lang]
        if index == 0:
            self.header_title.setText(trans.get('nav_dash', 'Dashboard'))
            self.header_desc.setText(trans.get('dash_badge', 'OFFLINE DESKTOP LAB'))
        elif index == 1:
            self.header_title.setText(trans.get('nav_math', 'Mathematics Studio'))
            self.header_desc.setText("Interactive algebra, calculus, and vector graphics solver.")
        elif index == 2:
            self.header_title.setText(trans.get('nav_physics', 'Physics Sandbox'))
            self.header_desc.setText("Kinematics, oscillations, chaos systems and optics simulation.")
        elif index == 3:
            self.header_title.setText(trans.get('nav_chemistry', 'Chemistry Lab'))
            self.header_desc.setText("Bohr atomic structure, gas law, acid-base pH titration, periodic table.")

    def switch_view(self, index):
        self.stack.setCurrentIndex(index)
        self.update_header(index)
        
        # Sync checked states of sidebar buttons
        buttons = [self.btn_dash, self.btn_math, self.btn_phys, self.btn_chem]
        if 0 <= index < len(buttons):
            buttons[index].setChecked(True)

    def dashboard_tab_launch(self, tab_name):
        if tab_name == "math":
            self.btn_math.setChecked(True)
            self.switch_view(1)
        elif tab_name == "physics":
            self.btn_phys.setChecked(True)
            self.switch_view(2)

def main():
    try:
        # Enable High DPI scaling for crisp rendering on high-res displays
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        app = QApplication(sys.argv)
        
        # Try setting app window icon
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        with open("crash_log.txt", "w") as f:
            f.write(str(e) + "\n")
            traceback.print_exc(file=f)

if __name__ == '__main__':
    main()
