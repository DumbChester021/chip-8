from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QTimer
import pygame
import sys
from menu import MenuBar
from memory import MemoryManager
from cpu import CPU
from display import Display
import time
import os
from input import InputManager
from sound import SoundManager
from config import EmulatorConfig
import logging

class PygameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        # Set minimum size and aspect ratio
        self.base_width = 640
        self.base_height = 320
        self.setMinimumSize(self.base_width, self.base_height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Enable OpenGL context for better vsync support
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
        
        # Set widget to update on timer instead of every paint event
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
    def resizeEvent(self, event):
        # Calculate new size maintaining 2:1 aspect ratio
        new_size = event.size()
        w = new_size.width()
        h = new_size.height()
        
        # Calculate height based on width (2:1 aspect ratio)
        target_h = w // 2
        
        if target_h > h:
            # Height is limiting factor
            w = h * 2
            self.resize(w, h)
        else:
            # Width is limiting factor
            self.resize(w, target_h)
            
        super().resizeEvent(event)
    
    def get_window_id(self):
        return int(self.winId())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CHIP-8 Emulator")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='emulator.log'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = EmulatorConfig.load()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create Pygame widget
        self.pygame_widget = PygameWidget(self)
        layout.addWidget(self.pygame_widget)
        
        # Need to show the widget before getting window ID
        self.pygame_widget.show()
        
        # Get the window ID after the widget is shown
        window_id = self.pygame_widget.get_window_id()
        
        # Initialize pygame display
        self.display = Display(window_id)
        
        # Initialize components in correct order
        self.memory_manager = MemoryManager()
        self.input_manager = InputManager()
        self.sound_manager = SoundManager()  # Create sound manager
        self.cpu = CPU(self.memory_manager, self.input_manager, self.sound_manager)  # Pass sound manager
        self.cpu.main_window = self  # Add this line
        
        # Connect display to memory manager
        self.memory_manager.display = self.display
        
        # Create menu bar
        self.menu_bar = MenuBar(self, self.memory_manager)
        self.setMenuBar(self.menu_bar)
        
        # Emulation control
        self.is_running = False
        self.last_timer_update = time.time()
        self.last_display_update = time.time()
        self.DISPLAY_UPDATE_INTERVAL = 1/60  # 60 FPS
        
        # Improved timing control
        self.frame_time = 1.0 / 60.0  # Target 60 FPS
        self.last_frame_time = time.time()
        self.accumulated_time = 0
        
        # Use a more precise timer
        self.timer = QTimer()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.emulation_loop)
        self.timer.start(1)  # Run as fast as possible, we'll control timing in the loop
        
        # Set window flags to ensure proper keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def emulation_loop(self):
        try:
            current_time = time.time()
            elapsed = current_time - self.last_frame_time
            self.last_frame_time = current_time
            self.accumulated_time += elapsed

            # Fixed timestep update
            while self.accumulated_time >= self.frame_time:
                # Handle input
                for event in pygame.event.get():
                    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                        self.input_manager.handle_pygame_event(event)
                
                # Run CPU cycles
                if self.is_running:
                    for _ in range(self.config.instructions_per_frame):
                        self.cpu.step()
                    
                    # Update timers
                    self.cpu.update_timers()
                
                self.accumulated_time -= self.frame_time
            
            # Render at display refresh rate
            self.display.refresh()
            
        except Exception as e:
            print(f"Error in emulation loop: {e}")
            import traceback
            traceback.print_exc()
    
    def start_emulation(self):
        self.is_running = True
    
    def stop_emulation(self):
        self.is_running = False
    
    def reset_emulation(self):
        self.cpu.reset()
        self.display.clear()
        self.is_running = False
    
    def keyPressEvent(self, event):
        """Handle Qt key press events"""
        # First check if it's a menu shortcut
        if event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            super().keyPressEvent(event)
            return
            
        # Handle game input
        self.input_manager.handle_qt_keypress(event)
    
    def keyReleaseEvent(self, event):
        """Handle Qt key release events"""
        # First check if it's a menu shortcut
        if event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            super().keyReleaseEvent(event)
            return
            
        # Handle game input
        self.input_manager.handle_qt_keyrelease(event)
    
    def closeEvent(self, event):
        """Clean up resources when window is closed"""
        self.sound_manager.cleanup()
        super().closeEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update display size if needed
        if hasattr(self, 'display'):
            self.display.refresh()
    
    def apply_config(self):
        """Apply configuration changes"""
        # Update CPU frequency
        self.timer.setInterval(1000 // self.config.cpu_frequency)
        
        # Update display
        self.display.set_colors(self.config.foreground_color, self.config.background_color)
        
        # Update sound
        self.sound_manager.set_frequency(self.config.sound_frequency)
        self.sound_manager.set_volume(self.config.sound_volume)
        
        # Update display optimization
        self.display.optimize_updates = self.config.optimize_display_updates

if __name__ == "__main__":
    # Create QApplication instance first
    app = QApplication(sys.argv)
    
    # Initialize pygame before creating the window
    os.environ['SDL_VIDEODRIVER'] = 'windib' if os.name == 'nt' else 'x11'
    pygame.init()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start Qt event loop
    sys.exit(app.exec())
