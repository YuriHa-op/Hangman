from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QPropertyAnimation, QRect, QRectF
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QPainterPath
import math
import random
import traceback

class ConfettiEffect(QWidget):
    """Creates a confetti explosion effect for celebrating wins"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_particles)
        self.setFixedSize(parent.size() if parent else QSize(800, 600))
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()
        # Used for shimmer effect
        self.animation_counter = 0
        
    def start_animation(self, duration=2000):
        """Start the confetti animation"""
        try:
            # Clear any existing particles
            self.particles = []
            # Reset animation counter
            self.animation_counter = 0
            
            # Get center of the widget, but move it up a bit from center
            center_x = self.width() / 2
            center_y = self.height() * 0.4  # Position at 40% from top instead of 50%
            
            # Create particles - increased count from 150 to 300
            for _ in range(300):  # More confetti!
                # Randomize initial position slightly for more natural explosion
                start_x = center_x + random.uniform(-20, 20)
                start_y = center_y + random.uniform(-20, 20)
                
                # More explosive velocity range
                velocity_magnitude = random.uniform(5, 15)  # Stronger velocity for more explosive effect
                angle = random.uniform(0, 2 * math.pi)
                
                # Create more powerful directional blast
                dx = math.cos(angle) * velocity_magnitude
                dy = math.sin(angle) * velocity_magnitude
                
                # More color variety with bright colors for celebrations
                hue = random.uniform(0, 1.0)
                saturation = random.uniform(0.7, 1.0)  # Brighter colors
                brightness = random.uniform(0.7, 1.0)  # Brighter colors
                color = QColor.fromHsvF(hue, saturation, brightness)
                
                # Add sparkle effect with gold/silver colors for some particles
                if random.random() < 0.2:  # 20% chance for metallic particles
                    if random.random() < 0.5:  # Gold
                        color = QColor(255, 215, 0, random.randint(200, 255))
                    else:  # Silver
                        color = QColor(192, 192, 192, random.randint(200, 255))
                
                particle = {
                    'x': start_x,
                    'y': start_y,
                    'dx': dx,
                    'dy': dy,
                    'size': random.randint(5, 20),  # Larger size range
                    'color': color,
                    'rotation': random.randint(0, 360),
                    'rotation_speed': random.uniform(-20, 20),  # Faster rotation
                    'opacity': 1.0,
                    'fade_speed': random.uniform(0.003, 0.01),  # Slower fade for longer effect
                    'gravity': random.uniform(0.1, 0.4),
                    'shape': random.choice(['rect', 'circle', 'star', 'triangle', 'diamond']),  # Added diamond shape
                    'shimmer': random.random() < 0.3,  # Some particles shimmer
                    'shimmer_phase': random.uniform(0, 2 * math.pi),  # Random starting phase for shimmer effect
                    'shimmer_speed': random.uniform(0.1, 0.3)  # Speed of shimmer cycle
                }
                self.particles.append(particle)
            
            # Add a few large "boom" particles that fade quickly at the center
            for _ in range(10):
                boom_particle = {
                    'x': center_x + random.uniform(-10, 10),
                    'y': center_y + random.uniform(-10, 10),
                    'dx': random.uniform(-1, 1),
                    'dy': random.uniform(-1, 1),
                    'size': random.randint(30, 80),  # Large size
                    'color': QColor(255, 255, 255, 150),  # Semi-transparent white
                    'rotation': random.randint(0, 360),
                    'rotation_speed': random.uniform(-5, 5),
                    'opacity': random.uniform(0.7, 1.0),
                    'fade_speed': random.uniform(0.02, 0.05),  # Fast fade
                    'gravity': 0.05,  # Low gravity
                    'shape': 'circle',
                    'shimmer': False,
                    'is_boom': True  # Special boom particle
                }
                self.particles.append(boom_particle)
            
            self.show()
            self.timer.start(16)  # ~60 FPS
            
            # Stop after the duration
            QTimer.singleShot(duration, self.stop_animation)
        except Exception as e:
            print(f"Error in confetti animation start: {str(e)}")
            traceback.print_exc()
            self.stop_animation()
    
    def update_particles(self):
        """Update particle positions and properties"""
        try:
            still_active = False
            
            # Increment counter for shimmer effect
            self.animation_counter += 0.05
            
            for particle in self.particles:
                # Apply gravity
                particle['dy'] += particle['gravity']
                
                # Update position
                particle['x'] += particle['dx']
                particle['y'] += particle['dy']
                
                # Slow down over time (air resistance)
                if not particle.get('is_boom', False):
                    particle['dx'] *= 0.98
                    particle['dy'] *= 0.98
                
                # Update rotation
                particle['rotation'] += particle['rotation_speed']
                
                # Shimmer effect (cycle opacity)
                if particle.get('shimmer', False):
                    # Use the counter plus a particle-specific phase offset
                    shimmer_value = self.animation_counter * particle.get('shimmer_speed', 0.1)
                    phase = particle.get('shimmer_phase', 0)
                    shimmer_factor = abs(math.sin(shimmer_value + phase))
                    base_opacity = particle['opacity']
                    particle['display_opacity'] = max(0, min(1, base_opacity * (0.5 + 0.5 * shimmer_factor)))
                else:
                    particle['display_opacity'] = particle['opacity']
                
                # Fade out
                particle['opacity'] -= particle['fade_speed']
                
                # Check if any particles are still visible
                if particle['opacity'] > 0:
                    still_active = True
                    
            if not still_active:
                self.stop_animation()
            
            # Trigger repaint
            self.update()
        except Exception as e:
            print(f"Error in confetti animation update: {str(e)}")
            traceback.print_exc()
            self.stop_animation()
    
    def stop_animation(self):
        """Stop the animation and hide widget"""
        try:
            self.timer.stop()
            self.hide()
            self.deleteLater()
        except Exception as e:
            print(f"Error stopping confetti animation: {str(e)}")
            traceback.print_exc()
    
    def paintEvent(self, event):
        """Draw all the confetti particles"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            for particle in self.particles:
                if particle['opacity'] <= 0:
                    continue
                    
                # Set opacity (with shimmer effect if applicable)
                painter.setOpacity(particle.get('display_opacity', particle['opacity']))
                
                # Save state for rotation
                painter.save()
                
                # Move to particle position and rotate
                painter.translate(particle['x'], particle['y'])
                painter.rotate(particle['rotation'])
                
                # Draw the particle based on shape
                painter.setBrush(QBrush(particle['color']))
                painter.setPen(Qt.NoPen)
                
                size = particle['size']
                half_size = size / 2
                
                # Special handling for boom particles
                if particle.get('is_boom', False):
                    # Create radial gradient for boom effect
                    gradient = QRadialGradient(0, 0, half_size)
                    color = particle['color']
                    gradient.setColorAt(0, QColor(255, 255, 255, 200))  # White center
                    gradient.setColorAt(0.3, QColor(color.red(), color.green(), color.blue(), 150))
                    gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))  # Transparent edge
                    painter.setBrush(QBrush(gradient))
                    rect = QRectF(-half_size, -half_size, size, size)
                    painter.drawEllipse(rect)
                elif particle['shape'] == 'rect':
                    # Convert coordinates to integers for rect
                    painter.drawRect(int(-half_size), int(-half_size), int(size), int(size))
                elif particle['shape'] == 'circle':
                    # Use QRectF for ellipse
                    rect = QRectF(-half_size, -half_size, size, size)
                    painter.drawEllipse(rect)
                elif particle['shape'] == 'triangle':
                    path = QPainterPath()
                    path.moveTo(0, -half_size)
                    path.lineTo(half_size, half_size)
                    path.lineTo(-half_size, half_size)
                    path.closeSubpath()
                    painter.drawPath(path)
                elif particle['shape'] == 'diamond':
                    path = QPainterPath()
                    path.moveTo(0, -half_size)  # Top point
                    path.lineTo(half_size, 0)   # Right point
                    path.lineTo(0, half_size)   # Bottom point
                    path.lineTo(-half_size, 0)  # Left point
                    path.closeSubpath()
                    painter.drawPath(path)
                elif particle['shape'] == 'star':
                    # Draw a simple star shape
                    path = QPainterPath()
                    outer_radius = half_size
                    inner_radius = half_size * 0.4
                    points = 5
                    
                    for i in range(points * 2):
                        angle = math.pi * i / points
                        radius = inner_radius if i % 2 else outer_radius
                        x = radius * math.sin(angle)
                        y = -radius * math.cos(angle)
                        
                        if i == 0:
                            path.moveTo(x, y)
                        else:
                            path.lineTo(x, y)
                            
                    path.closeSubpath()
                    painter.drawPath(path)
                
                # Restore state
                painter.restore()
        except Exception as e:
            print(f"Error in confetti paint event: {str(e)}")
            traceback.print_exc() 