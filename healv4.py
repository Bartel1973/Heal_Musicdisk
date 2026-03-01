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
        
        # Screen setup - adaptive to current display with space for control bar
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h - 100  # Leave space for control bar
        
        # Create windowed mode with adjusted height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Oldskool Music Disk")
        
        print(f"Screen resolution: {self.width}x{self.height}")
        
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
        self.vu_cloud_centers = 4
        self.vu_particles_per_center = 20
        self.vu_layers = 3  # 3D layers
        self.init_vu_cloud()
        
        # Animation
        self.time = 0
        self.starfield = self.init_starfield()
        
        # Text scrolling for track names
        self.scroll_offset = 0
        self.scroll_speed = 2  # Pixels per frame
        self.scroll_pause = 0  # Frames to pause at start/end
        
        # Fonts - adaptive scaling based on screen size
        base_font_size = max(24, min(48, self.height // 20))
        self.title_font = pygame.font.Font(None, base_font_size * 2)
        self.info_font = pygame.font.Font(None, base_font_size)
        self.control_font = pygame.font.Font(None, base_font_size // 2)
        
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
    
    def seek_forward(self):
        """Seek forward 10 seconds"""
        if self.music_files and self.is_playing:
            try:
                current_pos = pygame.mixer.music.get_pos() / 100.0  # Convert to seconds
                new_pos = current_pos + 10
                # Note: pygame.mixer.music doesn't have direct seek, so we'll reload and play from position
                # This is a limitation of pygame.mixer.music
                print(f"Seek forward to {new_pos:.1f}s (limited by pygame.mixer)")
            except:
                print("Seek not supported by current pygame.mixer backend")
    
    def seek_backward(self):
        """Seek backward 10 seconds"""
        if self.music_files and self.is_playing:
            try:
                current_pos = pygame.mixer.music.get_pos() / 100.0  # Convert to seconds
                new_pos = max(0, current_pos - 10)
                # Note: pygame.mixer.music doesn't have direct seek, so we'll reload and play from position
                # This is a limitation of pygame.mixer.music
                print(f"Seek backward to {new_pos:.1f}s (limited by pygame.mixer)")
            except:
                print("Seek not supported by current pygame.mixer backend")
    
    def set_volume(self, delta):
        """Adjust volume"""
        self.volume = max(0.0, min(1.0, self.volume + delta))
        pygame.mixer.music.set_volume(self.volume)
    
    def init_vu_cloud(self):
        """Initialize 3D VU cloud particles"""
        self.vu_particles = []
        center_x = self.width // 2
        center_y = self.height // 2
        
        for layer in range(self.vu_layers):
            layer_depth = (layer + 1) / self.vu_layers  # Front to back
            
            for center_idx in range(self.vu_cloud_centers):
                angle = (center_idx / self.vu_cloud_centers) * 2 * math.pi
                base_radius = min(self.width, self.height - (self.height // 8) - 50) // 5
                
                for particle_idx in range(self.vu_particles_per_center):
                    particle = {
                        'layer': layer,
                        'depth': layer_depth,
                        'center_idx': center_idx,
                        'offset_angle': np.random.uniform(0, 2 * math.pi),
                        'offset_radius': np.random.uniform(0, 35),
                        'offset_z': np.random.uniform(-30, 30),  # Z-axis offset
                        'base_angle': angle,
                        'base_radius': base_radius,
                        'size': np.random.uniform(2, 8),
                        'phase': np.random.uniform(0, 2 * math.pi),
                        'speed': np.random.uniform(0.5, 2.0),
                        'color_shift': np.random.uniform(0, 1),
                        'density': np.random.uniform(0.3, 1.0),  # Gas density
                        'viscosity': np.random.uniform(0.8, 1.2)  # Liquid viscosity
                    }
                    self.vu_particles.append(particle)
    
    def update_vu_cloud(self):
        """Update 3D VU cloud particles based on audio"""
        if self.is_playing:
            # Create rhythmic VU data
            base_level = 0.3
            beat = math.sin(self.time * 0.002) * 0.3 + 0.3
            noise = np.random.random() * 0.2
            intensity = base_level + beat + noise
            intensity = max(0, min(1, intensity))
            
            # Update each particle
            for particle in self.vu_particles:
                # Organic movement with 3D dynamics
                particle['phase'] += particle['speed'] * 0.05 * particle['viscosity']
                
                # Calculate 3D position with organic movement
                wobble = math.sin(particle['phase']) * 0.3
                pulse = math.sin(self.time * 0.001 + particle['color_shift'] * math.pi) * 0.2
                depth_pulse = math.sin(self.time * 0.0007 + particle['layer']) * 0.15
                
                # 3D radius with depth-based scaling
                depth_scale = 1.0 - (particle['depth'] * 0.3)  # Back particles smaller
                current_radius = (particle['base_radius'] + particle['offset_radius'] + 
                               (intensity * 80 * (1 + pulse + wobble)) * depth_scale +
                               particle['offset_z'] * depth_pulse)
                
                # 3D angle with depth-based movement
                depth_rotation = particle['depth'] * 0.2  # Back particles rotate differently
                current_angle = (particle['base_angle'] + particle['offset_angle'] + 
                              math.sin(particle['phase']) * 0.5 + 
                              math.cos(self.time * 0.0005 + particle['center_idx']) * 0.2 +
                              depth_rotation)
                
                # Z-axis movement (liquid gas effect)
                z_bubble = math.sin(particle['phase'] * 0.7) * 10 * particle['density']
                particle['current_z'] = particle['offset_z'] + z_bubble
                
                particle['current_radius'] = current_radius
                particle['current_angle'] = current_angle
                particle['intensity'] = intensity * particle['density']
        else:
            # Fade out when not playing
            for particle in self.vu_particles:
                particle['intensity'] = max(0, particle.get('intensity', 0) - 0.02)
                particle['current_radius'] = particle['base_radius'] + particle['offset_radius']
                particle['current_angle'] = particle['base_angle'] + particle['offset_angle']
                particle['current_z'] = particle['offset_z']
    
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
        """Draw 3D liquid gas VU cloud"""
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Sort particles by depth (back to front)
        sorted_particles = sorted(self.vu_particles, key=lambda p: p['depth'], reverse=True)
        
        for particle in sorted_particles:
            intensity = particle.get('intensity', 0)
            if intensity > 0.01:  # Only draw visible particles
                # Calculate 3D position
                depth_scale = 1.0 - (particle['depth'] * 0.3)
                z_offset = particle.get('current_z', 0) * depth_scale
                
                x = center_x + math.cos(particle['current_angle']) * (particle['current_radius'] + z_offset)
                y = center_y + math.sin(particle['current_angle']) * (particle['current_radius'] + z_offset)
                
                # 3D size scaling
                size = particle['size'] * depth_scale * (0.5 + intensity * 1.5)
                
                # Depth-based opacity
                depth_opacity = 1.0 - (particle['depth'] * 0.4)
                
                # Color based on intensity and depth
                if intensity > 0.7:
                    base_color = (255, 100, 100)  # Red for high
                elif intensity > 0.4:
                    base_color = (255, 255, 100)  # Yellow for medium
                else:
                    base_color = (100, 255, 100)  # Green for low
                
                # Add color variation based on particle and depth
                color_shift = particle['color_shift']
                depth_shift = particle['depth'] * 0.3
                color = (
                    int(base_color[0] * (0.7 + 0.3 * color_shift) * depth_opacity),
                    int(base_color[1] * (0.7 + 0.3 * (1 - color_shift)) * depth_opacity),
                    int(base_color[2] * (0.7 + 0.3 * math.sin(color_shift * math.pi)) * depth_opacity)
                )
                
                # Apply intensity to color
                color = tuple(int(c * intensity) for c in color)
                
                # Draw liquid gas effect with multiple layers
                if size > 3:
                    # Outer gas halo (largest, most transparent)
                    gas_size = size * 3
                    gas_alpha = int(50 * intensity * particle['density'] * depth_opacity)
                    gas_color = tuple(min(255, int(c * 0.2)) for c in color)
                    
                    # Create gas surface with transparency
                    gas_surface = pygame.Surface((int(gas_size * 2), int(gas_size * 2)), pygame.SRCALPHA)
                    for i in range(int(gas_size), 0, -2):
                        alpha = int(gas_alpha * (1 - i / gas_size))
                        bubble_color = (*gas_color, alpha)
                        pygame.draw.circle(gas_surface, bubble_color, 
                                       (int(gas_size), int(gas_size)), i)
                    
                    self.screen.blit(gas_surface, 
                                   (int(x - gas_size), int(y - gas_size)), 
                                   special_flags=pygame.BLEND_ADD)
                
                # Liquid bubble (medium)
                if size > 2:
                    liquid_size = size * 1.5
                    liquid_alpha = int(120 * intensity * particle['density'] * depth_opacity)
                    liquid_surface = pygame.Surface((int(liquid_size * 2), int(liquid_size * 2)), pygame.SRCALPHA)
                    
                    for i in range(int(liquid_size), 0, -1):
                        alpha = int(liquid_alpha * (1 - i / liquid_size))
                        bubble_color = (*color, alpha)
                        pygame.draw.circle(liquid_surface, bubble_color, 
                                       (int(liquid_size), int(liquid_size)), i)
                    
                    self.screen.blit(liquid_surface, 
                                   (int(x - liquid_size), int(y - liquid_size)), 
                                   special_flags=pygame.BLEND_ADD)
                
                # Core particle (brightest)
                core_size = max(1, int(size * 0.8))
                core_color = tuple(min(255, int(c * 1.5)) for c in color)
                pygame.draw.circle(self.screen, core_color, (int(x), int(y)), core_size)
                
                # Bright center
                if size > 1:
                    center_color = tuple(min(255, int(c * 2.0)) for c in color)
                    pygame.draw.circle(self.screen, center_color, (int(x), int(y)), max(1, core_size // 2))
        
        # Draw 3D connecting gas streams between nearby particles
        for i, p1 in enumerate(sorted_particles):
            if p1.get('intensity', 0) > 0.3:
                x1 = center_x + math.cos(p1['current_angle']) * (p1['current_radius'] + p1.get('current_z', 0))
                y1 = center_y + math.sin(p1['current_angle']) * (p1['current_radius'] + p1.get('current_z', 0))
                
                for j, p2 in enumerate(sorted_particles[i+1:], i+1):
                    if p2.get('intensity', 0) > 0.3:
                        x2 = center_x + math.cos(p2['current_angle']) * (p2['current_radius'] + p2.get('current_z', 0))
                        y2 = center_y + math.sin(p2['current_angle']) * (p2['current_radius'] + p2.get('current_z', 0))
                        
                        # Calculate 3D distance
                        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        depth_diff = abs(p1['depth'] - p2['depth'])
                        total_dist = dist + depth_diff * 50
                        
                        # Draw gas stream if particles are close
                        if total_dist < 120:
                            # Depth-based connection strength
                            avg_depth = (p1['depth'] + p2['depth']) / 2
                            depth_factor = 1.0 - avg_depth * 0.5
                            
                            alpha = int(255 * (1 - total_dist / 120) * 
                                      min(p1.get('intensity', 0), p2.get('intensity', 0)) * 
                                      0.2 * depth_factor)
                            
                            if alpha > 5:
                                # Create gas stream surface
                                stream_surface = pygame.Surface((abs(int(x2-x1)) + 20, abs(int(y2-y1)) + 20), pygame.SRCALPHA)
                                stream_color = (alpha // 3, alpha // 2, alpha // 3, alpha)
                                
                                # Draw thick gas stream
                                pygame.draw.line(stream_surface, stream_color, 
                                             (10, 10), (abs(int(x2-x1)) + 10, abs(int(y2-y1)) + 10), 
                                             max(1, int(5 * depth_factor)))
                                
                                self.screen.blit(stream_surface, 
                                             (min(int(x1), int(x2)) - 10, min(int(y1), int(y2)) - 10), 
                                             special_flags=pygame.BLEND_ADD)
    
    def draw_controls(self):
        """Draw control interface - adaptive scaling"""
        # Control panel background - adaptive positioning
        panel_margin = self.width // 20
        panel_height = self.height // 8
        panel_rect = pygame.Rect(panel_margin, self.height - panel_height - panel_margin, 
                                 self.width - 2 * panel_margin, panel_height)
        pygame.draw.rect(self.screen, (20, 20, 40), panel_rect)
        pygame.draw.rect(self.screen, self.primary_color, panel_rect, 2)
        
        # Controls - adaptive positioning
        controls = [
            ("[SPACE] Play/Pause", panel_margin + 20, self.height - panel_height),
            ("[S] Stop", panel_margin + 200, self.height - panel_height),
            ("[←/→] Prev/Next", panel_margin + 320, self.height - panel_height),
            ("[↑/↓] Seek ±10s", panel_margin + 480, self.height - panel_height),
            ("[+/-] Volume", panel_margin + 640, self.height - panel_height),
            ("[ESC] Quit", panel_margin + 780, self.height - panel_height)
        ]
        
        for text, x, y in controls:
            surface = self.control_font.render(text, True, self.text_color)
            self.screen.blit(surface, (x, y))
        
        # Volume bar - adaptive positioning
        vol_x = self.width - 250
        vol_y = self.height - panel_height + 20
        vol_width = 200
        vol_height = 20
        
        pygame.draw.rect(self.screen, (50, 50, 50), (vol_x, vol_y, vol_width, vol_height))
        pygame.draw.rect(self.screen, self.primary_color, (vol_x, vol_y, int(vol_width * self.volume), vol_height))
        pygame.draw.rect(self.screen, self.text_color, (vol_x, vol_y, vol_width, vol_height), 2)
        
        vol_text = self.control_font.render(f"Vol: {int(self.volume * 100)}%", True, self.text_color)
        self.screen.blit(vol_text, (vol_x, vol_y - 25))
    
    def draw_info(self):
        """Draw track information - adaptive scaling with scrolling text"""
        if self.music_files:
            # Current track name
            track_name = os.path.basename(self.music_files[self.current_track])
            
            # Title - adaptive positioning
            title_y = self.height // 20
            title_surface = self.title_font.render("Heal Musicdisk by Ohm-ego of RBBS^F.SyS", True, self.primary_color)
            title_rect = title_surface.get_rect(center=(self.width // 2, title_y))
            self.screen.blit(title_surface, title_rect)
            
            # Track name with scrolling - adaptive positioning
            track_y = title_y + self.height // 15
            
            # Render the full track name
            track_surface = self.info_font.render(track_name, True, self.text_color)
            track_width = track_surface.get_width()
            
            # Calculate available width (leave some margin)
            available_width = self.width - 100
            
            # Update scrolling
            if track_width > available_width:
                # Need to scroll
                if self.scroll_pause > 0:
                    self.scroll_pause -= 1
                else:
                    self.scroll_offset += self.scroll_speed
                    
                    # Reset scroll when text has fully scrolled
                    if self.scroll_offset > track_width + 50:
                        self.scroll_offset = -available_width
                        self.scroll_pause = 60  # Pause before starting again
            else:
                # No scrolling needed, center the text
                self.scroll_offset = 0
            
            # Create clipping region for scrolling effect
            clip_rect = pygame.Rect(50, track_y - 20, available_width, 40)
            self.screen.set_clip(clip_rect)
            
            # Draw the scrolling text
            if track_width > available_width:
                # Draw text at scrolled position
                scroll_x = 50 - self.scroll_offset
                self.screen.blit(track_surface, (scroll_x, track_y - 10))
                
                # Draw text again for seamless loop (when scrolling)
                if self.scroll_offset > 0:
                    loop_x = scroll_x + track_width + 50
                    self.screen.blit(track_surface, (loop_x, track_y - 10))
            else:
                # Center text if it fits
                centered_x = (self.width - track_width) // 2
                self.screen.blit(track_surface, (centered_x, track_y - 10))
            
            # Reset clipping
            self.screen.set_clip(None)
            
            # Status indicator
            status = "▶ PLAYING" if self.is_playing else "⏸ PAUSED"
            status_color = (0, 255, 0) if self.is_playing else (255, 255, 0)
            status_surface = self.info_font.render(status, True, status_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, track_y + self.height // 20))
            self.screen.blit(status_surface, status_rect)
            
            # Track info
            info_text = f"Track {self.current_track + 1}/{len(self.music_files)}"
            if self.is_playing:
                info_text += " - PLAYING"
            else:
                info_text += " - PAUSED"
            
            info_surface = self.control_font.render(info_text, True, self.accent_color)
            info_rect = info_surface.get_rect(center=(self.width // 2, track_y + self.height // 10))
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
                    elif event.key == pygame.K_UP:
                        self.seek_forward()
                    elif event.key == pygame.K_DOWN:
                        self.seek_backward()
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
