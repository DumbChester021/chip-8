class MemoryManager:
    def __init__(self):
        self.memory = [0] * 4096  # 4KB of memory
        self.display = None
        self.load_font_data()
    
    def load_font_data(self):
        # Standard CHIP-8 font set (5 bytes per character, 16 characters)
        font_data = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        
        # Load font data starting at memory location 0x50
        for i, byte in enumerate(font_data):
            self.memory[0x50 + i] = byte
    
    def read(self, address):
        """Read a byte from memory"""
        return self.memory[address & 0xFFF]  # Ensure address is within bounds
    
    def write(self, address, value):
        """Write a byte to memory"""
        self.memory[address & 0xFFF] = value & 0xFF  # Ensure address and value are within bounds
    
    def read_byte(self, address):
        """Alias for read"""
        return self.read(address)
    
    def write_byte(self, address, value):
        """Alias for write"""
        self.write(address, value)
    
    def read_word(self, address):
        """Read a 16-bit word from memory"""
        high = self.read(address)
        low = self.read(address + 1)
        return (high << 8) | low
    
    def write_word(self, address, value):
        """Write a 16-bit word to memory"""
        high = (value >> 8) & 0xFF
        low = value & 0xFF
        self.write(address, high)
        self.write(address + 1, low)
    
    def clear_display(self):
        """Clear the display"""
        if self.display:
            self.display.clear()
    
    def set_pixel(self, x, y, value):
        """Set a pixel on the display"""
        if self.display:
            return self.display.set_pixel(x, y, value)
        return False
    
    def get_memory_block(self, start, length):
        """Get a block of memory"""
        end = min(start + length, 4096)
        return self.memory[start:end]
    
    def load_rom(self, data):
        """Load ROM data into memory starting at 0x200"""
        print("Loading ROM data:")
        for i, byte in enumerate(data):
            if (0x200 + i) < 4096:  # Ensure we don't write past end of memory
                self.write(0x200 + i, byte)
                print(f"0x{0x200 + i:03X}: 0x{byte:02X}")
    
    def reset(self):
        """Reset memory to initial state"""
        self.memory = [0] * 4096
        self.load_font_data()
        if self.display:
            self.display.clear()
    
    def save_state(self):
        """Save current memory state"""
        return {
            'memory': self.memory.copy(),
            'display_buffer': [row[:] for row in self.display.buffer],
            'registers': self.cpu.registers.copy(),
            'index_register': self.cpu.index_register,
            'program_counter': self.cpu.program_counter,
            'stack': self.cpu.stack.copy(),
            'timers': (self.cpu.delay_timer, self.cpu.sound_timer)
        }
    
    def load_state(self, state):
        """Restore from saved state"""
        self.memory = state['memory'].copy()
        self.display.buffer = [row[:] for row in state['display_buffer']]
        self.cpu.registers = state['registers'].copy()
        self.cpu.index_register = state['index_register']
        self.cpu.program_counter = state['program_counter']
        self.cpu.stack = state['stack'].copy()
        self.cpu.delay_timer, self.cpu.sound_timer = state['timers']
