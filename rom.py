import os
import tkinter as tk
from tkinter import filedialog
import pygame

class ROMLoader:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        # Create a hidden tkinter root window for file dialog
        self.root = tk.Tk()
        self.root.withdraw()

    def load_rom(self):
        # Using tkinter's file dialog since Pygame doesn't have one built-in
        file_path = filedialog.askopenfilename(
            parent=self.root,
            filetypes=[
                ("CHIP-8 ROM", "*.ch8"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    rom_data = file.read()
                    print(f"ROM size: {len(rom_data)} bytes")
                    # Load ROM data into memory starting at 0x200 (512)
                    for i, byte in enumerate(rom_data):
                        self.memory_manager.write(0x200 + i, byte)
                    print(f"ROM loaded successfully: {file_path}")
                    return True
            except Exception as e:
                print(f"Error loading ROM: {e}")
        return False
