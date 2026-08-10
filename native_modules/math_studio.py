import math
import random
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPolygonF
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame, QComboBox, QSlider,
                             QRadioButton, QButtonGroup, QLineEdit, QListWidget)

# Simple expression evaluator helper: processes whitelisted keywords & variables safely
def safe_eval(expr, x):
    clean = expr.lower().strip()
    # Strip spaces and allow only mathematical structures
    for char in clean:
        if char not in "0123456789x+-*/^(). \t\n":
            if not any(token in clean for token in ["sin", "cos", "tan", "abs", "exp", "log", "sqrt", "pi", "e"]):
                return 0.0

    clean = clean.replace("^", "**")
    
    # Mathematical terms dictionary
    safe_dict = {
        'x': x,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'abs': abs,
        'exp': math.exp,
        'log': math.log,
        'sqrt': math.sqrt,
        'pi': math.pi,
        'e': math.e
    }
    try:
        val = eval(clean, {"__builtins__": None}, safe_dict)
        if isinstance(val, (int, float)):
            return float(val)
        return 0.0
    except:
        return 0.0

# ----------------- Tab 1: Calculus Canvas -----------------
class CalculusCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.zoom = 30.0
        self.offsetX = 0.0
        self.offsetY = 0.0
        self.dragStart = QPoint()
        self.isDragging = False
        
        # State
        self.selected_func = 'sin'
        self.custom_expr = 'x * sin(x)'
        self.active_mode = 'move' # 'move', 'derivative', 'integral'
        self.tangent_x = 0.0
        self.integral_a = -4.0
        self.integral_b = 4.0
        self.integral_n = 20
        self.mouse_coords = (0.0, 0.0)

    def get_y_val(self, x):
        if self.selected_func == 'sin':
            return math.sin(x)
        elif self.selected_func == 'quadratic':
            return 0.2 * x * x - 3
        elif self.selected_func == 'cubic':
            return 0.05 * x * x * x - x
        elif self.selected_func == 'gaussian':
            try: return 4.0 * math.exp(-0.2 * x * x)
            except: return 0.0
        elif self.selected_func == 'damped':
            try: return 3.0 * math.exp(-0.1 * x) * math.cos(x)
            except: return 0.0
        elif self.selected_func == 'custom':
            return safe_eval(self.custom_expr, x)
        return 0.0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.active_mode == 'move':
            self.isDragging = True
            self.dragStart = event.pos()

    def mouseReleaseEvent(self, event):
        self.isDragging = False

    def mouseMoveEvent(self, event):
        cx = self.width() / 2 + self.offsetX
        cy = self.height() / 2 + self.offsetY
        # Calculate coordinate positions
        rx = (event.x() - cx) / self.zoom
        ry = -(event.y() - cy) / self.zoom
        self.mouse_coords = (rx, ry)
        
        if self.isDragging:
            delta = event.pos() - self.dragStart
            self.offsetX += delta.x()
            self.offsetY += delta.y()
            self.dragStart = event.pos()
            self.update()
        else:
            self.update()

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 0.85
        self.zoom = max(10.0, min(150.0, self.zoom * factor))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2 + self.offsetX, h / 2 + self.offsetY

        # Dark Canvas Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Grid lines
        grid_pen = QPen(QColor(255, 255, 255, 12), 1)
        painter.setPen(grid_pen)
        
        # Vertical grid lines
        start_x = int(cx % self.zoom)
        for x in range(start_x, w, int(self.zoom)):
            painter.drawLine(x, 0, x, h)

        # Horizontal grid
        start_y = int(cy % self.zoom)
        for y in range(start_y, h, int(self.zoom)):
            painter.drawLine(0, y, w, y)

        # Draw Axis Lines
        axis_pen = QPen(QColor(255, 255, 255, 76), 2)
        painter.setPen(axis_pen)
        painter.drawLine(0, int(cy), w, int(cy))
        painter.drawLine(int(cx), 0, int(cx), h)

        # Draw Numbers
        num_font = QFont("JetBrains Mono", 8)
        painter.setFont(num_font)
        painter.setPen(QColor(255, 255, 255, 128))
        
        # X coordinates labels
        limit_left = int(-cx / self.zoom) - 1
        limit_right = int((w - cx) / self.zoom) + 1
        for i in range(limit_left, limit_right):
            if i != 0:
                px = cx + i * self.zoom
                painter.drawText(int(px - 5), int(cy + 15), str(i))

        # Y coordinates labels
        limit_bot = int(-cy / self.zoom) - 1
        limit_top = int((h - cy) / self.zoom) + 1
        for i in range(limit_bot, limit_top):
            if i != 0:
                py = cy - i * self.zoom
                painter.drawText(int(cx - 20), int(py + 4), str(i))

        # Render integrated Area (Riemann Sums)
        if self.active_mode == 'integral':
            a = min(self.integral_a, self.integral_b)
            b = max(self.integral_a, self.integral_b)
            dx = (b - a) / self.integral_n
            
            painter.setPen(QPen(QColor(0, 229, 255, 100), 1))
            painter.setBrush(QBrush(QColor(0, 229, 255, 38)))
            
            for i in range(self.integral_n):
                x_mid = a + (i + 0.5) * dx
                y = self.get_y_val(x_mid)
                rect_x = cx + (a + i * dx) * self.zoom
                rect_w = dx * self.zoom
                rect_h = y * self.zoom
                
                # Riemann rectangle geometry setup
                if y >= 0:
                    painter.drawRect(int(rect_x), int(cy - rect_h), int(rect_w), int(rect_h))
                else:
                    painter.drawRect(int(rect_x), int(cy), int(rect_w), int(-rect_h))

            # Bounds limits drawing
            painter.setPen(QPen(QColor(189, 0, 255, 200), 1.5, Qt.DashLine))
            painter.drawLine(int(cx + a * self.zoom), 0, int(cx + a * self.zoom), h)
            painter.drawLine(int(cx + b * self.zoom), 0, int(cx + b * self.zoom), h)

        # Plot Curve
        curve_pen = QPen(QColor(0, 229, 255), 2.5)
        painter.setPen(curve_pen)
        painter.setBrush(Qt.NoBrush)

        points = []
        for px in range(w):
            x = (px - cx) / self.zoom
            try:
                y = self.get_y_val(x)
                py = cy - y * self.zoom
                if 0 <= py <= h:
                    points.append(QPointF(px, py))
            except:
                pass
        
        if len(points) > 1:
            poly = QPolygonF(points)
            painter.drawPolyline(poly)

        # Derivative mode tangent line drawing
        if self.active_mode == 'derivative':
            x0 = self.tangent_x
            try:
                y0 = self.get_y_val(x0)
                # Numerical derivative calculation
                eps = 0.0001
                y1 = self.get_y_val(x0 + eps)
                y_1 = self.get_y_val(x0 - eps)
                slope = (y1 - y_1) / (2 * eps)
                intercept = y0 - slope * x0
                
                # Draw dashed tangent line
                tangent_pen = QPen(QColor(234, 88, 12), 2, Qt.DashLine)
                painter.setPen(tangent_pen)
                
                x_start = -20
                x_end = 20
                y_start = slope * x_start + intercept
                y_end = slope * x_end + intercept
                
                painter.drawLine(
                    int(cx + x_start * self.zoom), int(cy - y_start * self.zoom),
                    int(cx + x_end * self.zoom), int(cy - y_end * self.zoom)
                )

                # Point indicator
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(255, 174, 0)))
                painter.drawEllipse(QPointF(cx + x0 * self.zoom, cy - y0 * self.zoom), 5, 5)
            except:
                pass
                
        # Draw overlay coordinates info
        painter.setPen(QColor(148, 163, 184))
        painter.setFont(QFont("Outfit", 9))
        painter.drawText(15, h - 15, f"x: {self.mouse_coords[0]:.2f}, y: {self.mouse_coords[1]:.2f}")

        # Draw hover crosshairs if mouse is inside the canvas
        if hasattr(self, 'mouse_coords') and self.underMouse():
            mx, my = self.mouse_coords
            px = cx + mx * self.zoom
            py = cy - my * self.zoom
            
            if 0 <= px <= w and 0 <= py <= h:
                # Hover crosshair lines
                cross_pen = QPen(QColor(255, 255, 255, 25), 1, Qt.DashLine)
                painter.setPen(cross_pen)
                painter.drawLine(0, int(py), w, int(py))
                painter.drawLine(int(px), 0, int(px), h)
                
                # Floating coordinate description badge
                painter.setPen(QPen(QColor(0, 229, 255, 80), 1))
                painter.setBrush(QBrush(QColor(15, 23, 42, 230)))
                # Draw small black box near cursor
                bx, by = int(px + 12), int(py - 25)
                # Bounds check to make sure the tooltip stays visible inside the viewport boundaries
                if bx + 110 > w:
                    bx = int(px - 120)
                if by < 0:
                    by = int(py + 10)
                painter.drawRoundedRect(bx, by, 110, 20, 4, 4)
                
                painter.setFont(QFont("JetBrains Mono", 8, QFont.Bold))
                painter.setPen(QColor(0, 229, 255))
                painter.drawText(bx + 8, by + 14, f"X:{mx:.2f} Y:{my:.2f}")


# ----------------- Tab 2: Matrix Grid Space Canvas -----------------
class MatrixCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.t = 1.0 # interpolation factor: 0.0=identity, 1.0=fully transformed
        self.matrix = [[2.0, 1.0], [0.5, 1.5]] # defaults
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.anim_step = 0
        self.grid_pts = []
        self.init_pts()

    def init_pts(self):
        # Grid layout points
        self.grid_pts = []
        for x in [val * 0.5 for val in range(-10, 11)]:
            for y in [val * 0.5 for val in range(-10, 11)]:
                self.grid_pts.append({'x': x, 'y': y, 'color': QColor(255, 255, 255, 30), 'size': 2.0})

        # Smiley face drawing points
        smile_color = QColor(0, 255, 136)
        # Head circle
        for i in range(40):
            ang = (i / 40.0) * 2.0 * math.pi
            self.grid_pts.append({'x': math.cos(ang) * 2.5, 'y': math.sin(ang) * 2.5, 'color': smile_color, 'size': 3.5})
        # Eyes
        self.grid_pts.append({'x': -0.8, 'y': 0.8, 'color': smile_color, 'size': 4.5})
        self.grid_pts.append({'x': 0.8, 'y': 0.8, 'color': smile_color, 'size': 4.5})
        # Smile Mouth
        for i in range(12):
            ang = 0.85 * math.pi + (i / 11.0) * 0.3 * math.pi
            self.grid_pts.append({'x': math.cos(ang) * 1.4, 'y': math.sin(ang) * 1.4 + 0.3, 'color': smile_color, 'size': 3.5})

    def start_animation(self):
        self.t = 0.0
        self.anim_step = 0
        self.timer.start(25) # ~40 FPS

    def update_animation(self):
        self.anim_step += 1
        self.t = self.anim_step / 40.0
        if self.t >= 1.0:
            self.t = 1.0
            self.timer.stop()
        self.update()

    def draw_arrow(self, painter, cx, cy, tx, ty, color, width, label):
        painter.setPen(QPen(color, width))
        painter.drawLine(int(cx), int(cy), int(tx), int(ty))
        
        # Calculate arrowhead coordinates
        ang = math.atan2(ty - cy, tx - cx)
        arrow_len = 10
        arrow_w = 4 * math.pi / 5 # 144 degrees
        
        x1 = tx - arrow_len * math.cos(ang - arrow_w)
        y1 = ty - arrow_len * math.sin(ang - arrow_w)
        x2 = tx - arrow_len * math.cos(ang + arrow_w)
        y2 = ty - arrow_len * math.sin(ang + arrow_w)
        
        poly = QPolygonF([QPointF(tx, ty), QPointF(x1, y1), QPointF(x2, y2)])
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(poly)

        # Draw label
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("JetBrains Mono", 9, QFont.Bold))
        painter.drawText(int(tx + 8 * math.cos(ang)), int(ty + 8 * math.sin(ang)), label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        zoom = 45.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Setup interpolated transformation matrix
        # Mt = (1-t)*I + t*M
        m = self.matrix
        mt = [
            [(1.0 - self.t) * 1.0 + self.t * m[0][0], (1.0 - self.t) * 0.0 + self.t * m[0][1]],
            [(1.0 - self.t) * 0.0 + self.t * m[1][0], (1.0 - self.t) * 1.0 + self.t * m[1][1]]
        ]

        # Draw transformed grid lines by segments
        grid_pen = QPen(QColor(255, 255, 255, 12), 1)
        painter.setPen(grid_pen)
        painter.setBrush(Qt.NoBrush)

        # Draw grid lines (-6 to 6 units)
        for xl in range(-6, 7):
            pts_x = []
            for y_step in range(-30, 31):
                yl = y_step * 0.2
                tx = mt[0][0] * xl + mt[0][1] * yl
                ty = mt[1][0] * xl + mt[1][1] * yl
                pts_x.append(QPointF(cx + tx * zoom, cy - ty * zoom))
            painter.drawPolyline(QPolygonF(pts_x))

        for yl in range(-6, 7):
            pts_y = []
            for x_step in range(-30, 31):
                xl = x_step * 0.2
                tx = mt[0][0] * xl + mt[0][1] * yl
                ty = mt[1][0] * xl + mt[1][1] * yl
                pts_y.append(QPointF(cx + tx * zoom, cy - ty * zoom))
            painter.drawPolyline(QPolygonF(pts_y))

        # Basis components
        ix, iy = mt[0][0], mt[1][0]
        jx, jy = mt[0][1], mt[1][1]

        # Draw lattice points transformed
        for pt in self.grid_pts:
            tx = mt[0][0] * pt['x'] + mt[0][1] * pt['y']
            ty = mt[1][0] * pt['x'] + mt[1][1] * pt['y']
            painter.setBrush(QBrush(pt['color']))
            painter.setPen(Qt.NoPen)
            sz = pt['size']
            painter.drawEllipse(QPointF(cx + tx * zoom, cy - ty * zoom), sz, sz)

        # Draw transformed basis vectors (i-hat cyan, j-hat magenta)
        self.draw_arrow(painter, cx, cy, cx + ix * zoom, cy - iy * zoom, QColor(0, 229, 255), 3, "î")
        self.draw_arrow(painter, cx, cy, cx + jx * zoom, cy - jy * zoom, QColor(189, 0, 255), 3, "ĵ")


# ----------------- Tab 3: Vector Canvas -----------------
class VectorCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ax = 4.0
        self.ay = 3.0
        self.bx = -3.0
        self.by = 4.0

    def draw_arrow(self, painter, cx, cy, tx, ty, color, width, label):
        painter.setPen(QPen(color, width))
        painter.drawLine(int(cx), int(cy), int(tx), int(ty))
        
        # Arrowhead
        ang = math.atan2(ty - cy, tx - cx)
        arrow_len = 10
        arrow_w = 4 * math.pi / 5
        x1 = tx - arrow_len * math.cos(ang - arrow_w)
        y1 = ty - arrow_len * math.sin(ang - arrow_w)
        x2 = tx - arrow_len * math.cos(ang + arrow_w)
        y2 = ty - arrow_len * math.sin(ang + arrow_w)
        
        poly = QPolygonF([QPointF(tx, ty), QPointF(x1, y1), QPointF(x2, y2)])
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(poly)

        # Label placement
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Outfit", 10, QFont.Bold))
        painter.drawText(int(tx + 8 * math.cos(ang) - 4), int(ty + 8 * math.sin(ang) + 4), label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        zoom = 30.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Standard grid
        grid_pen = QPen(QColor(255, 255, 255, 12), 1)
        painter.setPen(grid_pen)
        for xl in range(int(-w/(2*zoom)), int(w/(2*zoom)) + 1):
            px = cx + xl * zoom
            painter.drawLine(int(px), 0, int(px), h)
        for yl in range(int(-h/(2*zoom)), int(h/(2*zoom)) + 1):
            py = cy - yl * zoom
            painter.drawLine(0, int(py), w, int(py))

        # Standard axes
        axis_pen = QPen(QColor(255, 255, 255, 50), 2)
        painter.setPen(axis_pen)
        painter.drawLine(0, int(cy), w, int(cy))
        painter.drawLine(int(cx), 0, int(cx), h)

        # Vector A: Cyan
        tx_a = cx + self.ax * zoom
        ty_a = cy - self.ay * zoom
        self.draw_arrow(painter, cx, cy, tx_a, ty_a, QColor(0, 229, 255), 2.5, "A")

        # Vector B: Magenta
        tx_b = cx + self.bx * zoom
        ty_b = cy - self.by * zoom
        self.draw_arrow(painter, cx, cy, tx_b, ty_b, QColor(189, 0, 255), 2.5, "B")

        # Vector A+B Sum: Orange
        sum_x = self.ax + self.bx
        sum_y = self.ay + self.by
        tx_sum = cx + sum_x * zoom
        ty_sum = cy - sum_y * zoom
        self.draw_arrow(painter, cx, cy, tx_sum, ty_sum, QColor(245, 158, 11), 3.0, "A+B")

        # Visualise A+B tip addition bounds (dashed guidelines)
        guideline_pen = QPen(QColor(255, 255, 255, 60), 1, Qt.DashLine)
        painter.setPen(guideline_pen)
        painter.drawLine(int(tx_a), int(ty_a), int(tx_sum), int(ty_sum))
        painter.drawLine(int(tx_b), int(ty_b), int(tx_sum), int(ty_sum))


# ----------------- Tab 4: Fourier Synthesizer Canvas -----------------
class FourierCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wave_type = 'square'
        self.harmonics = 10
        self.freq = 1.0
        self.time = 0.0
        self.wave_history = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(30) # ~33 FPS

    def tick(self):
        self.time += 0.02 * self.freq
        
        # Calculate current Fourier point
        cx, cy = self.width() / 4.0, self.height() / 2.0
        px, py = cx, cy
        
        for k in range(1, self.harmonics + 1):
            prev_x, prev_y = px, py
            
            # Determine term multiplier based on wave type
            if self.wave_type == 'square':
                n = 2 * k - 1
                r = (55.0 * 4.0) / (math.pi * n)
                theta = n * self.time
            elif self.wave_type == 'sawtooth':
                n = k
                r = (55.0 * 2.0) / (math.pi * n) * (-1.0 if k % 2 == 0 else 1.0)
                theta = n * self.time
            elif self.wave_type == 'triangle':
                n = 2 * k - 1
                r = (70.0 * 8.0) / (math.pi**2 * n**2) * (-1.0 if ((n - 1) // 2) % 2 != 0 else 1.0)
                theta = n * self.time
            else:
                n, r, theta = 1, 0, 0
                
            px += r * math.cos(theta)
            py += r * math.sin(theta)

        # Store Y value coordinate history
        self.wave_history.insert(0, py - cy)
        if len(self.wave_history) > 400:
            self.wave_history.pop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 4.0, h / 2.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Helper guidelines
        painter.setPen(QPen(QColor(255, 255, 255, 15), 1))
        painter.drawLine(0, int(cy), w, int(cy))

        # Calculate and draw epicycles (draw circles)
        px, py = cx, cy
        for k in range(1, self.harmonics + 1):
            prev_x, prev_y = px, py
            
            if self.wave_type == 'square':
                n = 2 * k - 1
                r = (55.0 * 4.0) / (math.pi * n)
                theta = n * self.time
            elif self.wave_type == 'sawtooth':
                n = k
                r = (55.0 * 2.0) / (math.pi * n) * (-1.0 if k % 2 == 0 else 1.0)
                theta = n * self.time
            elif self.wave_type == 'triangle':
                n = 2 * k - 1
                r = (70.0 * 8.0) / (math.pi**2 * n**2) * (-1.0 if ((n - 1) // 2) % 2 != 0 else 1.0)
                theta = n * self.time
            else:
                n, r, theta = 1, 0, 0
                
            px += r * math.cos(theta)
            py += r * math.sin(theta)

            # Circle path
            painter.setPen(QPen(QColor(255, 255, 255, 18), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(prev_x, prev_y), r, r)

            # Vector line radius
            vector_color = QColor(0, 229, 255, 160) if k % 2 == 0 else QColor(189, 0, 255, 160)
            painter.setPen(QPen(vector_color, 1.5))
            painter.drawLine(QPointF(prev_x, prev_y), QPointF(px, py))

        # Tip dot
        painter.setBrush(QBrush(QColor(0, 255, 136)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(px, py), 4, 4)

        # Draw guideline connecting tip to wave plotter
        painter.setPen(QPen(QColor(0, 255, 136, 80), 1, Qt.DashLine))
        wave_start_x = w / 2.2
        painter.drawLine(QPointF(px, py), QPointF(wave_start_x, py))

        # Trace Wave history
        if self.wave_history:
            trace_pen = QPen(QColor(0, 229, 255), 2)
            painter.setPen(trace_pen)
            pts = []
            for i, y_val in enumerate(self.wave_history):
                wx = wave_start_x + i * 1.2
                if wx < w:
                    pts.append(QPointF(wx, cy + y_val))
            if len(pts) > 1:
                painter.drawPolyline(QPolygonF(pts))


# ----------------- Tab 5: Galton Board Canvas -----------------
class GaltonCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = 9
        self.elasticity = 0.5
        self.balls = []
        self.bins = []
        self.accumulated = 0
        self.autodrop = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(25) # ~40 FPS

        self.drop_timer = QTimer(self)
        self.drop_timer.timeout.connect(self.drop_ball)
        self.drop_timer.start(350) # drop ball every 350ms if autodrop

    def init_bins(self):
        # Initialize bucket bins counts
        self.bins = [0] * (self.rows + 1)
        self.accumulated = 0
        self.balls.clear()

    def drop_ball(self):
        if self.autodrop or (len(self.balls) == 0 and not self.autodrop):
            # Create a ball at top center
            w = self.width() if self.width() > 0 else 400
            self.balls.append({
                'x': w / 2 + random.uniform(-2, 2),
                'y': 40.0,
                'vx': 0.0,
                'vy': 1.0,
                'row': -1
            })

    def trigger_single_drop(self):
        w = max(400, self.width())
        self.balls.append({
            'x': w / 2 + random.uniform(-2, 2),
            'y': 40.0,
            'vx': 0.0,
            'vy': 1.0,
            'row': -1
        })

    def tick(self):
        w, h = self.width(), self.height()
        if w < 100 or h < 100:
            return
            
        cx = w / 2
        peg_pitch_y = (h - 200.0) / self.rows
        peg_pitch_x = 24.0

        # Update each ball
        active_balls = []
        for b in self.balls:
            # Physics motion
            b['vy'] += 0.25 # Gravity accel multiplier
            b['vy'] *= 0.98 # air resistance Damping
            b['vx'] *= 0.98
            
            b['x'] += b['vx']
            b['y'] += b['vy']

            # Check rows pegs collision
            for r in range(self.rows):
                row_y = 70.0 + r * peg_pitch_y
                if abs(b['y'] - row_y) < 6.0: # near peg row
                    # Find which peg it is closest to
                    # In row r, there are r+1 pegs symmetrical around center cx
                    pegs_count = r + 1
                    row_w = (pegs_count - 1) * peg_pitch_x
                    start_px = cx - row_w / 2.0
                    
                    for p_idx in range(pegs_count):
                        px = start_px + p_idx * peg_pitch_x
                        dist = math.hypot(b['x'] - px, b['y'] - row_y)
                        
                        if dist < 8.0 and b['row'] < r:
                            # Bounce collision!
                            b['row'] = r
                            # Ball decides randomly to fall left or right
                            b['vx'] = (-1.8 if random.random() > 0.5 else 1.8) * self.elasticity
                            b['vy'] = 1.0 * self.elasticity
                            b['y'] = row_y + 4.0 # resolve overlap

            # Check bottom boundary limits
            bins_y = h - 140.0
            if b['y'] >= bins_y:
                # Land in appropriate bucket bin
                # Find bucket index based on position relative to center
                bin_width = 16.0
                bin_offset = (b['x'] - cx) / bin_width
                bin_idx = int(round(bin_offset + (self.rows + 1) / 2.0 - 0.5))
                
                # Clamp bin index
                bin_idx = max(0, min(self.rows, bin_idx))
                
                if len(self.bins) > bin_idx:
                    self.bins[bin_idx] += 1
                    self.accumulated += 1
                # Remove ball
            else:
                active_balls.append(b)

        self.balls = active_balls
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx = w / 2
        peg_pitch_y = (h - 200.0) / self.rows
        peg_pitch_x = 24.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Pegs drawing (silver small elements)
        painter.setPen(Qt.NoPen)
        for r in range(self.rows):
            row_y = 70.0 + r * peg_pitch_y
            pegs_count = r + 1
            row_w = (pegs_count - 1) * peg_pitch_x
            start_px = cx - row_w / 2.0
            
            for p_idx in range(pegs_count):
                px = start_px + p_idx * peg_pitch_x
                painter.setBrush(QBrush(QColor(148, 163, 184)))
                painter.drawEllipse(QPointF(px, row_y), 2.5, 2.5)

        # Draw channels divider guidelines at bottom
        bin_width = 16.0
        bins_y = h - 140.0
        painter.setPen(QPen(QColor(255, 255, 255, 12), 1))
        
        bins_count = self.rows + 1
        bins_w = bins_count * bin_width
        start_bin_x = cx - bins_w / 2.0

        for col in range(bins_count + 1):
            bx = start_bin_x + col * bin_width
            painter.drawLine(int(bx), int(bins_y), int(bx), h - 10)

        # Draw Bin Histogram Accumulations
        max_accum = max(self.bins) if self.bins and max(self.bins) > 0 else 1
        painter.setPen(Qt.NoPen)
        
        for idx, count in enumerate(self.bins):
            if count > 0:
                bx = start_bin_x + idx * bin_width + 1
                bh = (count / max_accum) * 110.0 # scale bar height relative to peaks
                
                # Dynamic distribution color gradient block
                bar_color = QColor(0, 255, 136, 180) if idx == (bins_count - 1) // 2 else QColor(0, 229, 255, 150)
                painter.setBrush(QBrush(bar_color))
                painter.drawRect(int(bx), int(h - 10 - bh), int(bin_width - 2), int(bh))

        # Draw Normal Curve Guide Overlay
        if self.accumulated > 5:
            painter.setPen(QPen(QColor(250, 204, 21, 150), 1.5, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            curve_pts = []
            
            mu_x = cx
            sigma_px = math.sqrt(self.rows * 0.25) * bin_width
            
            for sx in range(int(start_bin_x), int(start_bin_x + bins_w)):
                dx = sx - mu_x
                y = h - 10 - 110.0 * math.exp(- (dx * dx) / (2.0 * sigma_px * sigma_px))
                if y > bins_y - 25:
                    curve_pts.append(QPointF(sx, y))
            
            if len(curve_pts) > 1:
                painter.drawPolyline(QPolygonF(curve_pts))

        for b in self.balls:
            painter.setBrush(QBrush(QColor(189, 0, 255))) # Magenta active balls
            painter.setPen(QPen(QColor(255, 255, 255, 150), 0.5))
            painter.drawEllipse(QPointF(b['x'], b['y']), 4, 4)


# ----------------- Main Math Tab Studio Container View -----------------
from PyQt5.QtWidgets import QStackedWidget, QFormLayout, QHBoxLayout, QDoubleSpinBox, QRadioButton, QLineEdit

class MathStudioView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        # 1. Subtab Bar Header
        self.subtab_bar = QFrame()
        self.subtab_bar.setObjectName("subtab_bar")
        self.subtab_bar.setStyleSheet("""
            QFrame#subtab_bar {
                background-color: rgba(20, 21, 38, 0.4); border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding: 5px;
            }
        """)
        sub_layout = QHBoxLayout(self.subtab_bar)
        sub_layout.setContentsMargins(10, 5, 10, 5)
        sub_layout.setSpacing(8)

        self.btn_calc = QPushButton("Calculus & Graphing")
        self.btn_calc.setObjectName("subtab-calc")
        self.btn_matrix = QPushButton("Linear Algebra")
        self.btn_matrix.setObjectName("subtab-matrix")
        self.btn_vector = QPushButton("Vector Solver")
        self.btn_vector.setObjectName("subtab-vector")
        self.btn_fourier = QPushButton("Fourier Synthesizer")
        self.btn_fourier.setObjectName("subtab-fourier")
        self.btn_galton = QPushButton("Galton Board")
        self.btn_galton.setObjectName("subtab-galton")

        self.subtab_group = QButtonGroup(self)
        for btn in [self.btn_calc, self.btn_matrix, self.btn_vector, self.btn_fourier, self.btn_galton]:
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            self.subtab_group.addButton(btn)
            sub_layout.addWidget(btn)
        sub_layout.addStretch()

        self.btn_calc.setChecked(True)
        main_layout.addWidget(self.subtab_bar)

        # 2. Main Content Split View
        split_layout = QHBoxLayout()
        split_layout.setContentsMargins(5, 5, 5, 5)
        split_layout.setSpacing(15)

        # Screen Stacks (Left)
        self.stack = QStackedWidget()
        
        self.calc_canvas = CalculusCanvas()
        self.matrix_canvas = MatrixCanvas()
        self.vector_canvas = VectorCanvas()
        self.fourier_canvas = FourierCanvas()
        self.galton_canvas = GaltonCanvas()
        self.galton_canvas.init_bins()

        self.stack.addWidget(self.calc_canvas)
        self.stack.addWidget(self.matrix_canvas)
        self.stack.addWidget(self.vector_canvas)
        self.stack.addWidget(self.fourier_canvas)
        self.stack.addWidget(self.galton_canvas)

        split_layout.addWidget(self.stack, 3)

        # Control Panel Wrapper QFrame (Right side)
        self.control_panel = QFrame()
        self.control_panel.setObjectName("controls_panel")
        self.control_panel.setStyleSheet("""
            QFrame#controls_panel {
                background-color: rgba(20, 21, 38, 0.55); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px;
            }
        """)
        self.control_panel.setFixedWidth(300)
        
        cp_layout = QVBoxLayout(self.control_panel)
        cp_layout.setContentsMargins(0, 0, 0, 0)
        self.panel_layout = QStackedWidget()
        cp_layout.addWidget(self.panel_layout)

        # Panel 1: Calculus Layout
        calc_widget = QWidget()
        calc_layout = QVBoxLayout(calc_widget)
        calc_layout.setContentsMargins(15, 15, 15, 15)
        calc_layout.setSpacing(12)
        
        title_calc = QLabel("Calculus & Graphing")
        title_calc.setFont(QFont("Outfit", 14, QFont.Bold))
        calc_layout.addWidget(title_calc)

        form_c = QFormLayout()
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["sin", "quadratic", "cubic", "gaussian", "damped", "custom"])
        form_c.addRow(QLabel("Preserved Function:"), self.combo_preset)
        self.combo_preset.currentIndexChanged.connect(self.calc_preset_changed)

        self.cust_input = QLineEdit()
        self.cust_input.setText(self.calc_canvas.custom_expr)
        self.cust_input.setEnabled(False)
        self.cust_input.textChanged.connect(self.calc_custom_changed)
        form_c.addRow(QLabel("Custom Eq:"), self.cust_input)
        calc_layout.addLayout(form_c)

        calc_layout.addWidget(QLabel("Lab Mode:"))
        self.btn_m_move = QRadioButton("Inspection Mode")
        self.btn_m_deriv = QRadioButton("Derivative (Tangent)")
        self.btn_m_integ = QRadioButton("Riemann Integral")
        self.btn_m_move.setChecked(True)
        
        mode_grp = QButtonGroup(self)
        for r in [self.btn_m_move, self.btn_m_deriv, self.btn_m_integ]:
            mode_grp.addButton(r)
            calc_layout.addWidget(r)
        self.btn_m_move.toggled.connect(lambda: self.calc_mode_changed('move'))
        self.btn_m_deriv.toggled.connect(lambda: self.calc_mode_changed('derivative'))
        self.btn_m_integ.toggled.connect(lambda: self.calc_mode_changed('integral'))

        # Interactive sliders
        self.slider_tangent = QSlider(Qt.Horizontal)
        self.slider_tangent.setRange(-400, 400)
        self.slider_tangent.setValue(0)
        self.slider_tangent.setEnabled(False)
        self.slider_tangent.valueChanged.connect(self.calc_tangent_slider)
        
        self.lbl_t_val = QLabel("Tangent X: 0.0")
        calc_layout.addWidget(self.lbl_t_val)
        calc_layout.addWidget(self.slider_tangent)

        self.slider_integ_a = QSlider(Qt.Horizontal)
        self.slider_integ_a.setRange(-60, 60)
        self.slider_integ_a.setValue(-40)
        self.slider_integ_a.setEnabled(False)
        self.slider_integ_a.valueChanged.connect(self.calc_integ_slider_a)
        
        self.lbl_a_val = QLabel("Lower bounds a: -4.0")
        calc_layout.addWidget(self.lbl_a_val)
        calc_layout.addWidget(self.slider_integ_a)

        self.slider_integ_b = QSlider(Qt.Horizontal)
        self.slider_integ_b.setRange(-60, 60)
        self.slider_integ_b.setValue(40)
        self.slider_integ_b.setEnabled(False)
        self.slider_integ_b.valueChanged.connect(self.calc_integ_slider_b)

        self.lbl_b_val = QLabel("Upper bounds b: 4.0")
        calc_layout.addWidget(self.lbl_b_val)
        calc_layout.addWidget(self.slider_integ_b)

        self.slider_subdivisions = QSlider(Qt.Horizontal)
        self.slider_subdivisions.setRange(2, 60)
        self.slider_subdivisions.setValue(20)
        self.slider_subdivisions.setEnabled(False)
        self.slider_subdivisions.valueChanged.connect(self.calc_integ_slider_n)

        self.lbl_n_val = QLabel("Subdivisions n: 20")
        calc_layout.addWidget(self.lbl_n_val)
        calc_layout.addWidget(self.slider_subdivisions)
        
        # Readings output
        self.lbl_calc_out = QLabel("")
        self.lbl_calc_out.setWordWrap(True)
        self.lbl_calc_out.setStyleSheet("background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); padding: 10px; border-radius: 8px;")
        calc_layout.addWidget(self.lbl_calc_out)
        
        calc_layout.addStretch()
        self.panel_layout.addWidget(calc_widget)

        # Panel 2: Matrix Layout
        matrix_widget = QWidget()
        matrix_layout = QVBoxLayout(matrix_widget)
        matrix_layout.setContentsMargins(15, 15, 15, 15)
        matrix_layout.setSpacing(12)

        title_matrix = QLabel("Matrix Transformation")
        title_matrix.setFont(QFont("Outfit", 14, QFont.Bold))
        matrix_layout.addWidget(title_matrix)

        grid_i = QGridLayout()
        self.m00 = QDoubleSpinBox()
        self.m01 = QDoubleSpinBox()
        self.m10 = QDoubleSpinBox()
        self.m11 = QDoubleSpinBox()
        for idx, box in enumerate([self.m00, self.m01, self.m10, self.m11]):
            box.setRange(-5.0, 5.0)
            box.setSingleStep(0.2)
            box.setValue([2.0, 1.0, 0.5, 1.5][idx])
            grid_i.addWidget(box, idx // 2, idx % 2)

        matrix_layout.addLayout(grid_i)
        
        btn_anim = QPushButton("Animate Grid Transform")
        btn_anim.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 8px; padding: 8px;")
        btn_anim.clicked.connect(self.matrix_trigger_anim)
        matrix_layout.addWidget(btn_anim)

        # Presets layout
        matrix_layout.addWidget(QLabel("Preset Configurations:"))
        p_identity = QPushButton("Identity")
        p_shear = QPushButton("Shear Grid")
        p_rot = QPushButton("45° Rotation")
        p_scale = QPushButton("LHS Reflection")
        for p in [p_identity, p_shear, p_rot, p_scale]:
            matrix_layout.addWidget(p)
            
        p_identity.clicked.connect(lambda: self.matrix_set_preset(1, 0, 0, 1))
        p_shear.clicked.connect(lambda: self.matrix_set_preset(1.5, 1.0, 0.0, 1.0))
        p_rot.clicked.connect(lambda: self.matrix_set_preset(math.cos(math.pi/4), -math.sin(math.pi/4), math.sin(math.pi/4), math.cos(math.pi/4)))
        p_scale.clicked.connect(lambda: self.matrix_set_preset(-1, 0, 0, 1))

        self.lbl_matrix_out = QLabel("")
        self.lbl_matrix_out.setWordWrap(True)
        self.lbl_matrix_out.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        self.matrix_recalc_outputs()
        matrix_layout.addWidget(self.lbl_matrix_out)

        matrix_layout.addStretch()
        self.panel_layout.addWidget(matrix_widget)

        # Panel 3: Vector Layout
        vec_widget = QWidget()
        vec_layout = QVBoxLayout(vec_widget)
        vec_layout.setContentsMargins(15, 15, 15, 15)
        vec_layout.setSpacing(12)

        title_vec = QLabel("Vector Math Space")
        title_vec.setFont(QFont("Outfit", 14, QFont.Bold))
        vec_layout.addWidget(title_vec)

        # Vector inputs
        self.slider_ax = QSlider(Qt.Horizontal)
        self.slider_ay = QSlider(Qt.Horizontal)
        self.slider_bx = QSlider(Qt.Horizontal)
        self.slider_by = QSlider(Qt.Horizontal)
        
        self.lbl_ax = QLabel("Vector A_x: 4.0")
        self.lbl_ay = QLabel("Vector A_y: 3.0")
        self.lbl_bx = QLabel("Vector B_x: -3.0")
        self.lbl_by = QLabel("Vector B_y: 4.0")

        sliders_list = [
            (self.slider_ax, self.lbl_ax, "A_x", 40),
            (self.slider_ay, self.lbl_ay, "A_y", 30),
            (self.slider_bx, self.lbl_bx, "B_x", -30),
            (self.slider_by, self.lbl_by, "B_y", 40)
        ]
        for s, l, label_name, def_val in sliders_list:
            s.setRange(-60, 60)
            s.setValue(def_val)
            s.valueChanged.connect(self.vec_recalc)
            vec_layout.addWidget(l)
            vec_layout.addWidget(s)

        vec_layout.addWidget(QLabel("Geometric Presets:"))
        btn_ortho = QPushButton("Orthogonal (90°)")
        btn_par = QPushButton("Parallel Collinear")
        btn_opp = QPushButton("Opposite Alignment")

        for b in [btn_ortho, btn_par, btn_opp]:
            vec_layout.addWidget(b)

        btn_ortho.clicked.connect(lambda: self.vec_preset(40, 30, -30, 40))
        btn_par.clicked.connect(lambda: self.vec_preset(30, 20, 60, 40))
        btn_opp.clicked.connect(lambda: self.vec_preset(50, 20, -50, -20))

        self.lbl_vec_out = QLabel("")
        self.lbl_vec_out.setWordWrap(True)
        self.lbl_vec_out.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        vec_layout.addWidget(self.lbl_vec_out)
        self.vec_recalc()

        vec_layout.addStretch()
        self.panel_layout.addWidget(vec_widget)

        # Panel 4: Fourier Synthesizer Panel
        four_widget = QWidget()
        four_layout = QVBoxLayout(four_widget)
        four_layout.setContentsMargins(15, 15, 15, 15)
        four_layout.setSpacing(12)

        title_four = QLabel("Fourier Epicycles")
        title_four.setFont(QFont("Outfit", 14, QFont.Bold))
        four_layout.addWidget(title_four)

        form_f = QFormLayout()
        self.combo_wave = QComboBox()
        self.combo_wave.addItems(["square", "sawtooth", "triangle"])
        self.combo_wave.currentIndexChanged.connect(self.four_settings_changed)
        form_f.addRow(QLabel("Wave Synthesis:"), self.combo_wave)
        four_layout.addLayout(form_f)

        self.slider_harm = QSlider(Qt.Horizontal)
        self.slider_harm.setRange(1, 50)
        self.slider_harm.setValue(10)
        self.slider_harm.valueChanged.connect(self.four_settings_changed)
        self.lbl_harm = QLabel("Harmonics n: 10")
        
        self.slider_f_freq = QSlider(Qt.Horizontal)
        self.slider_f_freq.setRange(5, 30)
        self.slider_f_freq.setValue(10)
        self.slider_f_freq.valueChanged.connect(self.four_settings_changed)
        self.lbl_freq = QLabel("Frequency Multiplier: 1.0x")

        four_layout.addWidget(self.lbl_harm)
        four_layout.addWidget(self.slider_harm)
        four_layout.addWidget(self.lbl_freq)
        four_layout.addWidget(self.slider_f_freq)

        self.lbl_four_eq = QLabel("")
        self.lbl_four_eq.setWordWrap(True)
        self.lbl_four_eq.setStyleSheet("background: rgba(0,0,0,0.2); font-family: monospace; font-size: 11px; padding: 10px; border-radius: 8px;")
        four_layout.addWidget(self.lbl_four_eq)
        self.update_four_formula_label()

        four_layout.addStretch()
        self.panel_layout.addWidget(four_widget)

        # Panel 5: Galton statistics Board panel
        gal_widget = QWidget()
        gal_layout = QVBoxLayout(gal_widget)
        gal_layout.setContentsMargins(15, 15, 15, 15)
        gal_layout.setSpacing(12)

        title_gal = QLabel("Galton probability")
        title_gal.setFont(QFont("Outfit", 14, QFont.Bold))
        gal_layout.addWidget(title_gal)

        self.slider_pegs = QSlider(Qt.Horizontal)
        self.slider_pegs.setRange(6, 12)
        self.slider_pegs.setValue(9)
        self.slider_pegs.valueChanged.connect(self.galton_pegs_changed)
        self.lbl_pegs = QLabel("Peg board rows: 9")
        gal_layout.addWidget(self.lbl_pegs)
        gal_layout.addWidget(self.slider_pegs)

        self.slider_elast = QSlider(Qt.Horizontal)
        self.slider_elast.setRange(10, 80)
        self.slider_elast.setValue(50)
        self.slider_elast.valueChanged.connect(self.galton_elast_changed)
        self.lbl_elast = QLabel("Peg elasticity: 0.50")
        gal_layout.addWidget(self.lbl_elast)
        gal_layout.addWidget(self.slider_elast)

        btn_drop = QPushButton("Drop Single Ball")
        btn_drop.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 8px; padding: 8px;")
        btn_drop.clicked.connect(self.galton_canvas.trigger_single_drop)
        gal_layout.addWidget(btn_drop)

        self.btn_auto_drop = QPushButton("Auto Drop: OFF")
        self.btn_auto_drop.clicked.connect(self.galton_toggle_auto)
        gal_layout.addWidget(self.btn_auto_drop)

        btn_clear = QPushButton("Clear Distributions")
        btn_clear.clicked.connect(self.galton_canvas.init_bins)
        gal_layout.addWidget(btn_clear)

        self.lbl_gal_out = QLabel("")
        self.lbl_gal_out.setWordWrap(True)
        self.lbl_gal_out.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        gal_layout.addWidget(self.lbl_gal_out)

        # Start stats loop timer
        self.gal_stats_timer = QTimer(self)
        self.gal_stats_timer.timeout.connect(self.galton_update_stats)
        self.gal_stats_timer.start(250)

        gal_layout.addStretch()
        self.panel_layout.addWidget(gal_widget)

        # Core splitter addition
        split_layout.addWidget(self.control_panel)
        main_layout.addLayout(split_layout)

        # Tab Index mappings
        self.btn_calc.clicked.connect(lambda: self.change_sub_tab(0))
        self.btn_matrix.clicked.connect(lambda: self.change_sub_tab(1))
        self.btn_vector.clicked.connect(lambda: self.change_sub_tab(2))
        self.btn_fourier.clicked.connect(lambda: self.change_sub_tab(3))
        self.btn_galton.clicked.connect(lambda: self.change_sub_tab(4))

        # Initial recalc
        self.calc_recalc_outputs()

    def change_sub_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        self.panel_layout.setCurrentIndex(idx)

    # ---------------- CALCULUS BINDINGS ----------------
    def calc_preset_changed(self, idx):
        self.calc_canvas.selected_func = self.combo_preset.currentText()
        self.cust_input.setEnabled(self.calc_canvas.selected_func == "custom")
        self.calc_canvas.update()
        self.calc_recalc_outputs()

    def calc_custom_changed(self, text):
        self.calc_canvas.custom_expr = text
        self.calc_canvas.update()
        self.calc_recalc_outputs()

    def calc_mode_changed(self, mode):
        self.calc_canvas.active_mode = mode
        self.slider_tangent.setEnabled(mode == 'derivative')
        self.slider_integ_a.setEnabled(mode == 'integral')
        self.slider_integ_b.setEnabled(mode == 'integral')
        self.slider_subdivisions.setEnabled(mode == 'integral')
        self.calc_canvas.update()
        self.calc_recalc_outputs()

    def calc_tangent_slider(self, val):
        self.calc_canvas.tangent_x = val / 100.0
        self.lbl_t_val.setText(f"Tangent X: {self.calc_canvas.tangent_x:.2f}")
        self.calc_canvas.update()
        self.calc_recalc_outputs()

    def calc_integ_slider_a(self, val):
        self.calc_canvas.integral_a = val / 10.0
        self.lbl_a_val.setText(f"Lower bounds a: {self.calc_canvas.integral_a:.1f}")
        self.calc_canvas.update()
        self.calc_recalc_outputs()

    def calc_integ_slider_b(self, val):
        self.calc_canvas.integral_b = val / 10.0
        self.lbl_b_val.setText(f"Upper bounds b: {self.calc_canvas.integral_b:.1f}")
        self.calc_canvas.update()
        self.calc_recalc_outputs()

    def calc_integ_slider_n(self, val):
        self.calc_canvas.integral_n = val
        self.lbl_n_val.setText(f"Subdivisions n: {val}")
        self.calc_canvas.update()
        self.calc_recalc_outputs()

    def calc_recalc_outputs(self):
        c = self.calc_canvas
        if c.active_mode == 'move':
            self.lbl_calc_out.setText(f"<b>Inspector readout</b><br>Move mouse over grid area to display local coordinates. Scroll to zoom.")
        elif c.active_mode == 'derivative':
            x0 = c.tangent_x
            try:
                y0 = c.get_y_val(x0)
                eps = 0.0001
                y1 = c.get_y_val(x0 + eps)
                y_1 = c.get_y_val(x0 - eps)
                slope = (y1 - y_1) / (2 * eps)
                intercept = y0 - slope * x0
                self.lbl_calc_out.setText(
                    f"<b>Coordinates:</b> ({x0:.2f}, {y0:.2f})<br>"
                    f"<b>Slope dy/dx:</b> <span style='color:#00e5ff; font-weight:bold;'>{slope:.4f}</span><br>"
                    f"<b>Angle:</b> {(math.atan(slope)*180/math.pi):.1f}°<br>"
                    f"<b>Tangent line:</b><br><span style='font-family: monospace; font-size: 11px;'>y = {slope:.2f}x {'+' if intercept>=0 else '-'} {abs(intercept):.2f}</span>"
                )
            except:
                self.lbl_calc_out.setText("Evaluation Error.")
        elif c.active_mode == 'integral':
            a = min(c.integral_a, c.integral_b)
            b = max(c.integral_a, c.integral_b)
            n = c.integral_n
            dx = (b - a)/n
            sum_area = 0.0
            for i in range(n):
                x_mid = a + (i + 0.5)*dx
                sum_area += c.get_y_val(x_mid)*dx
            self.lbl_calc_out.setText(
                f"<b>Bounds:</b> [{a:.1f}, {b:.1f}]<br>"
                f"<b>Step width dx:</b> {dx:.4f}<br>"
                f"<b>Riemann Sum:</b><br><span style='color:#00e5ff; font-size:16px; font-weight:bold;'>A ≈ {sum_area:.5f}</span>"
            )

    # ---------------- MATRIX BINDINGS ----------------
    def matrix_trigger_anim(self):
        m = self.matrix_canvas
        m.matrix = [[self.m00.value(), self.m01.value()], [self.m10.value(), self.m11.value()]]
        m.start_animation()
        self.matrix_recalc_outputs()

    def matrix_set_preset(self, val00, val01, val10, val11):
        self.m00.setValue(val00)
        self.m01.setValue(val01)
        self.m10.setValue(val10)
        self.m11.setValue(val11)
        self.matrix_trigger_anim()

    def matrix_recalc_outputs(self):
        m00, m01, m10, m11 = self.m00.value(), self.m01.value(), self.m10.value(), self.m11.value()
        det = m00*m11 - m01*m10
        out = f"<b>Determinant (Det A):</b><br><span style='color:#00ff88; font-weight:bold; font-size:14px;'>{det:.3f}</span><br>"
        if abs(det) < 0.001:
            out += "Matrix is Singular (No Inverse)"
        else:
            scale = 1.0 / det
            out += f"<b>Matrix Inverse:</b><br>| {m11*scale:.3f}  {-m01*scale:.3f} |<br>| {-m10*scale:.3f}  {m00*scale:.3f} |"
        self.lbl_matrix_out.setText(out)

    # ---------------- VECTOR BINDINGS ----------------
    def vec_preset(self, ax, ay, bx, by):
        self.slider_ax.setValue(ax)
        self.slider_ay.setValue(ay)
        self.slider_bx.setValue(bx)
        self.slider_by.setValue(by)
        self.vec_recalc()

    def vec_recalc(self):
        ax = self.slider_ax.value() / 10.0
        ay = self.slider_ay.value() / 10.0
        bx = self.slider_bx.value() / 10.0
        by = self.slider_by.value() / 10.0

        self.vector_canvas.ax = ax
        self.vector_canvas.ay = ay
        self.vector_canvas.bx = bx
        self.vector_canvas.by = by
        self.vector_canvas.update()

        self.lbl_ax.setText(f"Vector A_x: {ax:.1f}")
        self.lbl_ay.setText(f"Vector A_y: {ay:.1f}")
        self.lbl_bx.setText(f"Vector B_x: {bx:.1f}")
        self.lbl_by.setText(f"Vector B_y: {by:.1f}")

        # Vector calculations
        dot = ax*bx + ay*by
        cross_mag = ax*by - ay*bx
        mag_a = math.hypot(ax, ay)
        mag_b = math.hypot(bx, by)
        
        angle_deg = 0.0
        if mag_a > 0 and mag_b > 0:
            cos_theta = max(-1.0, min(1.0, dot / (mag_a * mag_b)))
            angle_deg = math.acos(cos_theta) * 180.0 / math.pi
            
        sum_x = ax + bx
        sum_y = ay + by

        self.lbl_vec_out.setText(
            f"<b>Vectors:</b> A=({ax:.1f},{ay:.1f}), B=({bx:.1f},{by:.1f})<br>"
            f"<b>Sum A+B:</b> ({sum_x:.1f}, {sum_y:.1f})<br>"
            f"<b>Dot Product (A·B):</b> {dot:.3f}<br>"
            f"<b>Cross Product (AxB)_z:</b> {cross_mag:.3f}<br>"
            f"<b>Separation Angle:</b> {angle_deg:.1f}°"
        )

    # ---------------- FOURIER BINDINGS ----------------
    def four_settings_changed(self):
        f = self.fourier_canvas
        f.wave_type = self.combo_wave.currentText()
        f.harmonics = self.slider_harm.value()
        self.lbl_harm.setText(f"Harmonics n: {f.harmonics}")

        freq_val = self.slider_f_freq.value() / 10.0
        f.freq = freq_val
        self.lbl_freq.setText(f"Frequency Multiplier: {freq_val:.1f}x")
        self.update_four_formula_label()

    def update_four_formula_label(self):
        w_type = self.combo_wave.currentText()
        if w_type == 'square':
            self.lbl_four_eq.setText("y(t) = ∑_{k=1..N} (4/π(2k-1)) * sin((2k-1)wt)\n\nFades 1/n slope.")
        elif w_type == 'sawtooth':
            self.lbl_four_eq.setText("y(t) = ∑_{k=1..N} (2/πn) * (-1)^(n+1) * sin(nwt)\n\nFull harmonic synthesizer decay.")
        elif w_type == 'triangle':
            self.lbl_four_eq.setText("y(t) = ∑_{k=1..N} (8/π²n²) * (-1)^((n-1)/2) * sin(nwt)\n\nVery fast 1/n² harmonic falloff.")

    # ---------------- GALTON BINDINGS ----------------
    def galton_pegs_changed(self, val):
        self.galton_canvas.rows = val
        self.lbl_pegs.setText(f"Peg board rows: {val}")
        self.galton_canvas.init_bins()

    def galton_elast_changed(self, val):
        self.galton_canvas.elasticity = val / 100.0
        self.lbl_elast.setText(f"Peg elasticity: {self.galton_canvas.elasticity:.2f}")

    def galton_toggle_auto(self):
        self.galton_canvas.autodrop = not self.galton_canvas.autodrop
        self.btn_auto_drop.setText("Auto Drop: ON" if self.galton_canvas.autodrop else "Auto Drop: OFF")

    def galton_update_stats(self):
        bins = self.galton_canvas.bins
        n_balls = self.galton_canvas.accumulated
        if n_balls == 0:
            self.lbl_gal_out.setText("<b>Statistics Bucket</b><br>No balls dropped yet.")
            return

        # Calculate mean bucket index
        weighted_sum = sum(i * count for i, count in enumerate(bins))
        mean = weighted_sum / n_balls
        
        # Standard deviation
        variance = sum(count * (i - mean)**2 for i, count in enumerate(bins)) / n_balls
        std_dev = math.sqrt(variance)

        self.lbl_gal_out.setText(
            f"<b>Statistical Distributions:</b><br>"
            f"<b>Accumulated Drops:</b> {n_balls}<br>"
            f"<b>Mean Bin Node:</b> {mean:.2f}<br>"
            f"<b>Standard Deviation:</b> {std_dev:.3f}<br>"
            f"<i>Follows Binomial Probability limit.</i>"
        )
