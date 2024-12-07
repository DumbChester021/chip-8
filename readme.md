# CHIP-8 Emulator

A modern CHIP-8 emulator implementation using Python, PyQt6, and Pygame. This emulator provides a full-featured development environment with debugging tools and configurable settings.

## Attribution

This project was developed by [Your Name] with significant assistance from Anthropic's Claude-3 Sonnet AI. The AI helped with code structure, debugging, and documentation while I handled the implementation and design decisions.

## Current State and Limitations

⚠️ **Work in Progress**: While the core CHIP-8 emulation is functional, this project is still under development and has several limitations:

### Working Features

- Basic CHIP-8 instruction set execution
- ROM loading and execution
- Basic display output
- Keyboard input
- Simple sound implementation

### Known Issues and Incomplete Features

- Debug tools are partially implemented:
  - Memory Viewer shows data but lacks full functionality
  - CPU Viewer is incomplete
  - Display Viewer needs optimization
  - Input Viewer needs refinement
- Configuration system needs improvement:
  - Some settings may not take effect
  - Configuration persistence is unreliable
- Sound implementation is basic and may not be accurate
- Performance optimization is needed
- No save state functionality
- Missing error handling in several areas
- Limited ROM compatibility testing

### Future Improvements

- Complete implementation of all debug tools
- Add proper error handling and user feedback
- Implement save states
- Improve configuration system
- Add ROM compatibility database
- Optimize performance
- Add more extensive documentation
- Add unit tests

## Features

- **Full CHIP-8 Instruction Set Support**: Implements all standard CHIP-8 instructions
- **Modern GUI Interface**: Built with PyQt6 for a native look and feel
- **Real-time Debugging Tools**:
  - Memory Viewer
  - CPU State Monitor
  - Display Debugger
  - Input Viewer
- **Configurable Settings**:
  - CPU frequency
  - Display colors
  - Sound settings
  - Input mapping
- **Sound Support**: Emulates the original CHIP-8 sound capabilities
- **Cross-platform**: Works on Windows, Linux, and macOS

## Requirements

- Python 3.8+
- PyQt6
- Pygame
- NumPy

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/chip8-emulator.git
cd chip8-emulator
```

2. Install dependencies:

```bash
pip install PyQt6 pygame numpy
```

## Usage

Run the emulator:

```bash
python main.py
```

### Loading ROMs

1. Click `File > Load ROM` or use `Ctrl+O`
2. Select a CHIP-8 ROM file (`.ch8` extension)
3. The emulator will automatically start running the ROM

### Controls

Default CHIP-8 keypad mapping:

```
CHIP-8 Key | Keyboard
-----------|---------
   1-4     |  1234
   4-7     |  QWER
   7-A     |  ASDF
   A-F     |  ZXCV
```

### Debug Tools

Access debugging tools through the Debug menu:

- **Memory Viewer**: Examine and monitor system memory
- **CPU Viewer**: Monitor CPU state, registers, and execution
- **Display Viewer**: Debug display output with zoom and grid options
- **Input Viewer**: Monitor input states in real-time

## Technical Specifications

### CHIP-8 System Architecture

- **Memory**: 4KB (4096 bytes)
- **Display**: 64x32 pixels monochrome
- **Registers**:
  - 16 general purpose 8-bit registers (V0-VF)
  - 16-bit index register (I)
  - 16-bit program counter (PC)
- **Timers**:
  - Delay timer (60Hz)
  - Sound timer (60Hz)
- **Stack**: 16 16-bit values
- **Input**: 16-key hexadecimal keypad

### Memory Map

```
0x000-0x1FF - CHIP-8 interpreter (contains font set in emu)
0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
0x200-0xFFF - Program ROM and work RAM
```

## Configuration

The emulator can be configured through the `File > Configuration` menu:

- CPU frequency
- Display scale and colors
- Sound frequency and volume
- Display optimization settings

Settings are automatically saved to `config.json`.

## Development

### Project Structure

```
chip8-emulator/
├── main.py           # Main entry point
├── cpu.py           # CPU implementation
├── memory.py        # Memory management
├── display.py       # Display handling
├── input.py         # Input processing
├── sound.py         # Sound implementation
├── config.py        # Configuration management
├── debug_viewers.py # Debug tools
└── menu.py          # Menu system
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Cowgod&#39;s CHIP-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)
- [CHIP-8 Wikipedia Article](https://en.wikipedia.org/wiki/CHIP-8)
