import random
import math
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient, QBrush, QPen
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame)

# Quotes list with avatar colors and initials
QUOTES = [
    {"text": "Mathematics is the language in which God has written the universe.", "author": "Galileo Galilei", "initials": "GG", "color1": QColor(139, 92, 246), "color2": QColor(99, 102, 241)},
    {"text": "Equipped with his five senses, man explores the universe around him and calls the adventure Science.", "author": "Edwin Hubble", "initials": "EH", "color1": QColor(99, 102, 241), "color2": QColor(59, 130, 246)},
    {"text": "Look deep into nature, and then you will understand everything better.", "author": "Albert Einstein", "initials": "AE", "color1": QColor(244, 63, 94), "color2": QColor(219, 39, 119)},
    {"text": "In mathematics the art of proposing a question must be held of higher value than solving it.", "author": "Georg Cantor", "initials": "GC", "color1": QColor(37, 99, 235), "color2": QColor(29, 78, 216)},
    {"text": "What we know is a drop, what we don't know is an ocean.", "author": "Isaac Newton", "initials": "IN", "color1": QColor(13, 148, 136), "color2": QColor(15, 118, 110)},
    {"text": "There is geometry in the humming of the strings, there is music in the spacing of the spheres.", "author": "Pythagoras", "initials": "PY", "color1": QColor(217, 119, 6), "color2": QColor(180, 83, 9)},
    {"text": "The important thing is not to stop questioning. Curiosity has its own reason for existence.", "author": "Albert Einstein", "initials": "AE", "color1": QColor(244, 63, 94), "color2": QColor(219, 39, 119)},
    {"text": "Mathematics reveals its secrets only to those who approach it with pure love, for its beauty.", "author": "Archimedes", "initials": "AR", "color1": QColor(16, 185, 129), "color2": QColor(4, 120, 87)}
]

class Particle:
    def __init__(self, w, h):
        self.x = random.random() * w
        self.y = random.random() * h
        self.size = random.random() * 2 + 1.0
        self.vx = random.random() * 0.8 - 0.4
        self.vy = random.random() * 0.8 - 0.4
        self.color = QColor(59, 130, 246, 100) if random.random() > 0.5 else QColor(0, 229, 255, 100)

    def update(self, w, h):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > w:
            self.vx *= -1
        if self.y < 0 or self.y > h:
            self.vy *= -1

class ParticlesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(33) # ~30 FPS

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        self.particles = [Particle(w, h) for _ in range(50)]

    def animate(self):
        w, h = self.width(), self.height()
        for p in self.particles:
            p.update(w, h)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradient background
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor(20, 24, 56, 230))
        grad.setColorAt(1.0, QColor(13, 14, 28, 230))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 16, 16)

        # Draw lines between close particles (Plexus/Network web link effect)
        for i in range(len(self.particles)):
            p1 = self.particles[i]
            for j in range(i + 1, len(self.particles)):
                p2 = self.particles[j]
                dist = math.hypot(p1.x - p2.x, p1.y - p2.y)
                if dist < 85:
                    alpha = int((1.0 - (dist / 85)) * 40)
                    if alpha > 0:
                        # Draw soft blue plexus connection lines
                        painter.setPen(QPen(QColor(59, 130, 246, alpha), 1))
                        painter.drawLine(QPointF(p1.x, p1.y), QPointF(p2.x, p2.y))

        # Draw particles
        for p in self.particles:
            painter.setBrush(QBrush(p.color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(p.x, p.y), p.size + 1.0, p.size + 1.0)

class AvatarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.initials = "GG"
        self.color1 = QColor(139, 92, 246)
        self.color2 = QColor(99, 102, 241)

    def set_avatar(self, initials, color1, color2):
        self.initials = initials
        self.color1 = color1
        self.color2 = color2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw gradient circle background
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, self.color1)
        grad.setColorAt(1.0, self.color2)
        
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        # 46x46 circle centered in 50x50 widget
        painter.drawEllipse(2, 2, 46, 46)
        
        # Soft outer white glow border line
        border_pen = QPen(QColor(255, 255, 255, 35), 1.5)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(2, 2, 46, 46)
        
        # Initials Text centered
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Outfit", 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.initials)

class DashboardView(QWidget):
    # Signals to change tabs
    change_tab_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.quote_idx = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # 1. Welcome Panel (with absolute overlay layout using helper)
        self.welcome_panel = ParticlesWidget(self)
        self.welcome_panel.setMinimumHeight(240)
        
        # Grid layout inside welcome panel to position text and buttons safely
        welcome_layout = QVBoxLayout(self.welcome_panel)
        welcome_layout.setContentsMargins(40, 30, 40, 30)
        welcome_layout.setSpacing(10)

        badge = QLabel("OFFLINE DESKTOP LAB")
        badge.setStyleSheet("background-color: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); color: #acc8ff; font-size: 10px; font-weight: bold; padding: 4px 8px; border-radius: 6px;")
        badge.setSizePolicy(badge.sizePolicy().Fixed, badge.sizePolicy().Fixed)
        
        self.welcome_title = QLabel("Exploration through Visualizing")
        self.welcome_title.setFont(QFont("Outfit", 26, QFont.Bold))
        self.welcome_title.setStyleSheet("color: white;")

        self.welcome_desc = QLabel(
            "Unlock the secrets of math and physics. Choose a lab from the sidebar, "
            "adjust simulation parameters in real time, and watch the calculations dynamically unfold step-by-step!"
        )
        self.welcome_desc.setWordWrap(True)
        self.welcome_desc.setFont(QFont("Outfit", 12))
        self.welcome_desc.setStyleSheet("color: #94a3b8;")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_math = QPushButton("Math Studio")
        btn_math.setObjectName("welcome-btn-math")
        btn_math.setCursor(Qt.PointingHandCursor)
        btn_math.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; color: white; font-weight: bold; border-radius: 8px; padding: 10px 20px; font-size: 13px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        btn_math.clicked.connect(lambda: self.change_tab_signal.emit("math"))

        btn_phys = QPushButton("Physics Sandbox")
        btn_phys.setObjectName("welcome-btn-phys")
        btn_phys.setCursor(Qt.PointingHandCursor)
        btn_phys.setStyleSheet("""
            QPushButton {
                background: transparent; border: 1px solid rgba(255, 255, 255, 0.12); color: white; font-weight: bold; border-radius: 8px; padding: 10px 20px; font-size: 13px;
            }
            QPushButton:hover { border-color: rgba(255,255,255,0.25); background: rgba(255,255,255,0.03); }
        """)
        btn_phys.clicked.connect(lambda: self.change_tab_signal.emit("physics"))

        btn_layout.addWidget(btn_math)
        btn_layout.addWidget(btn_phys)
        btn_layout.addStretch()

        welcome_layout.addWidget(badge)
        welcome_layout.addWidget(self.welcome_title)
        welcome_layout.addWidget(self.welcome_desc)
        welcome_layout.addLayout(btn_layout)

        layout.addWidget(self.welcome_panel)

        # 2. Split Area -> Constants and Quote of the Day
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # Left Part: Scientific Constants Drawer
        self.constants_frame = QFrame()
        self.constants_frame.setObjectName("constants_panel")
        self.constants_frame.setProperty("class", "glass-panel")
        self.constants_frame.setStyleSheet("""
            QFrame#constants_panel {
                background-color: rgba(20, 21, 38, 0.55); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px;
            }
        """)
        const_layout = QVBoxLayout(self.constants_frame)
        const_layout.setContentsMargins(20, 20, 20, 20)

        self.const_title = QLabel("Scientific Constants Drawer")
        self.const_title.setFont(QFont("Outfit", 16, QFont.Bold))
        self.const_title.setStyleSheet("color: white;")
        
        self.const_desc = QLabel("Quick look at universal constants for science & math calculations.")
        self.const_desc.setFont(QFont("Outfit", 11))
        self.const_desc.setStyleSheet("color: #94a3b8; margin-bottom: 12px;")

        const_layout.addWidget(self.const_title)
        const_layout.addWidget(self.const_desc)

        # Constants grid (3x2 representation)
        constants = [
            {"symbol": "c", "name": "Speed of Light", "val": "299,792,458 m/s"},
            {"symbol": "g", "name": "Standard Gravity", "val": "9.80665 m/s²"},
            {"symbol": "G", "name": "Gravitational Const", "val": "6.6743 × 10⁻¹¹ N·m²/kg²"},
            {"symbol": "h", "name": "Planck Constant", "val": "6.62607 × 10⁻³⁴ J·s"},
            {"symbol": "π", "name": "Pi (Circle Ratio)", "val": "3.1415926535..."},
            {"symbol": "e", "name": "Euler's Number", "val": "2.7182818284..."}
        ]

        grid = QGridLayout()
        grid.setSpacing(10)
        for i, c in enumerate(constants):
            cf = QFrame()
            cf.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 8px;
                }
                QFrame:hover {
                    border-color: rgba(255, 255, 255, 0.12); background-color: rgba(255, 255, 255, 0.04);
                }
            """)
            cf_layout = QVBoxLayout(cf)
            cf_layout.setContentsMargins(8, 8, 8, 8)
            cf_layout.setSpacing(2)

            sym_lbl = QLabel(c["symbol"])
            sym_lbl.setAlignment(Qt.AlignRight)
            sym_lbl.setFont(QFont("JetBrains Mono", 14, QFont.Bold))
            sym_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.08);")

            name_lbl = QLabel(c["name"])
            name_lbl.setFont(QFont("Outfit", 9, QFont.Bold))
            name_lbl.setStyleSheet("color: #94a3b8; text-transform: uppercase;")

            val_lbl = QLabel(c["val"])
            val_lbl.setFont(QFont("JetBrains Mono", 10))
            val_lbl.setStyleSheet("color: white;")

            cf_layout.addWidget(sym_lbl)
            cf_layout.addWidget(name_lbl)
            cf_layout.addWidget(val_lbl)

            grid.addWidget(cf, i // 2, i % 2)

        const_layout.addLayout(grid)
        split_layout.addWidget(self.constants_frame, 3)

        # Right Part: Quote / Inspiration Section
        self.quote_frame = QFrame()
        self.quote_frame.setObjectName("quote_panel")
        self.quote_frame.setStyleSheet("""
            QFrame#quote_panel {
                background-color: rgba(20, 21, 38, 0.55); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px;
            }
        """)
        quote_layout = QVBoxLayout(self.quote_frame)
        quote_layout.setContentsMargins(24, 24, 24, 24)
        quote_layout.setSpacing(16)

        quote_mark = QLabel("“")
        quote_mark.setFont(QFont("Outfit", 48, QFont.Bold))
        quote_mark.setStyleSheet("color: #3b82f6; opacity: 0.3; line-height: 0px;")

        self.quote_text = QLabel(QUOTES[self.quote_idx]["text"])
        self.quote_text.setFont(QFont("Outfit", 13, QFont.StyleItalic))
        self.quote_text.setWordWrap(True)
        self.quote_text.setStyleSheet("color: #f8fafc;")

        self.quote_author = QLabel(f"— {QUOTES[self.quote_idx]['author']}")
        self.quote_author.setFont(QFont("Outfit", 11, QFont.Bold))
        self.quote_author.setStyleSheet("color: #94a3b8;")

        btn_next_quote = QPushButton("Next Quote →")
        btn_next_quote.setCursor(Qt.PointingHandCursor)
        btn_next_quote.setStyleSheet("""
            QPushButton {
                background: transparent; border: none; color: #3b82f6; font-weight: bold; font-size: 11px; text-align: left;
            }
            QPushButton:hover { color: #60a5fa; }
        """)
        btn_next_quote.clicked.connect(self.next_quote)

        # Bottom row integrating dynamic scientific avatar
        self.avatar_widget = AvatarWidget()
        q_init = QUOTES[self.quote_idx]
        self.avatar_widget.set_avatar(q_init["initials"], q_init["color1"], q_init["color2"])

        author_text_layout = QVBoxLayout()
        author_text_layout.setSpacing(2)
        author_text_layout.addWidget(self.quote_author)
        author_text_layout.addWidget(btn_next_quote)

        author_row = QHBoxLayout()
        author_row.setSpacing(12)
        author_row.addWidget(self.avatar_widget)
        author_row.addLayout(author_text_layout)
        author_row.addStretch()

        quote_layout.addWidget(quote_mark)
        quote_layout.addWidget(self.quote_text, 1)
        quote_layout.addLayout(author_row)

        split_layout.addWidget(self.quote_frame, 2)
        layout.addLayout(split_layout)

    def next_quote(self):
        self.quote_idx = (self.quote_idx + 1) % len(QUOTES)
        q = QUOTES[self.quote_idx]
        self.quote_text.setText(q["text"])
        self.quote_author.setText(f"— {q['author']}")
        self.avatar_widget.set_avatar(q["initials"], q["color1"], q["color2"])

    def translate_ui(self, trans):
        # We can implement multi-language updates here dynamically
        if 'dash_welcome_title' in trans:
            self.welcome_title.setText(trans['dash_welcome_title'])
        if 'dash_welcome_desc' in trans:
            self.welcome_desc.setText(trans['dash_welcome_desc'])
        if 'constants_title' in trans:
            self.const_title.setText(trans['constants_title'])
        if 'constants_desc' in trans:
            self.const_desc.setText(trans['constants_desc'])
