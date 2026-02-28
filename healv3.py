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
        self.vu_waves = []
        self.vu_wave_count = 8  # Number of plasma waves
        self.vu_segments = 64  # Segments per wave
        self.init_plasma_waves()
        
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
        
        # Set up music end event
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
    
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
    
    def init_plasma_waves(self):
        """Initialize plasma wave VU effect"""
        self.vu_waves = []
        
        for wave_idx in range(self.vu_wave_count):
            wave = {
                'index': wave_idx,
                'base_y': (wave_idx + 1) * (self.height / (self.vu_wave_count + 1)),
                'amplitude': np.random.uniform(20, 40),
                'frequency': np.random.uniform(0.01, 0.03),
                'phase': np.random.uniform(0, 2 * math.pi),
                'speed': np.random.uniform(0.5, 2.0),
                'color_phase': np.random.uniform(0, 2 * math.pi),
                'thickness': np.random.uniform(2, 5),
                'intensity_history': [0] * 10,  # Smooth intensity changes
                'ripple_phase': np.random.uniform(0, 2 * math.pi),
                'vertical_offset': np.random.uniform(-20, 20)
            }
            self.vu_waves.append(wave)
    
    def update_plasma_waves(self):
        """Update plasma wave VU effect based on audio"""
        if self.is_playing:
            # Create rhythmic VU data
            base_level = 0.3
            beat = math.sin(self.time * 0.002) * 0.3 + 0.3
            noise = np.random.random() * 0.2
            intensity = base_level + beat + noise
            intensity = max(0, min(1, intensity))
            
            # Update each wave
            for wave in self.vu_waves:
                # Update intensity history for smooth transitions
                wave['intensity_history'].pop(0)
                wave['intensity_history'].append(intensity)
                
                # Smooth intensity
                smooth_intensity = sum(wave['intensity_history']) / len(wave['intensity_history'])
                
                # Update wave parameters
                wave['phase'] += wave['speed'] * 0.02
                wave['color_phase'] += wave['speed'] * 0.01
                wave['ripple_phase'] += 0.03
                
                # Dynamic amplitude based on intensity
                wave['current_amplitude'] = wave['amplitude'] * (0.5 + smooth_intensity * 1.5)
                wave['current_intensity'] = smooth_intensity
        else:
            # Fade out when not playing
            for wave in self.vu_waves:
                wave['intensity_history'] = [max(0, val - 0.02) for val in wave['intensity_history']]
                wave['current_amplitude'] = wave['amplitude'] * 0.3
                wave['current_intensity'] = max(0, wave.get('current_intensity', 0) - 0.02)
    
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
    
    def draw_plasma_waves(self):
        """Draw plasma wave VU effect"""
        for wave in self.vu_waves:
            intensity = wave.get('current_intensity', 0)
            if intensity > 0.01:  # Only draw visible waves
                
                # Create plasma surface for this wave
                plasma_surface = pygame.Surface((self.width, int(wave['thickness'] * 4)), pygame.SRCALPHA)
                
                # Draw plasma wave segments
                points = []
                for segment in range(self.vu_segments + 1):
                    x = (segment / self.vu_segments) * self.width
                    
                    # Multiple sine waves for complex plasma effect
                    wave1 = math.sin(x * wave['frequency'] + wave['phase']) * wave['current_amplitude']
                    wave2 = math.sin(x * wave['frequency'] * 2 + wave['phase'] * 1.5) * wave['current_amplitude'] * 0.5
                    wave3 = math.cos(x * wave['frequency'] * 0.5 + wave['ripple_phase']) * wave['current_amplitude'] * 0.3
                    
                    # Ripple effect
                    ripple = math.sin(segment * 0.2 + wave['ripple_phase']) * 10 * intensity
                    
                    # Combine waves
                    y = wave['base_y'] + wave['vertical_offset'] + wave1 + wave2 + wave3 + ripple
                    points.append((x, y))
                
                # Draw plasma wave with gradient
                if len(points) > 1:
                    # Create color based on intensity and phase
                    hue = (wave['color_phase'] + intensity * math.pi) % (2 * math.pi)
                    
                    # Convert HSV to RGB for smooth color transitions
                    if hue < math.pi * 2/3:  # Red to Green
                        r = int(255 * (1 - hue / (math.pi * 2/3)))
                        g = int(255 * (hue / (math.pi * 2/3)))
                        b = 0
                    elif hue < math.pi * 4/3:  # Green to Blue
                        r = 0
                        g = int(255 * (1 - (hue - math.pi * 2/3) / (math.pi * 2/3)))
                        b = int(255 * ((hue - math.pi * 2/3) / (math.pi * 2/3)))
                    else:  # Blue to Red
                        r = int(255 * ((hue - math.pi * 4/3) / (math.pi * 2/3)))
                        g = 0
                        b = int(255 * (1 - (hue - math.pi * 4/3) / (math.pi * 2/3)))
                    
                    # Apply intensity
                    base_color = (
                        int(r * intensity),
                        int(g * intensity),
                        int(b * intensity)
                    )
                    
                    # Draw multiple layers for glow effect
                    for layer in range(3):
                        layer_intensity = intensity * (1 - layer * 0.3)
                        layer_thickness = wave['thickness'] * (3 - layer)
                        layer_color = tuple(int(c * layer_intensity) for c in base_color)
                        
                        # Draw wave segment
                        layer_points = [(p[0], p[1] + layer * 2) for p in points]
                        
                        if len(layer_points) > 1:
                            # Draw with anti-aliasing
                            pygame.draw.lines(plasma_surface, layer_color, False, layer_points, int(layer_thickness))
                    
                    # Add glow effect
                    glow_surface = pygame.Surface((self.width, int(wave['thickness'] * 8)), pygame.SRCALPHA)
                    glow_color = (*base_color, int(50 * intensity))
                    
                    glow_points = [(p[0], p[1] - wave['base_y'] + wave['thickness'] * 4) for p in points]
                    if len(glow_points) > 1:
                        pygame.draw.lines(glow_surface, glow_color, False, glow_points, int(wave['thickness'] * 2))
                    
                    # Blit glow to main surface
                    self.screen.blit(glow_surface, (0, wave['base_y'] - wave['thickness'] * 4), special_flags=pygame.BLEND_ADD)
                    
                    # Blit main plasma wave
                    self.screen.blit(plasma_surface, (0, wave['base_y'] - wave['thickness'] * 2), special_flags=pygame.BLEND_ADD)
        
        # Draw interference patterns between waves
        for i, wave1 in enumerate(self.vu_waves):
            if wave1.get('current_intensity', 0) > 0.3:
                for j, wave2 in enumerate(self.vu_waves[i+1:], i+1):
                    if wave2.get('current_intensity', 0) > 0.3:
                        # Calculate interference points
                        for segment in range(0, self.vu_segments, 8):  # Sample every 8th segment
                            x = (segment / self.vu_segments) * self.width
                            
                            # Get wave positions
                            y1 = wave1['base_y'] + math.sin(x * wave1['frequency'] + wave1['phase']) * wave1['current_amplitude']
                            y2 = wave2['base_y'] + math.sin(x * wave2['frequency'] + wave2['phase']) * wave2['current_amplitude']
                            
                            # Draw interference pattern
                            dist = abs(y2 - y1)
                            if dist < 50:  # Waves are close enough to interfere
                                avg_intensity = (wave1.get('current_intensity', 0) + wave2.get('current_intensity', 0)) / 2
                                alpha = int(100 * avg_intensity * (1 - dist / 50))
                                
                                if alpha > 10:
                                    interference_color = (alpha, alpha // 2, alpha)
                                    pygame.draw.circle(self.screen, interference_color, (int(x), int((y1 + y2) // 2)), 3)
    
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
                elif event.type == pygame.USEREVENT + 1:
                    # Music ended - automatically play next track
                    self.next_track()
            
            # Clear screen
            self.screen.fill(self.bg_color)
            
            # Draw effects
            self.draw_starfield()
            
            # Update and draw plasma waves
            self.update_plasma_waves()
            self.draw_plasma_waves()
            
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
