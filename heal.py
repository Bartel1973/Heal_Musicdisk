import pygame
import pygame.mixer
import math
import sys
import os
import numpy as np
from pygame import gfxdraw

class OldskoolMusicDisk:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Screen setup
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Oldskool Music Disk")
        self.clock = pygame.time.Clock()
        
        # Colors (oldskool palette)
        self.bg_color = (10, 10, 20)
        self.primary_color = (0, 255, 0)
        self.secondary_color = (255, 0, 255)
        self.accent_color = (0, 255, 255)
        self.text_color = (255, 255, 255)
        
        # Music setup
        self.music_files = self.find_mp3_files()
        self.current_track = 0
        self.is_playing = False
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)
        
        # VU meter setup
        self.vu_bars = 32
        self.vu_history = [[0] * self.vu_bars for _ in range(20)]  # History for trail effect
        self.vu_peaks = [0] * self.vu_bars
        self.peak_decay = 0.95
        
        # Animation
        self.time = 0
        self.starfield = self.init_starfield()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 32)
        self.control_font = pygame.font.Font(None, 24)
        
        # Load first track
        if self.music_files:
            self.load_track(0)
    
    def find_mp3_files(self):
        """Find all MP3 files in current directory"""
        mp3_files = []
        for file in os.listdir('.'):
            if file.lower().endswith('.mp3'):
                mp3_files.append(file)
        return mp3_files
    
    def init_starfield(self):
        """Initialize background starfield"""
        stars = []
        for _ in range(200):
            stars.append({
                'x': (np.random.random() - 0.5) * self.width * 2,  # Range: -width to +width
                'y': (np.random.random() - 0.5) * self.height * 2,  # Range: -height to +height
                'z': np.random.random() * 1000,
                'speed': np.random.random() * 2 + 1
            })
        return stars
    
    def load_track(self, index):
        """Load and play track at given index"""
        if 0 <= index < len(self.music_files):
            self.current_track = index
            try:
                pygame.mixer.music.load(self.music_files[index])
                if self.is_playing:
                    pygame.mixer.music.play()
                return True
            except pygame.error as e:
                print(f"Error loading {self.music_files[index]}: {e}")
                return False
        return False
    
    def play_pause(self):
        """Toggle play/pause"""
        if not self.music_files:
            return
        
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        else:
            if pygame.mixer.music.get_busy() == 0:  # Not playing
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            self.is_playing = True
    
    def stop(self):
        """Stop music"""
        pygame.mixer.music.stop()
        self.is_playing = False
    
    def next_track(self):
        """Go to next track"""
        if self.music_files:
            self.load_track((self.current_track + 1) % len(self.music_files))
    
    def prev_track(self):
        """Go to previous track"""
        if self.music_files:
            self.load_track((self.current_track - 1) % len(self.music_files))
    
    def set_volume(self, delta):
        """Adjust volume"""
        self.volume = max(0.0, min(1.0, self.volume + delta))
        pygame.mixer.music.set_volume(self.volume)
    
    def simulate_vu_data(self):
        """Simulate VU meter data (since we can't get real audio data from pygame.mixer)"""
        if self.is_playing:
            # Create rhythmic VU data based on time
            base_level = 0.3
            beat = math.sin(self.time * 0.002) * 0.3 + 0.3
            noise = np.random.random(self.vu_bars) * 0.2
            
            # Create frequency-like pattern
            freq_pattern = np.sin(np.linspace(0, math.pi * 4, self.vu_bars) + self.time * 0.001)
            
            vu_data = base_level + beat + noise + freq_pattern * 0.2
            vu_data = np.clip(vu_data, 0, 1)
        else:
            vu_data = np.zeros(self.vu_bars)
        
        return vu_data
    
    def update_vu_meter(self):
        """Update VU meter data"""
        vu_data = self.simulate_vu_data()
        
        # Update history (shift and add new data)
        self.vu_history.pop(0)
        self.vu_history.append(vu_data.tolist())
        
        # Update peaks
        for i in range(self.vu_bars):
            if vu_data[i] > self.vu_peaks[i]:
                self.vu_peaks[i] = vu_data[i]
            else:
                self.vu_peaks[i] *= self.peak_decay
    
    def draw_starfield(self):
        """Draw animated starfield background"""
        for star in self.starfield:
            # Move star
            star['z'] -= star['speed']
            if star['z'] <= 0:
                star['z'] = 1000
                star['x'] = (np.random.random() - 0.5) * self.width * 2
                star['y'] = (np.random.random() - 0.5) * self.height * 2
            
            # 3D projection
            perspective = 500 / star['z']
            x = star['x'] * perspective + self.width / 2
            y = star['y'] * perspective + self.height / 2
            size = max(1, int(3 * perspective))
            brightness = int(255 * (1 - star['z'] / 1000))
            
            # Only draw if on screen
            if 0 <= x < self.width and 0 <= y < self.height:
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (int(x), int(y)), size)
    
    def draw_vu_meter(self):
        """Draw fancy VU meter with effects"""
        center_x = self.width // 2
        center_y = self.height // 2
        max_radius = min(self.width, self.height) // 3
        
        # Draw circular VU meter
        for i in range(self.vu_bars):
            angle = (i / self.vu_bars) * 2 * math.pi - math.pi / 2
            
            # Get current and historical values
            current_value = self.vu_history[-1][i] if self.vu_history else 0
            peak_value = self.vu_peaks[i]
            
            # Draw bar
            for j, history_data in enumerate(reversed(self.vu_history[-5:])):  # Trail effect
                history_value = history_data[i]  # Get specific bar value from history
                radius = max_radius * (0.7 + 0.3 * history_value)
                alpha = (j + 1) / 5  # Fade trail
                
                # Color based on intensity
                if history_value > 0.8:
                    color = (255 * alpha, 0, 0)  # Red for high
                elif history_value > 0.6:
                    color = (255 * alpha, 255 * alpha, 0)  # Yellow for medium
                else:
                    color = (0, 255 * alpha, 0)  # Green for low
                
                # Calculate bar endpoints
                inner_radius = max_radius * 0.6
                x1 = center_x + math.cos(angle) * inner_radius
                y1 = center_y + math.sin(angle) * inner_radius
                x2 = center_x + math.cos(angle) * radius
                y2 = center_y + math.sin(angle) * radius
                
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 3)
            
            # Draw peak indicator
            if peak_value > 0.1:
                peak_radius = max_radius * (0.7 + 0.3 * peak_value)
                x_peak = center_x + math.cos(angle) * peak_radius
                y_peak = center_y + math.sin(angle) * peak_radius
                pygame.draw.circle(self.screen, self.accent_color, (int(x_peak), int(y_peak)), 2)
        
        # Draw center circle
        pygame.draw.circle(self.screen, self.primary_color, (center_x, center_y), int(max_radius * 0.6), 2)
        
        # Draw frequency spectrum bars (inner circle)
        for i in range(16):
            angle = (i / 16) * 2 * math.pi - math.pi / 2
            value = self.vu_history[-1][i * 2] if self.vu_history else 0
            bar_length = max_radius * 0.5 * value
            
            x1 = center_x + math.cos(angle) * (max_radius * 0.3)
            y1 = center_y + math.sin(angle) * (max_radius * 0.3)
            x2 = center_x + math.cos(angle) * (max_radius * 0.3 + bar_length)
            y2 = center_y + math.sin(angle) * (max_radius * 0.3 + bar_length)
            
            pygame.draw.line(self.screen, self.secondary_color, (x1, y1), (x2, y2), 2)
    
    def draw_controls(self):
        """Draw control interface"""
        # Control panel background
        panel_rect = pygame.Rect(50, self.height - 150, self.width - 100, 100)
        pygame.draw.rect(self.screen, (20, 20, 40), panel_rect)
        pygame.draw.rect(self.screen, self.primary_color, panel_rect, 2)
        
        # Controls
        controls = [
            ("[SPACE] Play/Pause", 70, self.height - 120),
            ("[S] Stop", 250, self.height - 120),
            ("[←] Previous", 400, self.height - 120),
            ("[→] Next", 550, self.height - 120),
            ("[+/-] Volume", 700, self.height - 120),
        ]
        
        for text, x, y in controls:
            surface = self.control_font.render(text, True, self.text_color)
            self.screen.blit(surface, (x, y))
        
        # Volume bar
        vol_x = 850
        vol_y = self.height - 120
        vol_width = 200
        vol_height = 20
        
        pygame.draw.rect(self.screen, (50, 50, 50), (vol_x, vol_y, vol_width, vol_height))
        pygame.draw.rect(self.screen, self.primary_color, (vol_x, vol_y, int(vol_width * self.volume), vol_height))
        pygame.draw.rect(self.screen, self.text_color, (vol_x, vol_y, vol_width, vol_height), 2)
        
        vol_text = self.control_font.render(f"Vol: {int(self.volume * 100)}%", True, self.text_color)
        self.screen.blit(vol_text, (vol_x, vol_y - 25))
    
    def draw_info(self):
        """Draw track information"""
        if self.music_files:
            # Current track name
            track_name = os.path.basename(self.music_files[self.current_track])
            if len(track_name) > 40:
                track_name = track_name[:37] + "..."
            
            title_surface = self.title_font.render("Heal Musicdisk by Ohm-ego of RBBS^F.SyS", True, self.primary_color)
            title_rect = title_surface.get_rect(center=(self.width // 2, 50))
            self.screen.blit(title_surface, title_rect)
            
            track_surface = self.info_font.render(track_name, True, self.text_color)
            track_rect = track_surface.get_rect(center=(self.width // 2, 100))
            self.screen.blit(track_surface, track_rect)
            
            # Track info
            info_text = f"Track {self.current_track + 1}/{len(self.music_files)}"
            if self.is_playing:
                info_text += " - PLAYING"
            else:
                info_text += " - PAUSED"
            
            info_surface = self.control_font.render(info_text, True, self.accent_color)
            info_rect = info_surface.get_rect(center=(self.width // 2, 140))
            self.screen.blit(info_surface, info_rect)
        else:
            # No MP3 files found
            no_music = self.title_font.render("NO MP3 FILES FOUND", True, (255, 0, 0))
            no_music_rect = no_music.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(no_music, no_music_rect)
            
            hint = self.info_font.render("Place MP3 files in the same directory", True, self.text_color)
            hint_rect = hint.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(hint, hint_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.play_pause()
                    elif event.key == pygame.K_s:
                        self.stop()
                    elif event.key == pygame.K_LEFT:
                        self.prev_track()
                    elif event.key == pygame.K_RIGHT:
                        self.next_track()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.set_volume(0.1)
                    elif event.key == pygame.K_MINUS:
                        self.set_volume(-0.1)
            
            # Clear screen
            self.screen.fill(self.bg_color)
            
            # Draw effects
            self.draw_starfield()
            
            # Update and draw VU meter
            self.update_vu_meter()
            self.draw_vu_meter()
            
            # Draw UI
            self.draw_info()
            self.draw_controls()
            
            # Update time
            self.time += 16  # Assuming 60 FPS
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    disk = OldskoolMusicDisk()
    disk.run()
