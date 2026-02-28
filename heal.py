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
        self.vu_particles = []
        self.vu_cloud_centers = 8
        self.vu_particles_per_center = 15
        self.init_vu_cloud()
        
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
    
    def init_vu_cloud(self):
        """Initialize VU cloud particles"""
        self.vu_particles = []
        center_x = self.width // 2
        center_y = self.height // 2
        
        for center_idx in range(self.vu_cloud_centers):
            angle = (center_idx / self.vu_cloud_centers) * 2 * math.pi
            base_radius = min(self.width, self.height) // 4
            
            for particle_idx in range(self.vu_particles_per_center):
                particle = {
                    'center_idx': center_idx,
                    'offset_angle': np.random.uniform(0, 2 * math.pi),
                    'offset_radius': np.random.uniform(0, 50),
                    'base_angle': angle,
                    'base_radius': base_radius,
                    'size': np.random.uniform(2, 6),
                    'phase': np.random.uniform(0, 2 * math.pi),
                    'speed': np.random.uniform(0.5, 2.0),
                    'color_shift': np.random.uniform(0, 1)
                }
                self.vu_particles.append(particle)
    
    def update_vu_cloud(self):
        """Update VU cloud particles based on audio"""
        if self.is_playing:
            # Create rhythmic VU data
            base_level = 0.3
            beat = math.sin(self.time * 0.002) * 0.3 + 0.3
            noise = np.random.random() * 0.2
            intensity = base_level + beat + noise
            intensity = max(0, min(1, intensity))
            
            # Update each particle
            for particle in self.vu_particles:
                # Organic movement
                particle['phase'] += particle['speed'] * 0.05
                
                # Calculate position with organic movement
                wobble = math.sin(particle['phase']) * 0.3
                pulse = math.sin(self.time * 0.001 + particle['color_shift'] * math.pi) * 0.2
                
                # Dynamic radius based on audio intensity
                current_radius = (particle['base_radius'] + particle['offset_radius'] + 
                               (intensity * 80 * (1 + pulse + wobble)))
                
                # Dynamic angle with organic movement
                current_angle = (particle['base_angle'] + particle['offset_angle'] + 
                              math.sin(particle['phase']) * 0.5 + 
                              math.cos(self.time * 0.0005 + particle['center_idx']) * 0.2)
                
                particle['current_radius'] = current_radius
                particle['current_angle'] = current_angle
                particle['intensity'] = intensity
        else:
            # Fade out when not playing
            for particle in self.vu_particles:
                particle['intensity'] = max(0, particle.get('intensity', 0) - 0.02)
                particle['current_radius'] = particle['base_radius'] + particle['offset_radius']
                particle['current_angle'] = particle['base_angle'] + particle['offset_angle']
    
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
    
    def draw_vu_cloud(self):
        """Draw cloudy, dotted, amorphous VU meter"""
        center_x = self.width // 2
        center_y = self.height // 2
        
        for particle in self.vu_particles:
            intensity = particle.get('intensity', 0)
            if intensity > 0.01:  # Only draw visible particles
                # Calculate position
                x = center_x + math.cos(particle['current_angle']) * particle['current_radius']
                y = center_y + math.sin(particle['current_angle']) * particle['current_radius']
                
                # Dynamic size based on intensity
                size = particle['size'] * (0.5 + intensity * 1.5)
                
                # Color based on intensity and position
                if intensity > 0.7:
                    base_color = (255, 100, 100)  # Red for high
                elif intensity > 0.4:
                    base_color = (255, 255, 100)  # Yellow for medium
                else:
                    base_color = (100, 255, 100)  # Green for low
                
                # Add color variation based on particle
                color_shift = particle['color_shift']
                color = (
                    int(base_color[0] * (0.7 + 0.3 * color_shift)),
                    int(base_color[1] * (0.7 + 0.3 * (1 - color_shift))),
                    int(base_color[2] * (0.7 + 0.3 * math.sin(color_shift * math.pi)))
                )
                
                # Apply intensity to color
                color = tuple(int(c * intensity) for c in color)
                
                # Draw particle with glow effect
                if size > 3:
                    # Outer glow
                    glow_size = size * 2
                    glow_color = tuple(int(c * 0.3) for c in color)
                    pygame.draw.circle(self.screen, glow_color, (int(x), int(y)), int(glow_size))
                
                # Main particle
                pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))
                
                # Inner bright core
                if size > 2:
                    core_color = tuple(min(255, int(c * 1.5)) for c in color)
                    pygame.draw.circle(self.screen, core_color, (int(x), int(y)), max(1, int(size * 0.3)))
        
        # Draw connecting lines between nearby particles for cloud effect
        for i, p1 in enumerate(self.vu_particles):
            if p1.get('intensity', 0) > 0.3:
                x1 = center_x + math.cos(p1['current_angle']) * p1['current_radius']
                y1 = center_y + math.sin(p1['current_angle']) * p1['current_radius']
                
                for j, p2 in enumerate(self.vu_particles[i+1:], i+1):
                    if p2.get('intensity', 0) > 0.3:
                        x2 = center_x + math.cos(p2['current_angle']) * p2['current_radius']
                        y2 = center_y + math.sin(p2['current_angle']) * p2['current_radius']
                        
                        # Calculate distance
                        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        
                        # Draw line if particles are close
                        if dist < 100:
                            alpha = int(255 * (1 - dist / 100) * min(p1.get('intensity', 0), p2.get('intensity', 0)) * 0.3)
                            if alpha > 10:
                                line_color = (alpha // 2, alpha, alpha // 2)
                                pygame.draw.line(self.screen, line_color, (int(x1), int(y1)), (int(x2), int(y2)), 1)
    
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
            
            # Update and draw VU cloud
            self.update_vu_cloud()
            self.draw_vu_cloud()
            
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
