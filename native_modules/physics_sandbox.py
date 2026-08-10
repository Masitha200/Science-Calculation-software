import math
import random
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPolygonF, QRadialGradient, QLinearGradient
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame, QComboBox, QSlider,
                             QRadioButton, QButtonGroup, QLineEdit, QStackedWidget, QFormLayout)

# ----------------- Tab 1: Projectile Dynamics Canvas -----------------
class ProjectileCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.reset()
        
        # Params
        self.v0 = 25.0
        self.angle = 45.0
        self.gravity = 9.8
        self.drag_coeff = 0.05
        self.init_height = 0.0

    def reset(self):
        self.timer.stop()
        self.t = 0.0
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.path = []
        self.is_running = False
        self.max_height = 0.0
        self.range = 0.0
        self.flight_time = 0.0
        self.update()

    def start_sim(self):
        self.reset()
        rad = math.radians(self.angle)
        self.vx = self.v0 * math.cos(rad)
        self.vy = self.v0 * math.sin(rad)
        self.y = self.init_height
        self.is_running = True
        self.timer.start(20) # 50 FPS

    def toggle_pause(self):
        if self.is_running:
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start(20)

    def tick(self):
        dt = 0.03 # timestep
        self.t += dt
        
        # Velocity magnitude
        v = math.hypot(self.vx, self.vy)
        
        # Physics-stabilized drag term (prevents direction reversal/explosion)
        if v > 0:
            decel = self.drag_coeff * v * dt
            if decel >= 1.0:
                self.vx = 0.0
                self.vy = 0.0
            else:
                self.vx *= (1.0 - decel)
                self.vy *= (1.0 - decel)
                
        # Apply gravity acceleration
        self.vy -= self.gravity * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        if self.y > self.max_height:
            self.max_height = self.y
            
        self.path.append(QPointF(self.x, self.y))
        
        # Landing detector
        if self.y <= 0.0:
            self.y = 0.0
            self.range = self.x
            self.flight_time = self.t
            self.is_running = False
            self.timer.stop()
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        
        # Dark viewport background
        painter.fillRect(self.rect(), QColor(9, 9, 21))
        
        # Coordinate scaling variables
        cx = 40.0
        cy = h - 60.0
        zoom = (w - 80.0) / 100.0 if w > 100 else 5.0
        zoom_y = (h - 100.0) / 45.0 if h > 100 else 5.0
        zoom = min(zoom, zoom_y)  # keep aspect scaling uniform

        # Grid guidelines
        painter.setPen(QPen(QColor(255, 255, 255, 12), 1))
        for g_x in range(0, 110, 10):
            px = cx + g_x * zoom
            painter.drawLine(int(px), 0, int(px), int(cy))
        for g_y in range(0, 50, 5):
            py = cy - g_y * zoom
            painter.drawLine(int(cx), int(py), w, int(py))

        # Ground line and Y axis
        painter.setPen(QPen(QColor(255, 255, 255, 60), 2))
        painter.drawLine(0, int(cy), w, int(cy))
        painter.drawLine(int(cx), 0, int(cx), h)

        # Plot launch base element
        painter.setBrush(QBrush(QColor(100, 116, 139)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(int(cx - 5), int(cy - self.init_height * zoom), 10, int(self.init_height * zoom))

        # Draw trace path
        if len(self.path) > 1:
            painter.setPen(QPen(QColor(0, 229, 255), 2))
            painter.setBrush(Qt.NoBrush)
            poly_pts = [QPointF(cx + p.x() * zoom, cy - p.y() * zoom) for p in self.path]
            painter.drawPolyline(QPolygonF(poly_pts))

        # Drifting bullet particle
        cur_px = cx + self.x * zoom
        cur_py = cy - self.y * zoom
        painter.setBrush(QBrush(QColor(189, 0, 255)))
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawEllipse(QPointF(cur_px, cur_py), 5, 5)


# ----------------- Tab 2: Single Pendulum Canvas -----------------
class PendulumCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        
        # Params
        self.length = 2.0  # meters
        self.mass = 1.0  # kg
        self.gravity = 9.8
        self.damping = 0.05
        
        # Initial angles and bob states
        self.theta = math.radians(45.0)
        self.omega = 0.0
        self.is_dragging = False

        self.timer.start(20) # 50 FPS

    def tick(self):
        if self.is_dragging:
            return
            
        dt = 0.02
        # Angular acceleration: alpha = -(g/L)*sin(theta) - damping*omega
        alpha = -(self.gravity / self.length) * math.sin(self.theta) - self.damping * self.omega
        self.omega += alpha * dt
        self.theta += self.omega * dt
        
        self.update()

    def get_energy(self):
        # Potential Energy = m * g * h
        # h = L - L*cos(theta)
        h = self.length * (1.0 - math.cos(self.theta))
        pe = self.mass * self.gravity * h
        # Kinetic Energy = 0.5 * m * v^2 where v = omega * L
        v = self.omega * self.length
        ke = 0.5 * self.mass * v * v
        return ke, pe

    def mousePressEvent(self, event):
        # Determine mouse distance to bob
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, 50.0
        zoom = 100.0  # pixels/meter
        
        bob_x = cx + (self.length * zoom) * math.sin(self.theta)
        bob_y = cy + (self.length * zoom) * math.cos(self.theta)
        
        dist = math.hypot(event.x() - bob_x, event.y() - bob_y)
        if dist < 20.0:
            self.is_dragging = True

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            w = self.width()
            cx = w / 2.0
            cy = 50.0
            
            dx = event.x() - cx
            dy = event.y() - cy
            # Calculate angle theta from cursor position
            self.theta = math.atan2(dx, dy)
            self.omega = 0.0 # damp momentum
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, 50.0
        zoom = 100.0 # scale pixels per meter

        # Viewport background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Draw ceiling anchor block
        painter.setPen(QPen(QColor(148, 163, 184), 2))
        painter.drawLine(int(cx - 30), int(cy), int(cx + 30), int(cy))

        # Bob location coordinates
        rx = cx + (self.length * zoom) * math.sin(self.theta)
        ry = cy + (self.length * zoom) * math.cos(self.theta)

        # Draw string line
        painter.setPen(QPen(QColor(255, 255, 255, 120), 2))
        painter.drawLine(QPointF(cx, cy), QPointF(rx, ry))

        # Draw Bob circle
        # Draw Bob circle
        bob_radius = 8.0 + self.mass * 3.0
        painter.setBrush(QBrush(QColor(0, 229, 255)))
        painter.setPen(QPen(QColor(255, 255, 255), 1.5))
        painter.drawEllipse(QPointF(rx, ry), bob_radius, bob_radius)


# ----------------- Tab 3: Double Pendulum (Chaos) Canvas -----------------
class DoublePendulumCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        
        # Params
        self.l1 = 1.2
        self.l2 = 1.0
        self.m1 = 1.5
        self.m2 = 1.2
        self.gravity = 9.8
        self.trail_len = 150

        # State
        self.theta1 = math.radians(90.0)
        self.theta2 = math.radians(90.0)
        self.omega1 = 0.0
        self.omega2 = 0.0
        self.trail = []

        self.timer.start(16) # ~60 FPS

    def reset_sim(self):
        self.theta1 = math.radians(90.0)
        self.theta2 = math.radians(90.0)
        self.omega1 = 0.0
        self.omega2 = 0.0
        self.trail.clear()
        self.update()

    def get_equations(self, th1, th2, w1, w2):
        g = self.gravity
        m1, m2 = self.m1, self.m2
        l1, l2 = self.l1, self.l2

        delta = th1 - th2

        den1 = l1 * (2*m1 + m2 - m2*math.cos(2*th1 - 2*th2))
        num1 = -g*(2*m1 + m2)*math.sin(th1) - m2*g*math.sin(th1 - 2*th2) - 2*math.sin(delta)*m2*(w2*w2*l2 + w1*w1*l1*math.cos(delta))
        alpha1 = num1 / den1

        den2 = l2 * (2*m1 + m2 - m2*math.cos(2*th1 - 2*th2))
        num2 = 2*math.sin(delta)*(w1*w1*l1*(m1 + m2) + g*(m1 + m2)*math.cos(th1) + w2*w2*l2*m2*math.cos(delta))
        alpha2 = num2 / den2

        return w1, alpha1, w2, alpha2

    def tick(self):
        dt = 0.02
        
        # Runge-Kutta 4th Order ode integrations steps
        th1, th2, w1, w2 = self.theta1, self.theta2, self.omega1, self.omega2

        dw1_1, dw2_1, dw3_1, dw4_1 = self.get_equations(th1, th2, w1, w2)
        
        th1_k2 = th1 + 0.5 * dt * dw1_1
        th2_k2 = th2 + 0.5 * dt * dw3_1
        w1_k2 = w1 + 0.5 * dt * dw2_1
        w2_k2 = w2 + 0.5 * dt * dw4_1
        dw1_2, dw2_2, dw3_2, dw4_2 = self.get_equations(th1_k2, th2_k2, w1_k2, w2_k2)

        th1_k3 = th1 + 0.5 * dt * dw1_2
        th2_k3 = th2 + 0.5 * dt * dw3_2
        w1_k3 = w1 + 0.5 * dt * dw2_2
        w2_k3 = w2 + 0.5 * dt * dw4_2
        dw1_3, dw2_3, dw3_3, dw4_3 = self.get_equations(th1_k3, th2_k3, w1_k3, w2_k3)

        th1_k4 = th1 + dt * dw1_3
        th2_k4 = th2 + dt * dw3_3
        w1_k4 = w1 + dt * dw2_3
        w2_k4 = w2 + dt * dw4_3
        dw1_4, dw2_4, dw3_4, dw4_4 = self.get_equations(th1_k4, th2_k4, w1_k4, w2_k4)

        self.theta1 += (dt / 6.0) * (dw1_1 + 2*dw1_2 + 2*dw1_3 + dw1_4)
        self.omega1 += (dt / 6.0) * (dw2_1 + 2*dw2_2 + 2*dw2_3 + dw2_4)
        self.theta2 += (dt / 6.0) * (dw3_1 + 2*dw3_2 + 2*dw3_3 + dw3_4)
        self.omega2 += (dt / 6.0) * (dw4_1 + 2*dw4_2 + 2*dw4_3 + dw4_4)

        # Pendulum cartesian tips locations
        x1 = self.l1 * math.sin(self.theta1)
        y1 = self.l1 * math.cos(self.theta1)
        x2 = x1 + self.l2 * math.sin(self.theta2)
        y2 = y1 + self.l2 * math.cos(self.theta2)

        self.trail.append(QPointF(x2, y2))
        if len(self.trail) > self.trail_len:
            self.trail.pop(0)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.5
        zoom = 95.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Position points mapping
        x1 = cx + (self.l1 * zoom) * math.sin(self.theta1)
        y1 = cy + (self.l1 * zoom) * math.cos(self.theta1)
        x2 = cx + (self.l1 * zoom) * math.sin(self.theta1) + (self.l2 * zoom) * math.sin(self.theta2)
        y2 = cy + (self.l1 * zoom) * math.cos(self.theta1) + (self.l2 * zoom) * math.cos(self.theta2)

        # Draw fading chaos path trail
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                opacity = int((i / len(self.trail)) * 180)
                trail_color = QColor(189, 0, 255, opacity)
                painter.setPen(QPen(trail_color, 1.5))
                pt1 = self.trail[i]
                pt2 = self.trail[i+1]
                painter.drawLine(QPointF(cx + pt1.x()*zoom, cy + pt1.y()*zoom), QPointF(cx + pt2.x()*zoom, cy + pt2.y()*zoom))

        # Rods
        painter.setPen(QPen(QColor(255, 255, 255, 80), 2))
        painter.drawLine(QPointF(cx, cy), QPointF(x1, y1))
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Bobs
        painter.setPen(Qt.NoPen)
        # Joint 1
        painter.setBrush(QBrush(QColor(0, 229, 255)))
        painter.drawEllipse(QPointF(x1, y1), int(6 + self.m1*2), int(6 + self.m1*2))
        # Joint 2 (Chaos Tip)
        painter.setBrush(QBrush(QColor(255, 174, 0)))
        painter.drawEllipse(QPointF(x2, y2), int(6 + self.m2*2), int(6 + self.m2*2))


# ----------------- Tab 4: Ray Optics Lab Canvas -----------------
class RayOpticsCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.focal_length = 3.0  # focal length (positive = convex, negative = concave)
        self.obj_dist = 5.0     # object distance
        self.obj_height = 1.5   # object height
        
        self.is_dragging_obj = False
        self.is_dragging_lens = False
        self.mouse_coords = (0.0, 0.0)

    def mousePressEvent(self, event):
        w, h = self.width(), self.height()
        cx = w / 2.0
        cy = h / 2.0
        zoom = 35.0

        # Object coordinate position
        obj_x = cx - self.obj_dist * zoom
        obj_y = cy - self.obj_height * zoom
        
        if math.hypot(event.x() - obj_x, event.y() - obj_y) < 20.0:
            self.is_dragging_obj = True
        elif abs(event.x() - cx) < 15.0:
            self.is_dragging_lens = True

    def mouseReleaseEvent(self, event):
        self.is_dragging_obj = False
        self.is_dragging_lens = False

    def mouseMoveEvent(self, event):
        w, h = self.width(), self.height()
        cx = w / 2.0
        cy = h / 2.0
        zoom = 35.0
        
        dx = (event.x() - cx) / zoom
        dy = -(event.y() - cy) / zoom
        self.mouse_coords = (dx, dy)

        if self.is_dragging_obj:
            # Update object distance (keep it negative on left side)
            self.obj_dist = max(1.0, min(10.0, -dx))
            self.obj_height = max(0.5, min(4.0, dy))
            self.update()
        elif self.is_dragging_lens:
            pass  # we keep lens static at center for coordinate simplicity

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx = w / 2.0
        cy = h / 2.0
        zoom = 35.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Optical principal axis
        painter.setPen(QPen(QColor(255, 255, 255, 60), 2))
        painter.drawLine(0, int(cy), w, int(cy))

        # Thin lens body line (convex vertical loop)
        painter.setPen(QPen(QColor(0, 229, 255), 3))
        painter.drawLine(int(cx), 30, int(cx), h - 30)
        # Convex lens design arrows headers
        painter.drawLine(int(cx), 30, int(cx - 8), 38)
        painter.drawLine(int(cx), 30, int(cx + 8), 38)
        painter.drawLine(int(cx), h - 30, int(cx - 8), h - 38)
        painter.drawLine(int(cx), h - 30, int(cx + 8), h - 38)

        # Focal points indicators (F and 2F on both sides)
        f = self.focal_length
        painter.setBrush(QBrush(QColor(189, 0, 255)))
        painter.setPen(Qt.NoPen)
        for side in [-1, 1]:
            # Focus points
            painter.drawEllipse(QPointF(cx + side*f*zoom, cy), 4.0, 4.0)
            painter.drawEllipse(QPointF(cx + side*2*f*zoom, cy), 4.0, 4.0)

        # Draw Object Arrow
        obj_x = cx - self.obj_dist * zoom
        obj_y = cy - self.obj_height * zoom
        painter.setPen(QPen(QColor(0, 255, 136), 3.0)) # green object
        painter.drawLine(int(obj_x), int(cy), int(obj_x), int(obj_y))
        # Arrowhead
        painter.drawLine(int(obj_x), int(obj_y), int(obj_x - 5), int(obj_y + 8))
        painter.drawLine(int(obj_x), int(obj_y), int(obj_x + 5), int(obj_y + 8))

        # Thin lens calculations: 1/f = 1/do + 1/di -> di = 1 / (1/f - 1/do)
        do = self.obj_dist
        di = 0.0
        real_image = True
        
        if abs(do - f) < 0.02:
            di = 999.0 # parallel rays focus at infinity
        else:
            di = 1.0 / (1.0/f - 1.0/do)

        img_height = -self.obj_height * di / do
        img_x = cx + di * zoom
        img_y = cy - img_height * zoom

        # Draw traced light rays
        ray_pen_parallel = QPen(QColor(234, 88, 12, 200), 1.5)
        ray_pen_focal = QPen(QColor(250, 204, 21, 200), 1.5)
        ray_pen_center = QPen(QColor(168, 85, 247, 200), 1.5)

        # Ray 1: Parallel -> lens -> Focus
        painter.setPen(ray_pen_parallel)
        painter.drawLine(QPointF(obj_x, obj_y), QPointF(cx, obj_y))
        if do > f:
            painter.drawLine(QPointF(cx, obj_y), QPointF(cx + f*zoom, cy))
            painter.drawLine(QPointF(cx + f*zoom, cy), QPointF(img_x, img_y))
        else:
            # Virtual diverge trace line
            painter.drawLine(QPointF(cx, obj_y), QPointF(cx + f*zoom, cy))
            # dashed extension back
            painter.setPen(QPen(QColor(234, 88, 12, 80), 1, Qt.DashLine))
            painter.drawLine(QPointF(cx, obj_y), QPointF(img_x, img_y))

        # Ray 2: Source center node
        painter.setPen(ray_pen_center)
        painter.drawLine(QPointF(obj_x, obj_y), QPointF(cx, cy))
        if do > f:
            painter.drawLine(QPointF(cx, cy), QPointF(img_x, img_y))
        else:
            painter.setPen(QPen(QColor(168, 85, 247, 80), 1, Qt.DashLine))
            painter.drawLine(QPointF(cx, cy), QPointF(img_x, img_y))

        # Draw Image arrow if distance is not infinite
        if abs(di) < 25.0:
            image_color = QColor(0, 229, 255) if di > 0 else QColor(255, 174, 0)
            painter.setPen(QPen(image_color, 3.0))
            painter.drawLine(int(img_x), int(cy), int(img_x), int(img_y))
            # Arrowhead depending on inversion
            side_y = 8 if img_height < 0 else -8
            painter.drawLine(int(img_x), int(img_y), int(img_x - 5), int(img_y + side_y))
            painter.drawLine(int(img_x), int(img_y), int(img_x + 5), int(img_y + side_y))


# ----------------- Tab 5: Keplerian Orbits Canvas (Orbital) -----------------
class OrbitalCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        
        # Params
        self.star_mass = 100.0
        self.init_vel = 4.2
        self.radius = 3.0

        self.reset()
        self.timer.start(16) # ~60 FPS

    def reset(self):
        self.x = self.radius
        self.y = 0.0
        self.vx = 0.0
        self.vy = self.init_vel
        self.trail = []
        self.update()

    def tick(self):
        # Gravity acceleration: a = -G * M * r_vec / |r|^3
        dt = 0.04
        r = math.hypot(self.x, self.y)
        if r < 0.2:
            self.reset()
            return
            
        accel = -self.star_mass / (r*r*r)
        ax = accel * self.x
        ay = accel * self.y
        
        self.vx += ax * dt
        self.vy += ay * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        self.trail.append(QPointF(self.x, self.y))
        if len(self.trail) > 200:
            self.trail.pop(0)
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        zoom = 50.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Concentric gravity well coordinate rings
        painter.setPen(QPen(QColor(255, 255, 255, 10), 1))
        painter.setBrush(Qt.NoBrush)
        for r in [1.5, 3.0, 4.5, 6.0]:
            painter.drawEllipse(QPointF(cx, cy), int(r * zoom), int(r * zoom))

        # Central Star (radial glow)
        star_glow = QRadialGradient(cx, cy, 35)
        star_glow.setColorAt(0.0, QColor(253, 224, 71, 240))
        star_glow.setColorAt(0.3, QColor(250, 204, 21, 140))
        star_glow.setColorAt(1.0, QColor(250, 204, 21, 0))
        painter.setBrush(QBrush(star_glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 35, 35)

        # Star Core
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QPointF(cx, cy), 8, 8)

        # Plot Orbit Trail
        if len(self.trail) > 1:
            painter.setPen(QPen(QColor(0, 229, 255, 120), 1.5))
            painter.setBrush(Qt.NoBrush)
            poly_pts = [QPointF(cx + pt.x()*zoom, cy - pt.y()*zoom) for pt in self.trail]
            painter.drawPolyline(QPolygonF(poly_pts))

        # Draw revolving Planet
        px = cx + self.x * zoom
        py = cy - self.y * zoom
        
        # Planet glow
        planet_glow = QRadialGradient(px, py, 11)
        planet_glow.setColorAt(0.0, QColor(0, 255, 136, 255))
        planet_glow.setColorAt(0.4, QColor(0, 255, 136, 100))
        planet_glow.setColorAt(1.0, QColor(0, 255, 136, 0))
        painter.setBrush(QBrush(planet_glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(px, py), 11, 11)
        
        # planet core
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QPointF(px, py), 4.5, 4.5)


# ----------------- Physics Tab Sandbox Container View -----------------
class PhysicsSandboxView(QWidget):
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

        self.btn_proj = QPushButton("Projectile Kinematics")
        self.btn_proj.setObjectName("subtab-proj")
        self.btn_pend = QPushButton("Oscillation Lab")
        self.btn_pend.setObjectName("subtab-pend")
        self.btn_dbl = QPushButton("Double Pendulum")
        self.btn_dbl.setObjectName("subtab-dbl")
        self.btn_optics = QPushButton("Ray Optics Lab")
        self.btn_optics.setObjectName("subtab-opt")
        self.btn_orbit = QPushButton("Orbital Sandbox")
        self.btn_orbit.setObjectName("subtab-orbit")

        self.subtab_group = QButtonGroup(self)
        for btn in [self.btn_proj, self.btn_pend, self.btn_dbl, self.btn_optics, self.btn_orbit]:
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            self.subtab_group.addButton(btn)
            sub_layout.addWidget(btn)
        sub_layout.addStretch()

        self.btn_proj.setChecked(True)
        main_layout.addWidget(self.subtab_bar)

        # 2. Main content area
        split_layout = QHBoxLayout()
        split_layout.setContentsMargins(5, 5, 5, 5)
        split_layout.setSpacing(15)

        # Canvas Stack on left
        self.stack = QStackedWidget()
        self.proj_canvas = ProjectileCanvas()
        self.pend_canvas = PendulumCanvas()
        self.dbl_canvas = DoublePendulumCanvas()
        self.optics_canvas = RayOpticsCanvas()
        self.orbit_canvas = OrbitalCanvas()

        self.stack.addWidget(self.proj_canvas)
        self.stack.addWidget(self.pend_canvas)
        self.stack.addWidget(self.dbl_canvas)
        self.stack.addWidget(self.optics_canvas)
        self.stack.addWidget(self.orbit_canvas)

        split_layout.addWidget(self.stack, 3)

        # Control Panel on right
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

        # Panel 1: Projectile Controls
        proj_widget = QWidget()
        proj_lay = QVBoxLayout(proj_widget)
        proj_lay.setContentsMargins(15, 15, 15, 15)
        proj_lay.setSpacing(12)

        proj_title = QLabel("Projectile Motion")
        proj_title.setFont(QFont("Outfit", 14, QFont.Bold))
        proj_lay.addWidget(proj_title)

        # Inputs
        self.sl_pv0 = QSlider(Qt.Horizontal)
        self.sl_pang = QSlider(Qt.Horizontal)
        self.sl_pg = QSlider(Qt.Horizontal)
        self.sl_pdrag = QSlider(Qt.Horizontal)
        self.sl_ph = QSlider(Qt.Horizontal)

        self.lbl_pv0 = QLabel("Initial Velocity: 25.0 m/s")
        self.lbl_pang = QLabel("Launch Angle: 45.0°")
        self.lbl_pg = QLabel("Gravity: 9.8 m/s²")
        self.lbl_pdrag = QLabel("Air Drag: 0.05")
        self.lbl_ph = QLabel("Launch Height: 0.0 m")

        sliders = [
            (self.sl_pv0, self.lbl_pv0, 5, 45, 25, "Initial Velocity: {:.1f} m/s"),
            (self.sl_pang, self.lbl_pang, 0, 90, 45, "Launch Angle: {:.1f}°"),
            (self.sl_pg, self.lbl_pg, 2, 25, 9.8, "Gravity: {:.1f} m/s²"),
            (self.sl_pdrag, self.lbl_pdrag, 0.0, 0.30, 0.05, "Air Drag: {:.2f}"),
            (self.sl_ph, self.lbl_ph, 0, 20, 0, "Launch Height: {:.1f} m")
        ]

        for s, l, minv, maxv, defv, fmt in sliders:
            s.setRange(int(minv * 100), int(maxv * 100))
            s.setValue(int(defv * 100))
            s.valueChanged.connect(self.proj_params_changed)
            proj_lay.addWidget(l)
            proj_lay.addWidget(s)

        # Sim control buttons
        btn_start = QPushButton("Launcher Fire")
        btn_start.setCursor(Qt.PointingHandCursor)
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; color: white; font-weight: bold; padding: 10px; border-radius: 8px; border: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_start.clicked.connect(self.proj_canvas.start_sim)
        
        btn_pause = QPushButton("Pause")
        btn_pause.setCursor(Qt.PointingHandCursor)
        btn_pause.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08); color: white; font-weight: bold; padding: 8px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        btn_pause.clicked.connect(self.proj_canvas.toggle_pause)
        
        btn_reset = QPushButton("Reset")
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15); color: #ef4444; font-weight: bold; padding: 8px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.25);
            }
        """)
        btn_reset.clicked.connect(self.proj_canvas.reset)
        
        proj_lay.addWidget(btn_start)
        
        sub_btn_lay = QHBoxLayout()
        sub_btn_lay.setSpacing(10)
        sub_btn_lay.addWidget(btn_pause)
        sub_btn_lay.addWidget(btn_reset)
        proj_lay.addLayout(sub_btn_lay)

        # HUD feedback
        self.lbl_proj_hud = QLabel("")
        self.lbl_proj_hud.setWordWrap(True)
        self.lbl_proj_hud.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        proj_lay.addWidget(self.lbl_proj_hud)
        
        self.proj_hud_timer = QTimer(self)
        self.proj_hud_timer.timeout.connect(self.proj_update_hud)
        self.proj_hud_timer.start(100)

        proj_lay.addStretch()
        self.panel_layout.addWidget(proj_widget)

        # Panel 2: Pendulum Controls
        pend_widget = QWidget()
        pend_lay = QVBoxLayout(pend_widget)
        pend_lay.setContentsMargins(15, 15, 15, 15)
        pend_lay.setSpacing(12)

        pend_title = QLabel("Oscillation Lab")
        pend_title.setFont(QFont("Outfit", 14, QFont.Bold))
        pend_lay.addWidget(pend_title)

        self.sl_pl = QSlider(Qt.Horizontal)
        self.sl_pm = QSlider(Qt.Horizontal)
        self.sl_pgrav = QSlider(Qt.Horizontal)
        self.sl_pdamp = QSlider(Qt.Horizontal)

        self.lbl_pl = QLabel("String Length: 2.0 m")
        self.lbl_pm = QLabel("Bob Weight: 1.0 kg")
        self.lbl_pgrav = QLabel("Local Gravity: 9.8 m/s²")
        self.lbl_pdamp = QLabel("Air Damping: 0.05")

        sliders_p = [
            (self.sl_pl, self.lbl_pl, 1, 3.5, 2.0, "String Length: {:.1f} m", "length"),
            (self.sl_pm, self.lbl_pm, 0.2, 3.0, 1.0, "Bob Weight: {:.1f} kg", "mass"),
            (self.sl_pgrav, self.lbl_pgrav, 1.0, 20.0, 9.8, "Local Gravity: {:.1f} m/s²", "gravity"),
            (self.sl_pdamp, self.lbl_pdamp, 0.0, 0.5, 0.05, "Air Damping: {:.2f}", "damping")
        ]

        for s, l, minv, maxv, defv, fmt, prop in sliders_p:
            s.setRange(int(minv * 100), int(maxv * 100))
            s.setValue(int(defv * 100))
            s.valueChanged.connect(lambda val, prop=prop, l=l, fmt=fmt: self.pend_params_changed(val, prop, l, fmt))
            pend_lay.addWidget(l)
            pend_lay.addWidget(s)

        # Energy stats
        self.lbl_pend_stats = QLabel("")
        self.lbl_pend_stats.setWordWrap(True)
        self.lbl_pend_stats.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        pend_lay.addWidget(self.lbl_pend_stats)

        self.pend_hud_timer = QTimer(self)
        self.pend_hud_timer.timeout.connect(self.pend_update_hud)
        self.pend_hud_timer.start(100)

        # Interactive Hint
        hint = QLabel("<i>Hint: Grab the blue bob with the mouse cursor to drag choose starting deflection angle.</i>")
        hint.setFont(QFont("Outfit", 9))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #94a3b8;")
        pend_lay.addWidget(hint)

        pend_lay.addStretch()
        self.panel_layout.addWidget(pend_widget)

        # Panel 3: Double Pendulum
        dbl_widget = QWidget()
        dbl_lay = QVBoxLayout(dbl_widget)
        dbl_lay.setContentsMargins(15, 15, 15, 15)
        dbl_lay.setSpacing(12)

        dbl_title = QLabel("Double Pendulum")
        dbl_title.setFont(QFont("Outfit", 14, QFont.Bold))
        dbl_lay.addWidget(dbl_title)

        self.sl_l1 = QSlider(Qt.Horizontal)
        self.sl_l2 = QSlider(Qt.Horizontal)
        self.sl_m1 = QSlider(Qt.Horizontal)
        self.sl_m2 = QSlider(Qt.Horizontal)

        self.lbl_l1 = QLabel("Rod 1 Height: 1.2 m")
        self.lbl_l2 = QLabel("Rod 2 Height: 1.0 m")
        self.lbl_m1 = QLabel("Bob 1 Weight: 1.5 kg")
        self.lbl_m2 = QLabel("Bob 2 Weight: 1.2 kg")

        sliders_d = [
            (self.sl_l1, self.lbl_l1, 0.5, 2.0, 1.2, "Rod 1 Height: {:.1f} m", "l1"),
            (self.sl_l2, self.lbl_l2, 0.5, 2.0, 1.0, "Rod 2 Height: {:.1f} m", "l2"),
            (self.sl_m1, self.lbl_m1, 0.5, 3.0, 1.5, "Bob 1 Weight: {:.1f} kg", "m1"),
            (self.sl_m2, self.lbl_m2, 0.5, 3.0, 1.2, "Bob 2 Weight: {:.1f} kg", "m2")
        ]

        for s, l, minv, maxv, defv, fmt, prop in sliders_d:
            s.setRange(int(minv * 100), int(maxv * 100))
            s.setValue(int(defv * 100))
            s.valueChanged.connect(lambda val, prop=prop, l=l, fmt=fmt: self.dbl_params_changed(val, prop, l, fmt))
            dbl_lay.addWidget(l)
            dbl_lay.addWidget(s)

        btn_dbl_reset = QPushButton("Reset Chaos positions")
        btn_dbl_reset.setCursor(Qt.PointingHandCursor)
        btn_dbl_reset.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15); color: #ef4444; font-weight: bold; padding: 10px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.25);
            }
        """)
        btn_dbl_reset.clicked.connect(self.dbl_canvas.reset_sim)
        dbl_lay.addWidget(btn_dbl_reset)

        dbl_lay.addWidget(QLabel("<i>Renders connected RK4 (Runge-Kutta 4th degree) differential integration steps. Trail shows chaotic motion limit.</i>"))

        dbl_lay.addStretch()
        self.panel_layout.addWidget(dbl_widget)

        # Panel 4: Ray Optics Controls
        opt_widget = QWidget()
        opt_lay = QVBoxLayout(opt_widget)
        opt_lay.setContentsMargins(15, 15, 15, 15)
        opt_lay.setSpacing(12)

        opt_title = QLabel("Ray Optics Lab")
        opt_title.setFont(QFont("Outfit", 14, QFont.Bold))
        opt_lay.addWidget(opt_title)

        self.sl_foc = QSlider(Qt.Horizontal)
        self.sl_foc.setRange(150, 500)
        self.sl_foc.setValue(300)
        self.sl_foc.valueChanged.connect(self.optics_params_changed)
        
        self.lbl_foc_val = QLabel("Focal Length f: 3.0")
        opt_lay.addWidget(self.lbl_foc_val)
        opt_lay.addWidget(self.sl_foc)

        opt_lay.addWidget(QLabel("Lens Converging Preset:"))
        btn_convex = QPushButton("Convex (+) Lens")
        btn_convex.setCursor(Qt.PointingHandCursor)
        btn_convex.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 229, 255, 0.15); color: #00e5ff; font-weight: bold; padding: 8px; border-radius: 8px; border: 1px solid rgba(0, 229, 255, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(0, 229, 255, 0.25);
            }
        """)
        
        btn_concave = QPushButton("Concave (-) Lens")
        btn_concave.setCursor(Qt.PointingHandCursor)
        btn_concave.setStyleSheet("""
            QPushButton {
                background-color: rgba(189, 0, 255, 0.15); color: #bd00ff; font-weight: bold; padding: 8px; border-radius: 8px; border: 1px solid rgba(189, 0, 255, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(189, 0, 255, 0.25);
            }
        """)
        
        btn_convex.clicked.connect(lambda: self.optics_set_lens(3.0))
        btn_concave.clicked.connect(lambda: self.optics_set_lens(-3.0))
        
        opt_lay.addWidget(btn_convex)
        opt_lay.addWidget(btn_concave)

        # HUD feedback
        self.lbl_optics_hud = QLabel("")
        self.lbl_optics_hud.setWordWrap(True)
        self.lbl_optics_hud.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        opt_lay.addWidget(self.lbl_optics_hud)
        
        self.optics_hud_timer = QTimer(self)
        self.optics_hud_timer.timeout.connect(self.optics_update_hud)
        self.optics_hud_timer.start(100)

        opt_lay.addWidget(QLabel("<i>Constraint: Click & Drag visual green arrow (object) tip to resize height and distance.</i>"))

        opt_lay.addStretch()
        self.panel_layout.addWidget(opt_widget)

        # Panel 5: Keplerian Orbit Panel
        orb_widget = QWidget()
        orb_lay = QVBoxLayout(orb_widget)
        orb_lay.setContentsMargins(15, 15, 15, 15)
        orb_lay.setSpacing(12)

        orb_title = QLabel("Orbital Simulator")
        orb_title.setFont(QFont("Outfit", 14, QFont.Bold))
        orb_lay.addWidget(orb_title)

        self.sl_star = QSlider(Qt.Horizontal)
        self.sl_star.setRange(500, 3000)
        self.sl_star.setValue(1000)
        self.sl_star.valueChanged.connect(self.orbit_params_changed)
        self.lbl_os = QLabel("Sun mass: 100.0")

        self.sl_vel = QSlider(Qt.Horizontal)
        self.sl_vel.setRange(20, 80)
        self.sl_vel.setValue(42)
        self.sl_vel.valueChanged.connect(self.orbit_params_changed)
        self.lbl_ov = QLabel("Orbital starts velocity: 4.2")

        orb_lay.addWidget(self.lbl_os)
        orb_lay.addWidget(self.sl_star)
        orb_lay.addWidget(self.lbl_ov)
        orb_lay.addWidget(self.sl_vel)

        btn_orb_reset = QPushButton("Reset orbit path")
        btn_orb_reset.setCursor(Qt.PointingHandCursor)
        btn_orb_reset.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15); color: #ef4444; font-weight: bold; padding: 10px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.25);
            }
        """)
        btn_orb_reset.clicked.connect(self.orbit_canvas.reset)
        orb_lay.addWidget(btn_orb_reset)

        orb_lay.addWidget(QLabel("<i>Simulates gravitational Kepler/Newton vector orbits. Velocity presets determine circular, elliptical or hyperbolic paths.</i>"))

        orb_lay.addStretch()
        self.panel_layout.addWidget(orb_widget)

        # Core additions
        split_layout.addWidget(self.control_panel)
        main_layout.addLayout(split_layout)

        # Button signals
        self.btn_proj.clicked.connect(lambda: self.change_sub_tab(0))
        self.btn_pend.clicked.connect(lambda: self.change_sub_tab(1))
        self.btn_dbl.clicked.connect(lambda: self.change_sub_tab(2))
        self.btn_optics.clicked.connect(lambda: self.change_sub_tab(3))
        self.btn_orbit.clicked.connect(lambda: self.change_sub_tab(4))

    def change_sub_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        self.panel_layout.setCurrentIndex(idx)

    # ---------------- PROJECTILE LOGIC ----------------
    def proj_params_changed(self):
        c = self.proj_canvas
        c.v0 = self.sl_pv0.value() / 100.0
        c.angle = self.sl_pang.value() / 100.0
        c.gravity = self.sl_pg.value() / 100.0
        c.drag_coeff = self.sl_pdrag.value() / 100.0
        c.init_height = self.sl_ph.value() / 100.0

        self.lbl_pv0.setText(f"Initial Velocity: {c.v0:.1f} m/s")
        self.lbl_pang.setText(f"Launch Angle: {c.angle:.1f}°")
        self.lbl_pg.setText(f"Gravity: {c.gravity:.1f} m/s²")
        self.lbl_pdrag.setText(f"Air Drag: {c.drag_coeff:.2f}")
        self.lbl_ph.setText(f"Launch Height: {c.init_height:.1f} m")

    def proj_update_hud(self):
        c = self.proj_canvas
        self.lbl_proj_hud.setText(
            f"<b>Simulation Coordinates:</b><br>"
            f"Position X: {c.x:.2f} m<br>"
            f"Position Y: {c.y:.2f} m<br>"
            f"Velocity X: {c.vx:.2f} m/s<br>"
            f"Velocity Y: {c.vy:.2f} m/s<br><br>"
            f"<b>Flight Milestones:</b><br>"
            f"Max Peak Height: {c.max_height:.2f} m<br>"
            f"Landing Distance: {c.range:.2f} m<br>"
            f"Total Flight Time: {c.flight_time:.2f} s"
        )

    # ---------------- PENDULUM LOGIC ----------------
    def pend_params_changed(self, val, prop, lbl, fmt):
        c = self.pend_canvas
        setattr(c, prop, val / 100.0)
        lbl.setText(fmt.format(val / 100.0))

    def pend_update_hud(self):
        c = self.pend_canvas
        ke, pe = c.get_energy()
        te = ke + pe
        
        # Theoretical oscillation period: T = 2*pi * sqrt(L/g)
        period = 2.0 * math.pi * math.sqrt(c.length / c.gravity)
        
        self.lbl_pend_stats.setText(
            f"<b>Dynamic Energy Readouts:</b><br>"
            f"Kinetic Energy: {ke:.3f} J<br>"
            f"Potential Energy: {pe:.3f} J<br>"
            f"Total State Energy: {te:.3f} J<br>"
            f"Theta Offset: {math.degrees(c.theta):.1f}°<br><br>"
            f"<b>Period Solver (T):</b><br>"
            f"Theoretical: {period:.2f} s"
        )

    # ---------------- DOUBLE PENDULUM ----------------
    def dbl_params_changed(self, val, prop, lbl, fmt):
        c = self.dbl_canvas
        setattr(c, prop, val / 100.0)
        lbl.setText(fmt.format(val / 100.0))

    # ---------------- RAY OPTICS BINDINGS ----------------
    def optics_params_changed(self):
        c = self.optics_canvas
        c.focal_length = self.sl_foc.value() / 100.0
        self.lbl_foc_val.setText(f"Focal Length f: {c.focal_length:.2f}")
        c.update()

    def optics_set_lens(self, f):
        self.sl_foc.setValue(int(f * 100))
        self.optics_params_changed()

    def optics_update_hud(self):
        c = self.optics_canvas
        
        # Recalc thin lens formula characteristics
        do = c.obj_dist
        f = c.focal_length
        m = 0.0
        
        if f > 0:
            lens_t = "Convex (Converging)"
            if abs(do - f) < 0.05:
                di_str = "Infinity (Parallel Rays)"
                image_t = "No Image (At Focus)"
            else:
                di = 1.0 / (1.0/f - 1.0/do)
                di_str = f"{di:.2f} units"
                m = -di / do
                image_t = "Real & Inverted" if di > 0 else "Virtual & Erect"
        else:
            lens_t = "Concave (Diverging)"
            di = 1.0 / (1.0/f - 1.0/do)
            di_str = f"{di:.2f} units"
            m = -di / do
            image_t = "Virtual & Erect (Shrunk)"

        self.lbl_optics_hud.setText(
            f"<b>Lens Profile:</b> {lens_t}<br>"
            f"Object Distance: {do:.2f} units<br>"
            f"Image Distance: {di_str}<br>"
            f"System Magnification (m): {m:.2f}x<br>"
            f"Image Standard Type: {image_t}"
        )

    # ---------------- ORBIT Sandbox LOGIC ----------------
    def orbit_params_changed(self):
        c = self.orbit_canvas
        c.star_mass = self.sl_star.value() / 10.0
        c.init_vel = self.sl_vel.value() / 10.0
        
        self.lbl_os.setText(f"Sun mass: {c.star_mass:.1f}")
        self.lbl_ov.setText(f"Orbital starts velocity: {c.init_vel:.1f}")


