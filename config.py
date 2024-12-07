import json
import os
from dataclasses import dataclass, asdict

@dataclass
class EmulatorConfig:
    # CPU configuration
    cpu_frequency: int = 500  # Hz
    instructions_per_frame: int = 8
    
    # Display configuration
    display_scale: int = 10
    foreground_color: tuple = (255, 255, 255)
    background_color: tuple = (0, 0, 0)
    optimize_display_updates: bool = True
    
    # Sound configuration
    sound_frequency: int = 440  # Hz
    sound_volume: float = 0.5
    
    # Input configuration
    input_repeat_delay: int = 200  # ms
    input_repeat_rate: int = 50   # ms
    
    @classmethod
    def load(cls, filepath='config.json'):
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Convert tuple strings back to tuples for colors
                if 'foreground_color' in data:
                    data['foreground_color'] = tuple(data['foreground_color'])
                if 'background_color' in data:
                    data['background_color'] = tuple(data['background_color'])
                return cls(**data)
        return cls()
    
    def save(self, filepath='config.json'):
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=4) 