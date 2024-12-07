class CPU:
    def __init__(self, memory_manager, input_manager, sound_manager):
        self.memory_manager = memory_manager
        self.input_manager = input_manager
        self.sound_manager = sound_manager
        self.main_window = None
        self.registers = [0] * 16
        self.index_register = 0
        self.program_counter = 0x200
        self.stack = []
        self.stack_pointer = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.decoded_instruction = 0
        self.reset()
    
    def reset(self):
        self.registers = [0] * 16  # Clear all general purpose registers (V0-VF)
        self.index_register = 0    # Clear index register (I)
        self.program_counter = 0x200  # Reset PC to start of program memory
        self.stack = []            # Clear the stack
        self.stack_pointer = 0     # Reset stack pointer
        self.delay_timer = 0       # Clear delay timer
        self.sound_timer = 0       # Clear sound timer
        self.decoded_instruction = 0  # Clear current instruction
    
    def step(self):
        # Fetch instruction from memory
        instruction = self.fetch_instruction()
        
        # Decode the instruction
        decoded = self.decode_instruction(instruction)
        
        # Execute the instruction
        self.execute_instruction(decoded)
    
    def fetch_instruction(self):
        # Get two consecutive bytes from memory and combine them into a 16-bit instruction
        high_byte = self.memory_manager.read_byte(self.program_counter)
        low_byte = self.memory_manager.read_byte(self.program_counter + 1)
        instruction = (high_byte << 8) | low_byte
        
        # Increment program counter by 2 (since each instruction is 2 bytes)
        self.program_counter += 2
        
        return instruction
    
    def decode_instruction(self, instruction):
        # Break down the instruction into its components
        # First nibble (4 bits) is the opcode
        opcode = (instruction & 0xF000) >> 12
        
        # Second nibble, often used as a 4-bit register identifier (x)
        x = (instruction & 0x0F00) >> 8
        
        # Third nibble, often used as a 4-bit register identifier (y)
        y = (instruction & 0x00F0) >> 4
        
        # Fourth nibble, often used as a 4-bit immediate value
        n = instruction & 0x000F
        
        # Last byte (8 bits), often used as an 8-bit immediate value
        kk = instruction & 0x00FF
        
        # Last 12 bits, often used as a memory address
        nnn = instruction & 0x0FFF
        
        self.decoded_instruction = instruction
        
        return {
            'opcode': opcode,
            'x': x,
            'y': y,
            'n': n,
            'kk': kk,
            'nnn': nnn,
            'raw': instruction
        }
    def execute_instruction(self, decoded_instr):
        opcode = decoded_instr['opcode']
        x = decoded_instr['x']
        y = decoded_instr['y']
        n = decoded_instr['n']
        kk = decoded_instr['kk']
        nnn = decoded_instr['nnn']
        
        # Switch based on the first nibble (opcode)
        if opcode == 0x0:
            if kk == 0xE0:  # 00E0: Clear screen
                self.memory_manager.clear_display()
            elif kk == 0xEE:  # 00EE: Return from subroutine
                self.program_counter = self.stack.pop()
                self.stack_pointer -= 1
                
        elif opcode == 0x1:  # 1NNN: Jump to address NNN
            self.program_counter = nnn
            
        elif opcode == 0x2:  # 2NNN: Call subroutine at NNN
            self.stack_pointer += 1
            self.stack.append(self.program_counter)
            self.program_counter = nnn
            
        elif opcode == 0x3:  # 3XKK: Skip next instruction if VX == KK
            if self.registers[x] == kk:
                self.program_counter += 2
                
        elif opcode == 0x4:  # 4XKK: Skip next instruction if VX != KK
            if self.registers[x] != kk:
                self.program_counter += 2
                
        elif opcode == 0x5:  # 5XY0: Skip next instruction if VX == VY
            if self.registers[x] == self.registers[y]:
                self.program_counter += 2
                
        elif opcode == 0x6:  # 6XKK: Set VX = KK
            self.registers[x] = kk
            
        elif opcode == 0x7:  # 7XKK: Set VX = VX + KK
            self.registers[x] = (self.registers[x] + kk) & 0xFF
            
        elif opcode == 0x8:
            if n == 0x0:  # 8XY0: Set VX = VY
                self.registers[x] = self.registers[y]
            elif n == 0x1:  # 8XY1: Set VX = VX OR VY
                self.registers[x] |= self.registers[y]
            elif n == 0x2:  # 8XY2: Set VX = VX AND VY
                self.registers[x] &= self.registers[y]
            elif n == 0x3:  # 8XY3: Set VX = VX XOR VY
                self.registers[x] ^= self.registers[y]
            elif n == 0x4:  # 8XY4: Set VX = VX + VY, set VF = carry
                result = self.registers[x] + self.registers[y]
                self.registers[0xF] = 1 if result > 0xFF else 0
                self.registers[x] = result & 0xFF
            elif n == 0x5:  # 8XY5: Set VX = VX - VY, set VF = NOT borrow
                self.registers[0xF] = 1 if self.registers[x] >= self.registers[y] else 0
                self.registers[x] = (self.registers[x] - self.registers[y]) & 0xFF
            elif n == 0x6:  # 8XY6: Set VX = VY >> 1, set VF = LSB of VY
                self.registers[0xF] = self.registers[y] & 0x1
                self.registers[x] = self.registers[y] >> 1
            elif n == 0x7:  # 8XY7: Set VX = VY - VX, set VF = NOT borrow
                self.registers[0xF] = 1 if self.registers[y] >= self.registers[x] else 0
                self.registers[x] = (self.registers[y] - self.registers[x]) & 0xFF
            elif n == 0xE:  # 8XYE: Set VX = VY << 1, set VF = MSB of VY
                self.registers[0xF] = (self.registers[y] & 0x80) >> 7
                self.registers[x] = (self.registers[y] << 1) & 0xFF
                
        elif opcode == 0x9:  # 9XY0: Skip next instruction if VX != VY
            if self.registers[x] != self.registers[y]:
                self.program_counter += 2
                
        elif opcode == 0xA:  # ANNN: Set I = NNN
            self.index_register = nnn
            
        elif opcode == 0xB:  # BNNN: Jump to V0 + NNN
            self.program_counter = nnn + self.registers[0]
            
        elif opcode == 0xC:  # CXKK: Set VX = random byte AND KK
            import random
            self.registers[x] = random.randint(0, 255) & kk
            
        elif opcode == 0xD:  # DXYN: Draw sprite at (VX, VY) with N bytes of sprite data starting at I
            x_coord = self.registers[x] & 0xFF
            y_coord = self.registers[y] & 0xFF
            self.registers[0xF] = 0
            
            for row in range(n):
                sprite_byte = self.memory_manager.read_byte(self.index_register + row)
                for col in range(8):
                    if (sprite_byte & (0x80 >> col)) != 0:
                        if self.memory_manager.set_pixel(x_coord + col, y_coord + row, 1):
                            self.registers[0xF] = 1
                            
        elif opcode == 0xE:
            if kk == 0x9E:  # EX9E: Skip next instruction if key VX is pressed
                if self.input_manager.is_key_pressed(self.registers[x]):
                    self.program_counter += 2
            elif kk == 0xA1:  # EXA1: Skip next instruction if key VX is not pressed
                if not self.input_manager.is_key_pressed(self.registers[x]):
                    self.program_counter += 2
                    
        elif opcode == 0xF:
            if kk == 0x07:  # FX07: Set VX = delay timer
                self.registers[x] = self.delay_timer
            elif kk == 0x0A:  # FX0A: Wait for key press, store key in VX
                key = self.input_manager.wait_for_keypress()
                if key is not None:
                    self.registers[x] = key
                else:
                    self.program_counter -= 2  # Repeat instruction if no key pressed
            elif kk == 0x15:  # FX15: Set delay timer = VX
                self.delay_timer = self.registers[x]
            elif kk == 0x18:  # FX18: Set sound timer = VX
                self.sound_timer = self.registers[x]
            elif kk == 0x1E:  # FX1E: Set I = I + VX
                self.index_register = (self.index_register + self.registers[x]) & 0xFFF
            elif kk == 0x29:  # FX29: Set I to location of sprite for digit VX
                self.index_register = self.registers[x] * 5  # Each sprite is 5 bytes
            elif kk == 0x33:  # FX33: Store BCD representation of VX in memory locations I, I+1, and I+2
                value = self.registers[x]
                self.memory_manager.write_byte(self.index_register, value // 100)
                self.memory_manager.write_byte(self.index_register + 1, (value % 100) // 10)
                self.memory_manager.write_byte(self.index_register + 2, value % 10)
            elif kk == 0x55:  # FX55: Store registers V0 through VX in memory starting at location I
                for i in range(x + 1):
                    self.memory_manager.write_byte(self.index_register + i, self.registers[i])
            elif kk == 0x65:  # FX65: Read registers V0 through VX from memory starting at location I
                for i in range(x + 1):
                    self.registers[i] = self.memory_manager.read_byte(self.index_register + i)

    def update_timers(self):
        # Update delay timer
        if self.delay_timer > 0:
            self.delay_timer -= 1
        
        # Update sound timer
        if self.sound_timer > 0:
            self.sound_timer -= 1
            self.sound_manager.start()
        else:
            self.sound_manager.stop()

