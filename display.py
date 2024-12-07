import pygame
import os

class Display:
    WIDTH = 64
    HEIGHT = 32
    
    def __init__(self, window_id):
        # Initialize Pygame display
        if os.name == 'nt':  # Windows
            os.environ['SDL_WINDOWID'] = str(window_id)
        
        # Create two surfaces for double buffering
        self.back_surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.front_surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        
        # Use hardware-accelerated scaling with vsync hint
        os.environ['SDL_HINT_RENDER_VSYNC'] = '1'
        self.surface = pygame.display.set_mode(
            (640, 320),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.SCALED
        )
        
        # Initialize display buffer
        self.buffer = [[0 for x in range(self.WIDTH)] for y in range(self.HEIGHT)]
        self.optimize_updates = True
        self.prev_buffer = [[0 for x in range(self.WIDTH)] for y in range(self.HEIGHT)]
        
        # Add needs_update flag
        self.needs_update = True
        
        # Create pixel surfaces
        self.pixel_on = pygame.Surface((1, 1))
        self.pixel_on.fill((255, 255, 255))
        self.pixel_off = pygame.Surface((1, 1))
        self.pixel_off.fill((0, 0, 0))
        
        # Initial clear
        self.clear()
    
    def clear(self):
        """Clear the display"""
        # Clear buffers
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self.buffer[y][x] = 0
                self.prev_buffer[y][x] = 0
        
        # Clear surfaces
        self.back_surface.fill((0, 0, 0))
        self.front_surface.fill((0, 0, 0))
        self.surface.fill((0, 0, 0))
        pygame.display.flip()
        
        # Set needs_update flag
        self.needs_update = True
    
    def set_pixel(self, x, y, value):
        """Set a pixel value and return if there was a collision"""
        x = x % self.WIDTH
        y = y % self.HEIGHT
        
        old_value = self.buffer[y][x]
        new_value = old_value ^ value
        
        # Only update if the pixel value actually changed
        if self.optimize_updates and new_value == self.prev_buffer[y][x]:
            return old_value == 1 and new_value == 0
        
        # Update buffers
        self.buffer[y][x] = new_value
        self.prev_buffer[y][x] = new_value
        
        # Clear the pixel location first
        self.back_surface.fill((0, 0, 0), (x, y, 1, 1))
        
        # Draw new pixel if it should be on
        if new_value:
            self.back_surface.blit(self.pixel_on, (x, y))
        
        # Set needs_update flag
        self.needs_update = True
        
        return old_value == 1 and new_value == 0
    
    def refresh(self):
        """Optimized display refresh"""
        if not self.needs_update:
            return
        
        # Copy back buffer to front buffer
        self.front_surface.blit(self.back_surface, (0, 0))
        
        # Scale using hardware acceleration
        current_size = self.surface.get_size()
        pygame.transform.scale(self.front_surface, current_size, self.surface)
        
        # Use flip() for double buffering
        pygame.display.flip()
        self.needs_update = False
    
    def set_colors(self, fg_color, bg_color):
        """Update the display colors"""
        self.pixel_on.fill(fg_color)
        self.pixel_off.fill(bg_color)
        
        # Redraw the entire display with new colors
        self.back_surface.fill(bg_color)
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.buffer[y][x]:
                    self.back_surface.blit(self.pixel_on, (x, y))
        
        # Set needs_update flag
        self.needs_update = True
    
    def test_pattern(self, offset):
        """Draw a test pattern for debugging"""
        self.clear()
        # Draw "TEST" scrolling across the screen
        test_pattern = [
            [1,1,1,1,0,1,1,1,1,0,1,1,1,1,0,1,1,1,1],  # T E S T
            [0,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0],
            [0,0,1,0,0,1,1,1,0,0,1,1,1,0,0,0,1,0,0],
            [0,0,1,0,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0],
            [0,0,1,0,0,1,1,1,1,0,1,1,1,0,0,0,1,0,0],
        ]
        
        pattern_height = len(test_pattern)
        pattern_width = len(test_pattern[0])
        
        # Draw the pattern with offset
        y_pos = (self.HEIGHT - pattern_height) // 2
        for y in range(pattern_height):
            for x in range(pattern_width):
                screen_x = (x + offset) % self.WIDTH
                if 0 <= screen_x < self.WIDTH:
                    self.set_pixel(screen_x, y_pos + y, test_pattern[y][x])
    