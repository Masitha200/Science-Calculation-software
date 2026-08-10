import math
import random
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPolygonF, QRadialGradient
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame, QComboBox, QSlider,
                             QRadioButton, QButtonGroup, QLineEdit, QStackedWidget, QFormLayout)

# ----------------- Tab 1: Bohr Atomic Model Canvas -----------------
class BohrCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.atomic_number = 1
        self.element_name = "Hydrogen"
        self.transition_active = False
        self.transition_t = 0.0
        self.transition_delta = 0  # 1 = absorb (n1->n2), -1 = emit (n2->n1)
        self.photon_x = 0.0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(25) # ~40 FPS

        self.time = 0.0

    def trigger_excitation(self):
        if not self.transition_active:
            self.transition_active = True
            self.transition_t = 0.0
            self.transition_delta = 1 # n=1 to n=3 excitation
            self.photon_x = -200.0

    def trigger_emission(self):
        if not self.transition_active:
            self.transition_active = True
            self.transition_t = 0.0
            self.transition_delta = -1 # n=3 to n=1 decay
            self.photon_x = 0.0 # start at electron

    def tick(self):
        self.time += 0.05
        if self.transition_active:
            self.transition_t += 0.02
            if self.transition_t >= 1.0:
                self.transition_active = False
                self.transition_t = 0.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0

        # Viewport Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Shell radii
        radius_1 = 50.0
        radius_2 = 90.0
        radius_3 = 135.0

        # Draw concentric orbits dashed lines & semi-transparent colored glow paths
        painter.setPen(QPen(QColor(59, 130, 246, 30), 2))
        painter.drawEllipse(QPointF(cx, cy), radius_1, radius_1)
        painter.setPen(QPen(QColor(189, 0, 255, 30), 2))
        painter.drawEllipse(QPointF(cx, cy), radius_2, radius_2)
        painter.setPen(QPen(QColor(0, 255, 136, 30), 2))
        painter.drawEllipse(QPointF(cx, cy), radius_3, radius_3)

        orb_pen = QPen(QColor(255, 255, 255, 15), 1, Qt.DashLine)
        painter.setPen(orb_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), radius_1, radius_1)
        painter.drawEllipse(QPointF(cx, cy), radius_2, radius_2)
        painter.drawEllipse(QPointF(cx, cy), radius_3, radius_3)
        
        # Label orbits
        painter.setPen(QPen(QColor(255, 255, 255, 60)))
        painter.setFont(QFont("Outfit", 8))
        painter.drawText(int(cx + radius_1 + 5), int(cy + 4), "n=1")
        painter.drawText(int(cx + radius_2 + 5), int(cy + 4), "n=2")
        painter.drawText(int(cx + radius_3 + 5), int(cy + 4), "n=3")

        # Nucleus fusion core background glow
        fusion_glow = QRadialGradient(cx, cy, 32)
        fusion_glow.setColorAt(0.0, QColor(99, 102, 241, 150))
        fusion_glow.setColorAt(0.5, QColor(168, 85, 247, 50))
        fusion_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(fusion_glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 32, 32)

        # Draw Nucleus (Protons/Neutrons clustered at center)
        random.seed(42)  # consistent cluster positions
        n_particles = max(3, self.atomic_number * 2)
        for i in range(n_particles):
            color = QColor(239, 68, 68) if i % 2 == 0 else QColor(59, 130, 246) # red proton, blue neutron
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            ox = cx + random.uniform(-10, 10)
            oy = cy + random.uniform(-10, 10)
            painter.drawEllipse(QPointF(ox, oy), 8, 8)

        # Distribute electrons (max 10: 2 in shell 1, 8 in shell 2)
        electrons_count = self.atomic_number
        electrons = []

        # Electron configuration helper
        in_s1 = min(2, electrons_count)
        in_s2 = min(8, electrons_count - in_s1)
        
        # Draw electrons revolving
        for i in range(in_s1):
            angle = (i * 2.0 * math.pi / max(1, in_s1)) + self.time
            ex = cx + radius_1 * math.cos(angle)
            ey = cy + radius_1 * math.sin(angle)
            electrons.append((ex, ey, 1))

        # Dynamic transition simulation logic for election 1 in shell 1/3
        active_r = radius_1
        if self.transition_active:
            if self.transition_delta == 1:
                # n=1 to n=3 interpolation
                active_r = radius_1 + (radius_3 - radius_1) * self.transition_t
            else:
                # n=3 to n=1 interpolation
                active_r = radius_3 - (radius_3 - radius_1) * self.transition_t
        
        for i in range(in_s2):
            angle = (i * 2.0 * math.pi / max(1, in_s2)) - 0.7 * self.time
            ex = cx + radius_2 * math.cos(angle)
            ey = cy + radius_2 * math.sin(angle)
            electrons.append((ex, ey, 2))

        # Modify first electron if transition is active
        if electrons:
            ex_t, ey_t, shell = electrons[0]
            angle = self.time # current angle
            ex_t = cx + active_r * math.cos(angle)
            ey_t = cy + active_r * math.sin(angle)
            electrons[0] = (ex_t, ey_t, shell)

        # Draw electrons as active yellow glowing particles
        for ex, ey, shell in electrons:
            elec_glow = QRadialGradient(ex, ey, 9)
            elec_glow.setColorAt(0.0, QColor(250, 204, 21, 255))
            elec_glow.setColorAt(0.4, QColor(250, 204, 21, 120))
            elec_glow.setColorAt(1.0, QColor(250, 204, 21, 0))
            painter.setBrush(QBrush(elec_glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(ex, ey), 9, 9)
            
            # central bright electron core
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPointF(ex, ey), 3.5, 3.5)

        # Draw Photon excitation wave
        if self.transition_active:
            if self.transition_delta == 1:
                # Photon incoming wave (sine wave)
                wp_x = cx + self.photon_x
                wp_y = cy
                self.photon_x = -200.0 + self.transition_t * 200.0
                
                # Draw squiggly green photon line
                painter.setPen(QPen(QColor(0, 255, 136), 1.5))
                pts = []
                for sx in range(int(wp_x - 30), int(wp_x + 30)):
                    sy = wp_y + 10 * math.sin((sx - wp_x) * 0.15)
                    pts.append(QPointF(sx, sy))
                if len(pts) > 1:
                    painter.drawPolyline(QPolygonF(pts))
            else:
                # Photon outgoing wave (sine wave) escaping
                wp_x = cx + self.photon_x
                wp_y = cy
                self.photon_x = self.transition_t * 200.0
                
                painter.setPen(QPen(QColor(244, 63, 94), 1.5)) # red photon emitted
                pts = []
                for sx in range(int(wp_x - 30), int(wp_x + 30)):
                    sy = wp_y + 10 * math.sin((sx - wp_x) * 0.15)
                    pts.append(QPointF(sx, sy))
                if len(pts) > 1:
                    painter.drawPolyline(QPolygonF(pts))


# ----------------- Tab 2: Acid Base Titration Laboratory Canvas -----------------
class TitrationCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titrant_vol = 0.0          # Base added in mL
        self.analyte_vol = 25.0         # Acid volume
        self.indicator = "Phenolphthalein"
        self.acid_ph = 1.5
        self.equivalence_pt = 22.0      # volume of base required for equivalence
        self.drops = []                 # active drops animation details
        self.titrant_normality = 0.1
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(25)

    def add_drop(self):
        w = max(400, self.width())
        cx = w / 2.0
        self.drops.append({'x': cx, 'y': 80.0, 'vy': 4.0})

    def tick(self):
        h = self.height()
        active_drops = []
        for drop in self.drops:
            drop['y'] += drop['vy']
            # Collision with liquid beaker top boundary
            if drop['y'] >= h - 110.0:
                # Add to volume
                self.titrant_vol = min(40.0, self.titrant_vol + 0.15)
            else:
                active_drops.append(drop)
        self.drops = active_drops
        self.update()

    def get_ph(self):
        # Calculate titration curve pH using Henderson-Hasselbalch equivalent logic
        vol_eq = self.equivalence_pt
        V_b = self.titrant_vol
        
        if V_b < vol_eq:
            # Excess acid remains
            unreacted = (vol_eq - V_b) / vol_eq
            # pH ranges from initial ~1.5 to ~5 near equivalence
            ph = self.acid_ph - math.log10(max(0.0001, unreacted))
        elif abs(V_b - vol_eq) < 0.1:
            # Equivalence point
            ph = 7.0
        else:
            # Excess base
            excess_ratio = (V_b - vol_eq) / 10.0
            # pH jumps to basic range
            ph = 12.0 + math.log10(max(1.0, 1.0 + excess_ratio))
            
        return max(1.0, min(14.0, ph))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx = w / 2.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # 1. Draw Glass Burette structure
        painter.setPen(QPen(QColor(148, 163, 184, 180), 2))
        painter.setBrush(Qt.NoBrush)
        # Burette body
        painter.drawRect(int(cx - 8), 10, 16, 70)
        # Burette valve nozzle
        poly_n = QPolygonF([QPointF(cx - 3, 80), QPointF(cx + 3, 80), QPointF(cx, 95)])
        painter.setBrush(QBrush(QColor(148, 163, 184)))
        painter.drawPolygon(poly_n)

        # 2. Draw Titration Liquid drops falling
        painter.setBrush(QBrush(QColor(0, 229, 255, 200)))
        painter.setPen(Qt.NoPen)
        for d in self.drops:
            painter.drawEllipse(QPointF(d['x'], d['y']), 3, 4)

        # 3. Draw Beaker holding analyte
        beaker_pen = QPen(QColor(255, 255, 255, 120), 2)
        painter.setPen(beaker_pen)
        painter.setBrush(Qt.NoBrush)

        beaker_w = 90.0
        beaker_h = 100.0
        bx = cx - beaker_w / 2.0
        by = h - beaker_h - 20.0

        # Draw Beaker glass borders
        painter.drawLine(int(bx), int(by), int(bx), int(by + beaker_h))
        painter.drawLine(int(bx), int(by + beaker_h), int(bx + beaker_w), int(by + beaker_h))
        painter.drawLine(int(bx + beaker_w), int(by), int(bx + beaker_w), int(by + beaker_h))

        # 4. Fill Beaker liquid dynamically changing color depending on pH
        ph = self.get_ph()
        liquid_h = 45.0 + (self.titrant_vol / 40.0) * 20.0
        
        # Color mapping: Phenolphthalein is clear in acid (pH<8.2), bright pink in base (pH>8.2)
        if self.indicator == "Phenolphthalein":
            if ph < 8.2:
                # Faint clear water like color
                liq_color = QColor(14, 165, 233, 40)
            else:
                # Transition pink glow
                alpha = int(40 + (ph - 8.2) * 45)
                alpha = max(40, min(180, alpha))
                liq_color = QColor(236, 72, 153, alpha)
        else: # Litmus
            # Red in acid, blue in base
            if ph < 7.0:
                liq_color = QColor(239, 68, 68, 100)
            else:
                liq_color = QColor(59, 130, 246, 100)

        painter.setBrush(QBrush(liq_color))
        painter.drawRect(int(bx + 2), int(by + beaker_h - liquid_h), int(beaker_w - 4), int(liquid_h - 1))


# ----------------- Tab 3: Ideal Gas Law Simulator Canvas -----------------
class GasLawCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temperature = 300.0        # Kelvin
        self.volume = 1.0              # scaling factor
        self.n_moles = 0.5             # quantity
        
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(25) # ~40 FPS
        self.sync_particles()

    def sync_particles(self):
        target_count = int(self.n_moles * 80)
        # Add particles if needed
        while len(self.particles) < target_count:
            # Random position within bounds
            self.particles.append({
                'x': random.uniform(20.0, 180.0),
                'y': random.uniform(20.0, 180.0),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1)
            })
        # Trim if too many
        while len(self.particles) > target_count:
            self.particles.pop()

    def tick(self):
        w, h = self.width(), self.height()
        if w < 10 or h < 10:
            return
            
        box_w = 40.0 + self.volume * 220.0
        box_h = 180.0
        
        # Temp affects speed scale factor
        speed_factor = math.sqrt(self.temperature / 100.0) * 1.5

        bx1, bx2 = (w - box_w)/2.0, (w + box_w)/2.0
        by1, by2 = (h - box_h)/2.0, (h + box_h)/2.0

        for p in self.particles:
            p['x'] += p['vx'] * speed_factor
            p['y'] += p['vy'] * speed_factor

            # Left/Right collision
            if p['x'] <= bx1 + 4:
                p['x'] = bx1 + 4
                p['vx'] = abs(p['vx'])
            elif p['x'] >= bx2 - 4:
                p['x'] = bx2 - 4
                p['vx'] = -abs(p['vx'])

            # Top/Bottom collision
            if p['y'] <= by1 + 4:
                p['y'] = by1 + 4
                p['vy'] = abs(p['vy'])
            elif p['y'] >= by2 - 4:
                p['y'] = by2 - 4
                p['vy'] = -abs(p['vy'])

        self.update()

    def get_pressure(self):
        # P = nRT/V
        # R = 0.0821 gas constant
        p = (self.n_moles * 0.0821 * self.temperature) / self.volume
        return p

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Draw container box outline
        box_w = 40.0 + self.volume * 220.0
        box_h = 180.0
        bx1, bx2 = (w - box_w)/2.0, (w + box_w)/2.0
        by1, by2 = (h - box_h)/2.0, (h + box_h)/2.0

        # Draw container frame
        painter.setPen(QPen(QColor(255, 255, 255, 120), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(bx1), int(by1), int(box_w), int(box_h))

        # Gas Particles
        painter.setPen(Qt.NoPen)
        for p in self.particles:
            # Color shifts depending on temperature
            color_temp = QColor(0, 229, 255) if self.temperature < 250 else (QColor(239, 68, 68) if self.temperature > 400 else QColor(0, 255, 136))
            painter.setBrush(QBrush(color_temp))
            painter.drawEllipse(QPointF(p['x'], p['y']), 3.5, 3.5)

        # Draw physical Analog Pressure Gauge Dial on the right
        g_cx = w - 75.0
        g_cy = cy
        g_r = 45.0

        if w > 420: # Only draw if there's enough horizontal width
            # Dial outer ring
            painter.setPen(QPen(QColor(255, 255, 255, 60), 2))
            painter.setBrush(QBrush(QColor(15, 23, 42)))
            painter.drawEllipse(QPointF(g_cx, g_cy), g_r, g_r)

            # Dial tick marks (e.g. 0 to 100 in steps of 10)
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
            for i in range(11):
                tick_angle = math.radians(-135.0 + i * 27.0 - 90.0)
                # Outer tick point
                x1 = g_cx + (g_r - 2) * math.cos(tick_angle)
                y1 = g_cy + (g_r - 2) * math.sin(tick_angle)
                # Inner tick point
                x2 = g_cx + (g_r - 6) * math.cos(tick_angle)
                y2 = g_cy + (g_r - 6) * math.sin(tick_angle)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            # Draw "P (atm)" labels inside
            painter.setPen(QPen(QColor(148, 163, 184)))
            painter.setFont(QFont("Outfit", 7, QFont.Bold))
            painter.drawText(QRectF(g_cx - g_r, g_cy + 12, g_r*2, 15), Qt.AlignCenter, "P (atm)")

            # Draw needle pointer
            p_val = self.get_pressure()
            # map p_val from 0 to 100 atm onto -135 to +135 deg
            needle_angle_deg = -135.0 + (min(100.0, p_val) / 100.0) * 270.0
            needle_angle_rad = math.radians(needle_angle_deg - 90.0)
            
            # Draw needle pointer line (bright orange-red)
            painter.setPen(QPen(QColor(239, 68, 68), 2))
            nx = g_cx + (g_r - 10) * math.cos(needle_angle_rad)
            ny = g_cy + (g_r - 10) * math.sin(needle_angle_rad)
            painter.drawLine(QPointF(g_cx, g_cy), QPointF(nx, ny))

            # Draw central cap pin
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPointF(g_cx, g_cy), 4, 4)


# ----------------- Tab 5: Chemical Kinetics Canvas -----------------
class KineticsCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temperature = 300.0
        self.activation_energy = 50.0  # limit
        self.reactant_a = 30
        self.reactant_b = 30
        self.product_ab = 0
        
        self.particles = []
        self.history = []  # trace records of reactants counts
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        
        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self.record_state)
        
        self.reset_sim()
        self.timer.start(25) # ~40 FPS
        self.record_timer.start(500) # every 500ms

    def reset_sim(self):
        self.particles.clear()
        self.history.clear()
        self.product_ab = 0
        
        # Populate A Reactants (Red)
        for _ in range(self.reactant_a):
            self.particles.append({
                'type': 'A',
                'x': random.uniform(20, 230),
                'y': random.uniform(20, 150),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1)
            })
        # Populate B Reactants (Green)
        for _ in range(self.reactant_b):
            self.particles.append({
                'type': 'B',
                'x': random.uniform(20, 230),
                'y': random.uniform(20, 150),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1)
            })
        self.update()

    def record_state(self):
        # count particles
        count_a = sum(1 for p in self.particles if p['type'] == 'A')
        count_b = sum(1 for p in self.particles if p['type'] == 'B')
        count_ab = self.product_ab
        self.history.append({'a': count_a, 'b': count_b, 'ab': count_ab})
        if len(self.history) > 120:
            self.history.pop(0)

    def tick(self):
        w, h = self.width(), self.height()
        if w < 10 or h < 10:
            return
            
        boundary_w = 260.0
        boundary_h = 170.0
        bx1, bx2 = 20.0, 20.0 + boundary_w
        by1, by2 = 20.0, 20.0 + boundary_h

        # Motion speed scale
        speed_factor = math.sqrt(self.temperature / 100.0) * 1.6

        # Move particles
        for p in self.particles:
            p['x'] += p['vx'] * speed_factor
            p['y'] += p['vy'] * speed_factor

            # Wall Collisions
            if p['x'] <= bx1:
                p['x'] = bx1
                p['vx'] = abs(p['vx'])
            elif p['x'] >= bx2:
                p['x'] = bx2
                p['vx'] = -abs(p['vx'])

            if p['y'] <= by1:
                p['y'] = by1
                p['vy'] = abs(p['vy'])
            elif p['y'] >= by2:
                p['y'] = by2
                p['vy'] = -abs(p['vy'])

        # Collisions reactions detector (A + B -> AB)
        indices_to_remove = set()
        new_ab_particles = []

        for i in range(len(self.particles)):
            if i in indices_to_remove:
                continue
            for j in range(i + 1, len(self.particles)):
                if j in indices_to_remove:
                    continue
                p1 = self.particles[i]
                p2 = self.particles[j]
                
                # Verify match of reactants and not products
                if p1['type'] != p2['type'] and p1['type'] in ('A', 'B') and p2['type'] in ('A', 'B'):
                    # Distance check
                    dist = math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])
                    if dist < 8.0:
                        # Collision! Check if combined energy exceeds Activation Energy
                        # We simulate relative speed velocity as kinetic energy indicator
                        rel_vx = p1['vx'] * speed_factor - p2['vx'] * speed_factor
                        rel_vy = p1['vy'] * speed_factor - p2['vy'] * speed_factor
                        combined_ke = 12.0 * (rel_vx*rel_vx + rel_vy*rel_vy) # arb constant multiplier
                        
                        if combined_ke >= self.activation_energy:
                            # Reaction succeeds!
                            indices_to_remove.add(i)
                            indices_to_remove.add(j)
                            new_ab_particles.append({
                                'type': 'AB',
                                'x': (p1['x'] + p2['x']) / 2.0,
                                'y': (p1['y'] + p2['y']) / 2.0,
                                'vx': (p1['vx'] + p2['vx']) / 2.0,
                                'vy': (p1['vy'] + p2['vy']) / 2.0
                            })
                            self.product_ab += 1
                            break

        # Apply removal and append AB
        self.particles = [p for idx, p in enumerate(self.particles) if idx not in indices_to_remove]
        self.particles.extend(new_ab_particles)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Reactor sandbox frame (draw on left side)
        boundary_w = 260.0
        boundary_h = 170.0
        bx1, bx2 = 20.0, 20.0 + boundary_w
        by1, by2 = 20.0, 20.0 + boundary_h

        painter.setPen(QPen(QColor(255, 255, 255, 60), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(bx1), int(by1), int(boundary_w), int(boundary_h))

        # Draw reactant particles
        painter.setPen(Qt.NoPen)
        for p in self.particles:
            if p['type'] == 'A':
                painter.setBrush(QBrush(QColor(239, 68, 68))) # red
            elif p['type'] == 'B':
                painter.setBrush(QBrush(QColor(0, 255, 136))) # green
            else:
                painter.setBrush(QBrush(QColor(250, 204, 21))) # AB product (yellow)
            painter.drawEllipse(QPointF(p['x'], p['y']), 4, 4)

        # Draw kinetics Concentration Graph on right side
        gx = bx2 + 30.0
        gy = by1
        gw = w - gx - 20.0
        gh = boundary_h
        
        if gw > 30:
            # Graph axes
            painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
            painter.drawRect(int(gx), int(gy), int(gw), int(gh))
            
            # Trace curves A (red), B (green), AB (yellow)
            if len(self.history) > 1:
                total_reactants = self.reactant_a + self.reactant_b # e.g. 60
                
                pts_a = []
                pts_b = []
                pts_ab = []
                
                space_x = gw / max(1.0, float(len(self.history) - 1))
                
                for idx, record in enumerate(self.history):
                    rx = gx + idx * space_x
                    ry_a = gy + gh - (record['a'] / total_reactants) * gh * 2.0  # normalized scale
                    ry_b = gy + gh - (record['b'] / total_reactants) * gh * 2.0
                    ry_ab = gy + gh - (record['ab'] / (total_reactants/2)) * gh  # AB max is total/2
                    
                    pts_a.append(QPointF(rx, ry_a))
                    pts_b.append(QPointF(rx, ry_b))
                    pts_ab.append(QPointF(rx, ry_ab))

                painter.setBrush(Qt.NoBrush)
                # Red curve A
                painter.setPen(QPen(QColor(239, 68, 68), 1.5))
                painter.drawPolyline(QPolygonF(pts_a))
                # Green curve B
                painter.setPen(QPen(QColor(0, 255, 136), 1.5))
                painter.drawPolyline(QPolygonF(pts_b))
                # Yellow product AB
                painter.setPen(QPen(QColor(250, 204, 21), 2.0))
                painter.drawPolyline(QPolygonF(pts_ab))


# ----------------- Tab 4: Interactive Periodic Table Grid Canvas -----------------
class PeriodicCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_z = 1
        
        # Periodic Table First 20 Elements data
        self.elements = {
            1: {"symbol": "H", "name": "Hydrogen", "weight": 1.008, "group": "Nonmetal", "valency": 1, "config": "1s¹", "desc": "Lightest element, highly flammable gas.", "col": 1, "row": 1},
            2: {"symbol": "He", "name": "Helium", "weight": 4.003, "group": "Noble Gas", "valency": 0, "config": "1s²", "desc": "Colorless, odorless inert noble gas.", "col": 18, "row": 1},
            
            3: {"symbol": "Li", "name": "Lithium", "weight": 6.940, "group": "Alkali Metal", "valency": 1, "config": "[He] 2s¹", "desc": "Soft, silvery highly reactive metal.", "col": 1, "row": 2},
            4: {"symbol": "Be", "name": "Beryllium", "weight": 9.012, "group": "Alkaline Earth", "valency": 2, "config": "[He] 2s²", "desc": "Hard, gray metal with high melting point.", "col": 2, "row": 2},
            5: {"symbol": "B", "name": "Boron", "weight": 10.811, "group": "Metalloid", "valency": 3, "config": "[He] 2s² 2p¹", "desc": "Metalloid used in glass and ignition systems.", "col": 13, "row": 2},
            6: {"symbol": "C", "name": "Carbon", "weight": 12.011, "group": "Nonmetal", "valency": 4, "config": "[He] 2s² 2p²", "desc": "Basis of all known organic life forms.", "col": 14, "row": 2},
            7: {"symbol": "N", "name": "Nitrogen", "weight": 14.007, "group": "Nonmetal", "valency": 3, "config": "[He] 2s² 2p³", "desc": "Constitutes 78% of Earth's atmosphere.", "col": 15, "row": 2},
            8: {"symbol": "O", "name": "Oxygen", "weight": 15.999, "group": "Nonmetal", "valency": 2, "config": "[He] 2s² 2p⁴", "desc": "Highly reactive gas essential for respiration.", "col": 16, "row": 2},
            9: {"symbol": "F", "name": "Fluorine", "weight": 18.998, "group": "Halogen", "valency": 1, "config": "[He] 2s² 2p⁵", "desc": "Extremely toxic, reactive pale yellow gas.", "col": 17, "row": 2},
            10: {"symbol": "Ne", "name": "Neon", "weight": 20.180, "group": "Noble Gas", "valency": 0, "config": "[He] 2s² 2p⁶", "desc": "Glows reddish-orange in high-voltage discharge.", "col": 18, "row": 2},
            
            11: {"symbol": "Na", "name": "Sodium", "weight": 22.990, "group": "Alkali Metal", "valency": 1, "config": "[Ne] 3s¹", "desc": "Reacts violently with water.", "col": 1, "row": 3},
            12: {"symbol": "Mg", "name": "Magnesium", "weight": 24.305, "group": "Alkaline Earth", "valency": 2, "config": "[Ne] 3s²", "desc": "Burns with a brilliant white light.", "col": 2, "row": 3},
            13: {"symbol": "Al", "name": "Aluminium", "weight": 26.982, "group": "Post-Transition Metal", "valency": 3, "config": "[Ne] 3s² 3p¹", "desc": "Lightweight, corrosion-resistant metal.", "col": 13, "row": 3},
            14: {"symbol": "Si", "name": "Silicon", "weight": 28.085, "group": "Metalloid", "valency": 4, "config": "[Ne] 3s² 3p²", "desc": "Semiconductor widely used in computer chips.", "col": 14, "row": 3},
            15: {"symbol": "P", "name": "Phosphorus", "weight": 30.974, "group": "Nonmetal", "valency": 3, "config": "[Ne] 3s² 3p³", "desc": "Highly reactive element found in match heads.", "col": 15, "row": 3},
            16: {"symbol": "S", "name": "Sulfur", "weight": 32.060, "group": "Nonmetal", "valency": 2, "config": "[Ne] 3s² 3p⁴", "desc": "Abundant multivalent nonmetal with yellow color.", "col": 16, "row": 3},
            17: {"symbol": "Cl", "name": "Chlorine", "weight": 35.450, "group": "Halogen", "valency": 1, "config": "[Ne] 3s² 3p⁵", "desc": "Disinfectant gas with strong pungent odor.", "col": 17, "row": 3},
            18: {"symbol": "Ar", "name": "Argon", "weight": 39.948, "group": "Noble Gas", "valency": 0, "config": "[Ne] 3s² 3p⁶", "desc": "Third-most abundant gas in Earth's atmosphere.", "col": 18, "row": 3},

            19: {"symbol": "K", "name": "Potassium", "weight": 39.098, "group": "Alkali Metal", "valency": 1, "config": "[Ar] 4s¹", "desc": "Soft metal that can be cut with a knife.", "col": 1, "row": 4},
            20: {"symbol": "Ca", "name": "Calcium", "weight": 40.078, "group": "Alkaline Earth", "valency": 2, "config": "[Ar] 4s²", "desc": "Essential for bone structure and cell signaling.", "col": 2, "row": 4}
        }
        self.on_element_selected = None

    def mousePressEvent(self, event):
        w, h = self.width(), self.height()
        col_w = w / 19.0
        row_h = (h - 20) / 5.0
        
        # Detect which element box was clicked
        for z, el in self.elements.items():
            bx = (el['col'] - 0.5) * col_w
            by = (el['row'] - 0.5) * row_h + 10
            
            box_rect = QRectF(bx, by, col_w - 4, row_h - 4)
            if box_rect.contains(event.pos()):
                self.selected_z = z
                self.update()
                if self.on_element_selected:
                    self.on_element_selected(z)
                break

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        col_w = w / 19.0
        row_h = (h - 20) / 5.0

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 21))

        # Color coding mapping for chemical families
        group_colors = {
            "Nonmetal": QColor(14, 165, 233, 80),            # cyan
            "Alkali Metal": QColor(239, 68, 68, 80),         # red
            "Alkaline Earth": QColor(245, 158, 11, 80),       # orange
            "Metalloid": QColor(168, 85, 247, 80),           # purple
            "Halogen": QColor(236, 72, 153, 80),             # pink
            "Noble Gas": QColor(16, 185, 129, 80),            # green
            "Post-Transition Metal": QColor(107, 114, 128, 80) # gray
        }

        group_borders = {
            "Nonmetal": QColor(14, 165, 233),
            "Alkali Metal": QColor(239, 68, 68),
            "Alkaline Earth": QColor(245, 158, 11),
            "Metalloid": QColor(168, 85, 247),
            "Halogen": QColor(236, 72, 153),
            "Noble Gas": QColor(16, 185, 129),
            "Post-Transition Metal": QColor(107, 114, 128)
        }

        # Draw first 20 elements layout boxes
        for z, el in self.elements.items():
            bx = (el['col'] - 0.5) * col_w
            by = (el['row'] - 0.5) * row_h + 10
            
            painter.setBrush(QBrush(group_colors.get(el['group'], QColor(100, 100, 100, 80))))
            
            # Highlight selected element box
            if z == self.selected_z:
                painter.setPen(QPen(QColor(255, 255, 255), 2))
            else:
                painter.setPen(QPen(group_borders.get(el['group'], QColor(200, 200, 200)), 1))

            painter.drawRoundedRect(QRectF(bx, by, col_w - 4, row_h - 4), 6, 6)

            # Element text descriptors inside cell
            painter.setPen(QPen(QColor(255, 255, 255)))
            
            # Atomic number Z (small top left)
            painter.setFont(QFont("Outfit", 7))
            painter.drawText(int(bx + 4), int(by + 12), str(z))

            # Chem symbol (large center bold)
            painter.setFont(QFont("Outfit", 9, QFont.Bold))
            painter.drawText(QRectF(bx, by + row_h/4.0, col_w - 4, row_h/2.0), Qt.AlignCenter, el['symbol'])

            # Atomic Weight (tiny bottom center)
            painter.setFont(QFont("Outfit", 6))
            painter.drawText(QRectF(bx, by + row_h*0.7, col_w - 4, row_h*0.25), Qt.AlignCenter, f"{el['weight']:.2f}")


# ----------------- Chemistry Tab Container View Layout -----------------
from PyQt5.QtCore import QRectF

class ChemistryLabView(QWidget):
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

        self.btn_bohr = QPushButton("Bohr Atomic Model")
        self.btn_bohr.setObjectName("subtab-bohr")
        self.btn_titr = QPushButton("Titration Simulator")
        self.btn_titr.setObjectName("subtab-titr")
        self.btn_gas = QPushButton("Gas Law Sandbox")
        self.btn_gas.setObjectName("subtab-gas")
        self.btn_periodic = QPushButton("Periodic Table")
        self.btn_periodic.setObjectName("subtab-periodic")
        self.btn_kinetics = QPushButton("Reaction Kinetics")
        self.btn_kinetics.setObjectName("subtab-kinetics")

        self.subtab_group = QButtonGroup(self)
        for btn in [self.btn_bohr, self.btn_titr, self.btn_gas, self.btn_periodic, self.btn_kinetics]:
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            self.subtab_group.addButton(btn)
            sub_layout.addWidget(btn)
        sub_layout.addStretch()

        self.btn_bohr.setChecked(True)
        main_layout.addWidget(self.subtab_bar)

        # 2. Main content area
        split_layout = QHBoxLayout()
        split_layout.setContentsMargins(5, 5, 5, 5)
        split_layout.setSpacing(15)

        # Content stacks on left
        self.stack = QStackedWidget()
        self.bohr_canvas = BohrCanvas()
        self.titr_canvas = TitrationCanvas()
        self.gas_canvas = GasLawCanvas()
        self.periodic_canvas = PeriodicCanvas()
        self.kinetics_canvas = KineticsCanvas()

        self.stack.addWidget(self.bohr_canvas)
        self.stack.addWidget(self.titr_canvas)
        self.stack.addWidget(self.gas_canvas)
        self.stack.addWidget(self.periodic_canvas)
        self.stack.addWidget(self.kinetics_canvas)

        split_layout.addWidget(self.stack, 3)

        # Controls stack on right
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

        # Panel 1: Bohr controls
        b_widget = QWidget()
        b_lay = QVBoxLayout(b_widget)
        b_lay.setContentsMargins(15, 15, 15, 15)
        b_lay.setSpacing(12)

        title_b = QLabel("Bohr Orbit Model")
        title_b.setFont(QFont("Outfit", 14, QFont.Bold))
        b_lay.addWidget(title_b)

        form_b = QFormLayout()
        self.combo_element = QComboBox()
        self.combo_element.addItems(["H (1)", "He (2)", "Li (3)", "Be (4)", "B (5)", "C (6)", "N (7)", "O (8)", "F (9)", "Ne (10)"])
        self.combo_element.currentIndexChanged.connect(self.bohr_element_changed)
        form_b.addRow(QLabel("Atomic Element:"), self.combo_element)
        b_lay.addLayout(form_b)

        b_lay.addWidget(QLabel("Quantum Transitions Energy:"))
        btn_excite = QPushButton("Absorb Photon (n1 -> n3)")
        btn_excite.setStyleSheet("background-color: #3b82f6; color: white; padding: 8px; border-radius: 8px;")
        btn_excite.clicked.connect(self.bohr_canvas.trigger_excitation)
        
        btn_emit = QPushButton("Emit Photon (n3 -> n1)")
        btn_emit.setStyleSheet("background-color: #10b981; color: white; padding: 8px; border-radius: 8px;")
        btn_emit.clicked.connect(self.bohr_canvas.trigger_emission)

        b_lay.addWidget(btn_excite)
        b_lay.addWidget(btn_emit)

        self.lbl_bohr_desc = QLabel("")
        self.lbl_bohr_desc.setWordWrap(True)
        self.lbl_bohr_desc.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        b_lay.addWidget(self.lbl_bohr_desc)
        self.bohr_update_desc()

        b_lay.addStretch()
        self.panel_layout.addWidget(b_widget)

        # Panel 2: Titration Controls
        t_widget = QWidget()
        t_lay = QVBoxLayout(t_widget)
        t_lay.setContentsMargins(15, 15, 15, 15)
        t_lay.setSpacing(12)

        title_t = QLabel("Acid Base Titration")
        title_t.setFont(QFont("Outfit", 14, QFont.Bold))
        t_lay.addWidget(title_t)

        form_t = QFormLayout()
        self.combo_indicator = QComboBox()
        self.combo_indicator.addItems(["Phenolphthalein", "Litmus Dye"])
        self.combo_indicator.currentIndexChanged.connect(self.titr_indicator_changed)
        form_t.addRow(QLabel("pH Indicator:"), self.combo_indicator)
        t_lay.addLayout(form_t)

        btn_drop = QPushButton("Add Titrant Drop (0.15 mL)")
        btn_drop.setStyleSheet("background-color: #3b82f6; color: white; padding: 8px; border-radius: 8px;")
        btn_drop.clicked.connect(self.titr_canvas.add_drop)
        t_lay.addWidget(btn_drop)

        self.btn_auto_titr = QPushButton("Auto Flow Valve: OFF")
        self.btn_auto_titr.setCursor(Qt.PointingHandCursor)
        self.btn_auto_titr.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08); color: white; font-weight: bold; padding: 8px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        self.btn_auto_titr.clicked.connect(self.titr_toggle_valve)
        t_lay.addWidget(self.btn_auto_titr)

        btn_t_reset = QPushButton("Reset Titration flask")
        btn_t_reset.setCursor(Qt.PointingHandCursor)
        btn_t_reset.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15); color: #ef4444; font-weight: bold; padding: 8px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.25);
            }
        """)
        btn_t_reset.clicked.connect(self.titr_reset)
        t_lay.addWidget(btn_t_reset)

        self.lbl_titr_hud = QLabel("")
        self.lbl_titr_hud.setWordWrap(True)
        self.lbl_titr_hud.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        t_lay.addWidget(self.lbl_titr_hud)

        # Valve timer
        self.valve_timer = QTimer(self)
        self.valve_timer.timeout.connect(self.titr_valve_flow)
        
        self.titr_hud_timer = QTimer(self)
        self.titr_hud_timer.timeout.connect(self.titr_update_hud)
        self.titr_hud_timer.start(100)

        t_lay.addStretch()
        self.panel_layout.addWidget(t_widget)

        # Panel 3: Gas Law controls
        g_widget = QWidget()
        g_lay = QVBoxLayout(g_widget)
        g_lay.setContentsMargins(15, 15, 15, 15)
        g_lay.setSpacing(12)

        title_g = QLabel("Gas Law Sandbox")
        title_g.setFont(QFont("Outfit", 14, QFont.Bold))
        g_lay.addWidget(title_g)

        # Temperature
        self.sl_temp = QSlider(Qt.Horizontal)
        self.sl_temp.setRange(100, 600)
        self.sl_temp.setValue(300)
        self.sl_temp.valueChanged.connect(self.gas_params_changed)
        self.lbl_temp = QLabel("Temperature T: 300 K")

        # Volume
        self.sl_vol = QSlider(Qt.Horizontal)
        self.sl_vol.setRange(40, 100)
        self.sl_vol.setValue(80)
        self.sl_vol.valueChanged.connect(self.gas_params_changed)
        self.lbl_vol = QLabel("Container Volume V: 1.00 L")

        # Moles
        self.sl_moles = QSlider(Qt.Horizontal)
        self.sl_moles.setRange(10, 100)
        self.sl_moles.setValue(50)
        self.sl_moles.valueChanged.connect(self.gas_params_changed)
        self.lbl_moles = QLabel("Quantity n: 0.50 moles")

        g_lay.addWidget(self.lbl_temp)
        g_lay.addWidget(self.sl_temp)
        g_lay.addWidget(self.lbl_vol)
        g_lay.addWidget(self.sl_vol)
        g_lay.addWidget(self.lbl_moles)
        g_lay.addWidget(self.sl_moles)

        self.lbl_gas_hud = QLabel("")
        self.lbl_gas_hud.setWordWrap(True)
        self.lbl_gas_hud.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        g_lay.addWidget(self.lbl_gas_hud)

        self.gas_hud_timer = QTimer(self)
        self.gas_hud_timer.timeout.connect(self.gas_update_hud)
        self.gas_hud_timer.start(100)

        g_lay.addStretch()
        self.panel_layout.addWidget(g_widget)

        # Panel 4: Periodic table detailed readout
        p_widget = QWidget()
        p_lay = QVBoxLayout(p_widget)
        p_lay.setContentsMargins(15, 15, 15, 15)
        p_lay.setSpacing(12)

        title_p = QLabel("Element Details")
        title_p.setFont(QFont("Outfit", 14, QFont.Bold))
        p_lay.addWidget(title_p)

        self.lbl_periodic_out = QLabel("")
        self.lbl_periodic_out.setWordWrap(True)
        self.lbl_periodic_out.setStyleSheet("background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.06); padding: 12px; border-radius: 8px; font-size: 11px;")
        p_lay.addWidget(self.lbl_periodic_out)
        self.periodic_canvas.on_element_selected = self.periodic_element_selected
        self.periodic_element_selected(1)

        p_lay.addStretch()
        self.panel_layout.addWidget(p_widget)

        # Panel 5: Reaction Kinetics controls
        k_widget = QWidget()
        k_lay = QVBoxLayout(k_widget)
        k_lay.setContentsMargins(15, 15, 15, 15)
        k_lay.setSpacing(12)

        title_k = QLabel("Reaction Kinetics")
        title_k.setFont(QFont("Outfit", 14, QFont.Bold))
        k_lay.addWidget(title_k)

        self.sl_ktemp = QSlider(Qt.Horizontal)
        self.sl_ktemp.setRange(100, 600)
        self.sl_ktemp.setValue(300)
        self.sl_ktemp.valueChanged.connect(self.kinetics_params_changed)
        self.lbl_ktemp = QLabel("Temperature T: 300 K")

        self.sl_act = QSlider(Qt.Horizontal)
        self.sl_act.setRange(5, 150)
        self.sl_act.setValue(50)
        self.sl_act.valueChanged.connect(self.kinetics_params_changed)
        self.lbl_act = QLabel("Activation Barrier Ea: 50")

        k_lay.addWidget(self.lbl_ktemp)
        k_lay.addWidget(self.sl_ktemp)
        k_lay.addWidget(self.lbl_act)
        k_lay.addWidget(self.sl_act)

        btn_k_reset = QPushButton("Reset Reactants")
        btn_k_reset.setCursor(Qt.PointingHandCursor)
        btn_k_reset.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15); color: #ef4444; font-weight: bold; padding: 10px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.25);
            }
        """)
        btn_k_reset.clicked.connect(self.kinetics_canvas.reset_sim)
        k_lay.addWidget(btn_k_reset)

        self.lbl_kinetics_hud = QLabel("")
        self.lbl_kinetics_hud.setWordWrap(True)
        self.lbl_kinetics_hud.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;")
        k_lay.addWidget(self.lbl_kinetics_hud)

        self.kinetics_hud_timer = QTimer(self)
        self.kinetics_hud_timer.timeout.connect(self.kinetics_update_hud)
        self.kinetics_hud_timer.start(150)

        k_lay.addStretch()
        self.panel_layout.addWidget(k_widget)

        # Add control panel to base splitter layout
        split_layout.addWidget(self.control_panel)
        main_layout.addLayout(split_layout)

        # Tab Index Mappings
        self.btn_bohr.clicked.connect(lambda: self.change_sub_tab(0))
        self.btn_titr.clicked.connect(lambda: self.change_sub_tab(1))
        self.btn_gas.clicked.connect(lambda: self.change_sub_tab(2))
        self.btn_periodic.clicked.connect(lambda: self.change_sub_tab(3))
        self.btn_kinetics.clicked.connect(lambda: self.change_sub_tab(4))

    def change_sub_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        self.panel_layout.setCurrentIndex(idx)

    # ---------------- BOHR MODEL BINDINGS ----------------
    def bohr_element_changed(self, idx):
        self.bohr_canvas.atomic_number = idx + 1
        names = ["Hydrogen", "Helium", "Lithium", "Beryllium", "Boron", "Carbon", "Nitrogen", "Oxygen", "Fluorine", "Neon"]
        self.bohr_canvas.element_name = names[idx]
        self.bohr_update_desc()

    def bohr_update_desc(self):
        c = self.bohr_canvas
        z = c.atomic_number
        config_list = ["1s¹", "1s²", "1s² 2s¹", "1s² 2s²", "1s² 2s² 2p¹", "1s² 2s² 2p²", "1s² 2s² 2p³", "1s² 2s² 2p⁴", "1s² 2s² 2p⁵", "1s² 2s² 2p⁶"]
        config = config_list[z-1]
        self.lbl_bohr_desc.setText(
            f"<b>Element:</b> {c.element_name}<br>"
            f"Atomic Number Z: {z}<br>"
            f"Electron Config: {config}<br>"
            f"Protons/Neutrons: {z}/{z}<br><br>"
            f"<i>Observe orbitals: Shell n=1 has max 2 electrons; shell n=2 has standard valency up to 8.</i>"
        )

    # ---------------- TITRATION BINDINGS ----------------
    def titr_indicator_changed(self, idx):
        self.titr_canvas.indicator = self.combo_indicator.currentText()

    def titr_toggle_valve(self):
        if self.valve_timer.isActive():
            self.valve_timer.stop()
            self.btn_auto_flow_valve = "Auto Flow Valve: OFF" # update text
            self.btn_auto_drop.setEnabled(True) # safety if exists
            self.btn_auto_titr.setText("Auto Flow Valve: OFF")
        else:
            self.valve_timer.start(80) # drop every 80ms
            self.btn_auto_titr.setText("Auto Flow Valve: ON")

    def titr_valve_flow(self):
        self.titr_canvas.add_drop()

    def titr_reset(self):
        if self.valve_timer.isActive():
            self.valve_timer.stop()
            self.btn_auto_titr.setText("Auto Flow Valve: OFF")
        self.titr_canvas.titrant_vol = 0.0
        self.titr_canvas.drops.clear()
        self.titr_canvas.update()

    def titr_update_hud(self):
        c = self.titr_canvas
        ph = c.get_ph()
        self.lbl_titr_hud.setText(
            f"<b>Analyte Acid Flask (HCl):</b><br>"
            f"Volume: {c.analyte_vol} mL<br>"
            f"Normality: 0.1 N<br><br>"
            f"<b>Titrant Base added (NaOH):</b><br>"
            f"Volume: {c.titrant_vol:.2f} mL<br>"
            f"pH Readout: <span style='font-size:16px; font-weight:bold; color:#ff48eb;'>{ph:.2f}</span><br>"
            f"Neutralization State: " + ("Neutralized" if abs(ph-7)<0.5 else ("Acidic remnant" if ph<7 else "Basic excess"))
        )

    # ---------------- GAS LAW BINDINGS ----------------
    def gas_params_changed(self):
        c = self.gas_canvas
        c.temperature = self.sl_temp.value()
        c.volume = self.sl_vol.value() / 80.0
        c.n_moles = self.sl_moles.value() / 100.0
        c.sync_particles()

        self.lbl_temp.setText(f"Temperature T: {c.temperature} K")
        self.lbl_vol.setText(f"Container Volume V: {c.volume:.2f} L")
        self.lbl_moles.setText(f"Quantity n: {c.n_moles:.2f} moles")

    def gas_update_hud(self):
        c = self.gas_canvas
        p = c.get_pressure()
        p_torr = p * 760.0
        self.lbl_gas_hud.setText(
            f"<b>Dynamic Pressure Readout:</b><br>"
            f"Pressure (P): <span style='font-size:16px; font-weight:bold; color:#00e5ff;'>{p:.3f} atm</span><br>"
            f"In Torr: {p_torr:.1f} Torr<br><br>"
            f"<b>State Variable Matrix (PV=nRT):</b><br>"
            f"P·V Product: {(p*c.volume):.3f}<br>"
            f"n·R·T Product: {(c.n_moles*0.0821*c.temperature):.3f}"
        )

    # ---------------- PERIODIC TABLE GRID BINDINGS ----------------
    def periodic_element_selected(self, z):
        info = self.periodic_canvas.elements[z]
        self.lbl_periodic_out.setText(
            f"<b style='font-size:16px; color:#00ff88;'>{info['name']} ({info['symbol']})</b><br><br>"
            f"<b>Atomic Number (Z):</b> {z}<br>"
            f"<b>Atomic Weight:</b> {info['weight']:.4f} u<br>"
            f"<b>Chemical Family:</b> {info['group']}<br>"
            f"<b>Standard Valency:</b> {info['valency']}<br>"
            f"<b>Electron Configuration:</b> {info['config']}<br><br>"
            f"<b>Description:</b><br><i>{info['desc']}</i>"
        )

    # ---------------- REACTION KINETICS BINDINGS ----------------
    def kinetics_params_changed(self):
        c = self.kinetics_canvas
        c.temperature = self.sl_ktemp.value()
        c.activation_energy = self.sl_act.value()
        
        self.lbl_ktemp.setText(f"Temperature T: {c.temperature} K")
        self.lbl_act.setText(f"Activation Barrier Ea: {c.activation_energy}")

    def kinetics_update_hud(self):
        c = self.kinetics_canvas
        count_a = sum(1 for p in c.particles if p['type'] == 'A')
        count_b = sum(1 for p in c.particles if p['type'] == 'B')
        count_ab = c.product_ab
        
        # Calculate yield progress percentage
        total_initial = c.reactant_a # A is limiting reactant, usually equal to B index count
        yield_pct = (count_ab / total_initial) * 100.0 if total_initial > 0 else 0.0

        self.lbl_kinetics_hud.setText(
            f"<b>Beaker Species counts:</b><br>"
            f"Reactants A (Red): {count_a}<br>"
            f"Reactants B (Green): {count_b}<br>"
            f"Compound AB (Yellow): {count_ab}<br><br>"
            f"<b>Reaction Yield Progress:</b><br>"
            f"Yield percentage: <span style='font-size:15px; font-weight:bold; color:#f59e0b;'>{yield_pct:.1f}%</span>"
        )


