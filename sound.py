import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init(44100, -16, 1, 512)
        
        # Generate a simple square wave tone
        self.generate_tone()
        
        # Sound state
        self.is_playing = False
    
    def generate_tone(self, frequency=440, duration=0.1):
        """Generate a square wave tone at the specified frequency"""
        sample_rate = 44100
        samples = int(duration * sample_rate)
        
        # Generate time array
        t = np.linspace(0, duration, samples, False)
        
        # Generate square wave
        tone = np.sign(np.sin(2 * np.pi * frequency * t))
        
        # Scale to 16-bit integer range and convert to int16
        tone = (tone * 32767).astype(np.int16)
        
        # Create pygame Sound object
        self.tone = pygame.mixer.Sound(tone.tobytes())
        
        # Set volume to 50%
        self.tone.set_volume(0.5)
    
    def start(self):
        """Start playing the tone if not already playing"""
        if not self.is_playing:
            self.tone.play(-1)  # -1 means loop indefinitely
            self.is_playing = True
    
    def stop(self):
        """Stop playing the tone"""
        if self.is_playing:
            self.tone.stop()
            self.is_playing = False
    
    def cleanup(self):
        """Clean up pygame mixer"""
        pygame.mixer.quit() 