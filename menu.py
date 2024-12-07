from PyQt6.QtWidgets import QMenuBar, QMenu, QFileDialog
from PyQt6.QtCore import Qt
from debug_viewers import InputViewer, MemoryViewer, DisplayViewer, CPUViewer
from config_dialog import ConfigDialog
from config import EmulatorConfig

class MenuBar(QMenuBar):
    def __init__(self, main_window, memory_manager):
        super().__init__(main_window)
        self.main_window = main_window
        self.memory_manager = memory_manager
        
        # Create menus
        self.create_file_menu()
        self.create_emulation_menu()
        self.create_debug_menu()
    
    def create_file_menu(self):
        file_menu = QMenu("&File", self)
        self.addMenu(file_menu)
        
        file_menu.addAction("Load ROM", self.load_rom)
        file_menu.addAction("Configuration", self.show_config_dialog)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.main_window.close)
    
    def create_emulation_menu(self):
        emu_menu = QMenu("&Emulation", self)
        self.addMenu(emu_menu)
        
        emu_menu.addAction("Start", self.main_window.start_emulation)
        emu_menu.addAction("Stop", self.main_window.stop_emulation)
        emu_menu.addAction("Reset", self.main_window.reset_emulation)
    
    def create_debug_menu(self):
        debug_menu = QMenu("&Debug", self)
        self.addMenu(debug_menu)
        
        debug_menu.addAction("Show Memory", self.show_memory_viewer)
        debug_menu.addAction("Show Display", self.show_display_viewer)
        debug_menu.addAction("Show CPU", self.show_cpu_viewer)
        debug_menu.addAction("Show Input", self.show_input_viewer)
    
    def load_rom(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Load ROM",
            "",
            "CHIP-8 ROM (*.ch8);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    rom_data = file.read()
                    print(f"ROM size: {len(rom_data)} bytes")
                    # Reset emulator state before loading new ROM
                    self.main_window.reset_emulation()
                    # Load ROM data into memory starting at 0x200 (512)
                    for i, byte in enumerate(rom_data):
                        self.memory_manager.write(0x200 + i, byte)
                    print(f"ROM loaded successfully: {file_path}")
                    # Start emulation automatically after loading ROM
                    self.main_window.start_emulation()
            except Exception as e:
                print(f"Error loading ROM: {e}")
    
    def show_memory_viewer(self):
        try:
            self.memory_viewer = MemoryViewer(self.main_window, self.memory_manager)
            self.memory_viewer.show()
        except Exception as e:
            print(f"Error showing memory viewer: {e}")
    
    def show_display_viewer(self):
        try:
            self.display_viewer = DisplayViewer(self.main_window, self.main_window.display)
            self.display_viewer.show()
        except Exception as e:
            print(f"Error showing display viewer: {e}")
    
    def show_cpu_viewer(self):
        try:
            self.cpu_viewer = CPUViewer(self.main_window, self.main_window.cpu)
            self.cpu_viewer.show()
        except Exception as e:
            print(f"Error showing CPU viewer: {e}")
    
    def show_input_viewer(self):
        try:
            self.input_viewer = InputViewer(self.main_window, self.main_window.input_manager)
            self.input_viewer.show()
        except Exception as e:
            print(f"Error showing input viewer: {e}")
    
    def show_config_dialog(self):
        try:
            dialog = ConfigDialog(self.main_window, self.main_window.config)
            if dialog.exec():
                self.main_window.config = dialog.get_config()
                self.main_window.config.save()
                # Apply configuration changes
                self.main_window.apply_config()
        except Exception as e:
            print(f"Error showing configuration dialog: {e}")

