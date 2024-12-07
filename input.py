import pygame
from PyQt6.QtCore import Qt

class InputManager:
    def __init__(self):
        # Initialize key states (0-F)
        self.key_states = [False] * 16
        
        # Add documentation for key mappings
        self.key_mapping_text = """
CHIP-8 Key | Keyboard
-----------|---------
   1-4     |  1234
   4-7     |  QWER
   7-A     |  ASDF
   A-F     |  ZXCV
        """
        
        # CHIP-8 keypad layout:
        # 1 2 3 C
        # 4 5 6 D
        # 7 8 9 E
        # A 0 B F
        
        # Map Qt keys to CHIP-8 keys
        self.qt_keymap = {
            Qt.Key.Key_1: 0x1, Qt.Key.Key_2: 0x2, Qt.Key.Key_3: 0x3, Qt.Key.Key_4: 0xC,
            Qt.Key.Key_Q: 0x4, Qt.Key.Key_W: 0x5, Qt.Key.Key_E: 0x6, Qt.Key.Key_R: 0xD,
            Qt.Key.Key_A: 0x7, Qt.Key.Key_S: 0x8, Qt.Key.Key_D: 0x9, Qt.Key.Key_F: 0xE,
            Qt.Key.Key_Z: 0xA, Qt.Key.Key_X: 0x0, Qt.Key.Key_C: 0xB, Qt.Key.Key_V: 0xF
        }
        
        # Map pygame keys to CHIP-8 keys (for compatibility)
        self.pygame_keymap = {
            pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
            pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
            pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
            pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
        }
    
    def handle_qt_keypress(self, event):
        """Handle Qt key press events"""
        # Ignore key events with modifiers (Alt, Ctrl, etc.)
        if event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            return
            
        if event.key() in self.qt_keymap:
            chip8_key = self.qt_keymap[event.key()]
            self.key_states[chip8_key] = True
    
    def handle_qt_keyrelease(self, event):
        """Handle Qt key release events"""
        if event.key() in self.qt_keymap:
            chip8_key = self.qt_keymap[event.key()]
            self.key_states[chip8_key] = False
    
    def handle_pygame_event(self, event):
        """Handle Pygame key events"""
        if event.type == pygame.KEYDOWN and event.key in self.pygame_keymap:
            chip8_key = self.pygame_keymap[event.key]
            self.key_states[chip8_key] = True
        elif event.type == pygame.KEYUP and event.key in self.pygame_keymap:
            chip8_key = self.pygame_keymap[event.key]
            self.key_states[chip8_key] = False
    
    def is_key_pressed(self, key):
        """Check if a specific CHIP-8 key is pressed"""
        return self.key_states[key]
    
    def wait_for_keypress(self):
        """Wait for any key press and return the CHIP-8 key number"""
        # This will be called from the CPU to implement FX0A
        for i, pressed in enumerate(self.key_states):
            if pressed:
                return i
        return None
    
    def reset(self):
        """Reset all key states"""
        self.key_states = [False] * 16 
    
    def get_key_mapping_text(self):
        """Return formatted key mapping documentation"""
        return self.key_mapping_text
    
    def process_input(self):
        """Batch process all pending input events"""
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
                else:
                    self.handle_keyup(event)