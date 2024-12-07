from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QComboBox, QTextEdit, QCheckBox, QLineEdit, 
                           QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QImage, QPixmap
import pygame

class MemoryViewer(QMainWindow):
    def __init__(self, parent, memory_manager):
        super().__init__(parent)
        self.memory_manager = memory_manager
        self.setWindowTitle("Memory Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(600, 400)

        # Memory segments for CHIP-8
        self.segments = {
            "All Memory": (0x000, 0x1000),  # Complete memory range
            "Reserved": (0x000, 0x200),     # Interpreter
            "Font Data": (0x050, 0x0A0),    # Built-in font data
            "Program": (0x200, 0x1000),     # Program ROM and work RAM
            "Stack": (0xEA0, 0xEFF),        # Stack
            "Display Refresh": (0xF00, 0xFFF)  # Display refresh
        }
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left panel (segment selection)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add segment selector
        self.segment_combo = QComboBox()
        self.segment_combo.addItems(self.segments.keys())
        self.segment_combo.currentTextChanged.connect(self.update_display)
        left_layout.addWidget(QLabel("Memory Segment:"))
        left_layout.addWidget(self.segment_combo)
        
        # Add address jump
        jump_widget = QWidget()
        jump_layout = QHBoxLayout(jump_widget)
        self.addr_entry = QLineEdit()
        self.addr_entry.setPlaceholderText("Hex address")
        jump_button = QPushButton("Jump to")
        jump_button.clicked.connect(self.jump_to_address)
        jump_layout.addWidget(self.addr_entry)
        jump_layout.addWidget(jump_button)
        left_layout.addWidget(QLabel("Jump to Address:"))
        left_layout.addWidget(jump_widget)
        
        # Add auto-refresh checkbox
        self.auto_refresh_check = QCheckBox("Auto Refresh")
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        left_layout.addWidget(self.auto_refresh_check)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # Create right panel (memory display)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add memory display with monospace font
        self.memory_display = QTextEdit()
        monospace_font = QFont("Courier New")
        monospace_font.setStyleHint(QFont.StyleHint.Monospace)
        monospace_font.setFixedPitch(True)
        monospace_font.setPointSize(10)
        self.memory_display.setFont(monospace_font)
        self.memory_display.setReadOnly(True)
        right_layout.addWidget(self.memory_display)
        
        main_layout.addWidget(right_panel)
        
        # Set up auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_display)
        
        # Initial display update
        self.update_display()
    
    def toggle_auto_refresh(self, state):
        if state == Qt.CheckState.Checked.value:
            self.refresh_timer.start(100)  # Refresh every 100ms
        else:
            self.refresh_timer.stop()
    
    def jump_to_address(self):
        try:
            addr = int(self.addr_entry.text(), 16)
            if not (0x000 <= addr <= 0xFFF):
                raise ValueError("Address out of range")
            
            # Find appropriate segment
            for segment_name, (start, end) in self.segments.items():
                if start <= addr < end:
                    self.segment_combo.setCurrentText(segment_name)
                    self.update_display()
                    # TODO: Implement scrolling to specific address
                    break
            
        except ValueError as e:
            print(f"Invalid address: {e}")
    
    def update_display(self):
        segment_name = self.segment_combo.currentText()
        if segment_name not in self.segments:
            return
            
        start_addr, end_addr = self.segments[segment_name]
        memory = self.memory_manager.get_memory_block(start_addr, end_addr - start_addr)
        
        # Format the display text
        display_text = f"=== {segment_name} (0x{start_addr:03X}-0x{end_addr-1:03X}) ===\n\n"
        
        for i in range(0, len(memory), 16):
            # Address column
            line = f"0x{start_addr+i:03X}: "
            
            # Hex values
            hex_part = ""
            ascii_part = "│ "
            
            for j in range(16):
                if i + j < len(memory):
                    byte = memory[i + j]
                    hex_part += f"{byte:02X} "
                    ascii_part += chr(byte) if 32 <= byte <= 126 else "."
                else:
                    hex_part += "   "
                    ascii_part += " "
                
                if j == 7:  # Add extra space in middle
                    hex_part += " "
            
            ascii_part += " │"
            display_text += line + hex_part + ascii_part + "\n"
        
        self.memory_display.setText(display_text)

class DisplayViewer(QMainWindow):
    def __init__(self, parent, display):
        super().__init__(parent)
        self.display = display
        self.setWindowTitle("Display Viewer")
        self.setGeometry(100, 100, 800, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left panel (controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add zoom control
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        self.zoom_factor = QComboBox()
        self.zoom_factor.addItems(['1x', '2x', '4x', '8x', '16x'])
        self.zoom_factor.setCurrentText('8x')
        self.zoom_factor.currentTextChanged.connect(self.update_display)
        zoom_layout.addWidget(QLabel("Zoom:"))
        zoom_layout.addWidget(self.zoom_factor)
        left_layout.addWidget(zoom_widget)
        
        # Add grid checkbox
        self.show_grid = QCheckBox("Show Grid")
        self.show_grid.stateChanged.connect(self.update_display)
        left_layout.addWidget(self.show_grid)
        
        # Add auto-refresh checkbox
        self.auto_refresh = QCheckBox("Auto Refresh")
        self.auto_refresh.stateChanged.connect(self.toggle_auto_refresh)
        left_layout.addWidget(self.auto_refresh)
        
        # Add test pattern button
        test_button = QPushButton("Test Pattern")
        test_button.clicked.connect(self.show_test_pattern)
        left_layout.addWidget(test_button)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # Create right panel (display view)
        self.display_view = QLabel()
        self.display_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.display_view)
        
        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_display)
        
        # Initial display update
        self.update_display()
    
    def toggle_auto_refresh(self, state):
        if state == Qt.CheckState.Checked.value:
            self.refresh_timer.start(100)  # Refresh every 100ms
        else:
            self.refresh_timer.stop()
    
    def show_test_pattern(self):
        self.display.test_pattern(0)  # You might want to add scroll control
        self.update_display()
    
    def update_display(self):
        try:
            # Get zoom factor
            zoom = int(self.zoom_factor.currentText().replace('x', ''))
            
            # Create a scaled image of the display
            width = self.display.WIDTH * zoom
            height = self.display.HEIGHT * zoom
            
            # Create a new surface and scale it
            scaled_surface = pygame.Surface((width, height))
            pygame.transform.scale(self.display.surface, (width, height), scaled_surface)
            
            # Draw grid if enabled
            if self.show_grid.isChecked():
                for x in range(0, width, zoom):
                    pygame.draw.line(scaled_surface, (40, 40, 40), (x, 0), (x, height))
                for y in range(0, height, zoom):
                    pygame.draw.line(scaled_surface, (40, 40, 40), (0, y), (width, y))
            
            # Convert pygame surface to QPixmap
            buffer = pygame.image.tostring(scaled_surface, "RGB")
            qimage = QImage(buffer, width, height, width * 3, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            
            self.display_view.setPixmap(pixmap)
            
        except Exception as e:
            print(f"Error updating display view: {e}")

class CPUViewer(QMainWindow):
    def __init__(self, parent, cpu):
        super().__init__(parent)
        self.cpu = cpu
        self.setWindowTitle("CPU Debugger")
        self.setGeometry(100, 100, 600, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create controls
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        
        # Step button
        self.step_button = QPushButton("Step")
        self.step_button.clicked.connect(self.single_step)
        controls_layout.addWidget(self.step_button)
        
        # Continue/Break button
        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.toggle_continue)
        controls_layout.addWidget(self.continue_button)
        
        layout.addWidget(controls_widget)
        
        # Create info display
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        monospace_font = QFont("Courier New")
        monospace_font.setStyleHint(QFont.StyleHint.Monospace)
        monospace_font.setFixedPitch(True)
        self.info_display.setFont(monospace_font)
        layout.addWidget(self.info_display)
        
        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_display)
        self.refresh_timer.start(100)  # Update every 100ms
        
        # Initial update
        self.update_display()
    
    def single_step(self):
        """Execute a single CPU instruction"""
        self.cpu.step()
        self.update_display()
    
    def toggle_continue(self):
        """Toggle between continue and break"""
        if self.continue_button.text() == "Continue":
            self.continue_button.setText("Break")
            self.step_button.setEnabled(False)
            self.cpu.main_window.start_emulation()
        else:
            self.continue_button.setText("Continue")
            self.step_button.setEnabled(True)
            self.cpu.main_window.stop_emulation()
    
    def update_display(self):
        """Update the CPU state display"""
        try:
            # Format CPU state information
            info = "=== CPU State ===\n\n"
            
            # Program counter and current instruction
            info += f"PC: 0x{self.cpu.program_counter:03X}\n"
            info += f"Current Instruction: 0x{self.cpu.decoded_instruction:04X}\n\n"
            
            # Registers
            info += "Registers:\n"
            for i in range(0, 16, 4):
                reg_line = ""
                for j in range(4):
                    reg_num = i + j
                    reg_line += f"V{reg_num:X}: 0x{self.cpu.registers[reg_num]:02X}  "
                info += reg_line + "\n"
            
            info += f"\nIndex Register (I): 0x{self.cpu.index_register:03X}\n"
            
            # Timers
            info += f"\nDelay Timer: {self.cpu.delay_timer}"
            info += f"\nSound Timer: {self.cpu.sound_timer}\n"
            
            # Stack
            info += "\nStack:\n"
            for i, value in enumerate(self.cpu.stack):
                info += f"{i}: 0x{value:03X}\n"
            
            self.info_display.setText(info)
            
        except Exception as e:
            print(f"Error updating CPU display: {e}")

class InputViewer(QMainWindow):
    def __init__(self, parent, input_manager):
        super().__init__(parent)
        self.input_manager = input_manager
        self.setWindowTitle("Input Debugger")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create key state display grid
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        
        # CHIP-8 keypad layout buttons
        self.key_buttons = {}
        key_layout = [
            ['1', '2', '3', 'C'],
            ['4', '5', '6', 'D'],
            ['7', '8', '9', 'E'],
            ['A', '0', 'B', 'F']
        ]
        
        for row, keys in enumerate(key_layout):
            for col, key in enumerate(keys):
                btn = QPushButton(key)
                btn.setCheckable(True)
                btn.setEnabled(False)  # Make buttons non-interactive
                self.key_buttons[key] = btn
                grid_layout.addWidget(btn, row, col)
        
        layout.addWidget(grid_widget)
        
        # Add key mapping documentation
        mapping_text = QTextEdit()
        mapping_text.setReadOnly(True)
        mapping_text.setText(input_manager.get_key_mapping_text())
        layout.addWidget(QLabel("Key Mappings:"))
        layout.addWidget(mapping_text)
        
        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_display)
        self.refresh_timer.start(16)  # 60fps refresh
    
    def update_display(self):
        """Update the key state display"""
        try:
            # Map CHIP-8 keys to button labels
            key_map = {
                0x0: '0', 0x1: '1', 0x2: '2', 0x3: '3',
                0x4: '4', 0x5: '5', 0x6: '6', 0x7: '7',
                0x8: '8', 0x9: '9', 0xA: 'A', 0xB: 'B',
                0xC: 'C', 0xD: 'D', 0xE: 'E', 0xF: 'F'
            }
            
            # Update button states
            for chip8_key, label in key_map.items():
                is_pressed = self.input_manager.is_key_pressed(chip8_key)
                self.key_buttons[label].setChecked(is_pressed)
                
        except Exception as e:
            print(f"Error updating input display: {e}")

class BreakpointManager:
    def __init__(self):
        self.breakpoints = set()
        
    def add_breakpoint(self, address):
        self.breakpoints.add(address)
        
    def remove_breakpoint(self, address):
        self.breakpoints.discard(address)
        
    def should_break(self, address):
        return address in self.breakpoints