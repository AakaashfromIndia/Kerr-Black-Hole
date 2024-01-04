import pygame
import sys
import math

# Constants
c = 30              # Velocity of light (also affects size of event horizon)
G = 2               # Gravitational constant (affects size and impact of black hole)
dt = 0.1            # Affects the dilation outside and inside the event horizon

# Particle (Photon)
class Photon:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(-c, 0)
        self.capture = False
        self.angle = 0

    def update(self):
        if not self.capture:
            self.pos += self.vel * dt
        else:
            self.gravitational_capture_inward()

    def show(self):
        pygame.draw.circle(screen, (0, 0, 255), (int(self.pos.x), int(self.pos.y)), 4)      #We can adjust the colour and size of the photon/particles here

    def gravitational_capture(self, event_horizon_radius):      #Orbital decay
        self.capture = True      
        distance_to_center = self.pos.distance_to(KerrBH.pos)   

        if distance_to_center <= event_horizon_radius:      #To check if the photon has entered the event horizon 
            angle_to_center = math.atan2(self.pos.y-KerrBH.pos.y,self.pos.x-KerrBH.pos.x)       #Calculating the initial angle to the surface. The resulting angle provides the direction of approach for the photon towards the event horizon
            angle_to_surface = math.acos(min(1.0, max(-1.0, event_horizon_radius / distance_to_center)))    #This angle is crucial for determining the photon's trajectory and interaction with the event horizon.
            self.angle = angle_to_center + angle_to_surface
            self.capture_radius = event_horizon_radius
        else:
            self.angle = 0

    def gravitational_capture_inward(self):
        self.angle -= 0.05      #Adjust the angular velocity of the rotation of the black hole (Positive for clockwise and negative for counter clockwise)
        radius = max(1, self.capture_radius - abs(self.angle) * 5)  # Adjust the multiplier for a tighter or looser spiral. A higher multiplier amplifies the effect, causing the captured particle to spiral more tightly as it approaches the singularity
        self.pos.x = int(KerrBH.pos.x + radius * math.cos(self.angle))
        self.pos.y = int(KerrBH.pos.y + radius * math.sin(self.angle))

# Kerr Black Hole
class BlackHole:
    def __init__(self, x, y, mass):
        self.pos = pygame.Vector2(x, y)
        self.mass = mass
        self.rs=(2*G*self.mass)/(c**2)          #Schwartzchild radius
        self.event_horizon_radius = self.rs*2
        self.particles=[]

    def pull(self, particle):
        force = pygame.Vector2(self.pos.x-particle.pos.x, self.pos.y-particle.pos.y)
        r = max(1, force.length())

        # Check if the particle is not exactly at the singularity of the black hole (to avoid division by zero as distance = 0)
        if r > 1e-5:
            force = force.normalize()*((G*self.mass) / (r ** 2))
            particle.vel += force * dt

            # Check if the particle is too close to the singularity and remove it from the simulation
            if r < 5:
                particles.remove(particle)

            # Check if the particle enters the event horizon
            distance = math.sqrt((particle.pos.x - self.pos.x) ** 2 + (particle.pos.y - self.pos.y) ** 2)
            if not particle.capture and distance < self.event_horizon_radius:
                particle.gravitational_capture(self.event_horizon_radius)

    def update_particles(self):
        for particle in self.particles:
            distance = math.sqrt((particle.pos.x - self.pos.x) ** 2 + (particle.pos.y - self.pos.y) ** 2)

            if particle.capture:
                particle.gravitational_capture_inward()
            elif distance < self.event_horizon_radius or abs(distance - self.event_horizon_radius) < 1e-5:
                angle = math.atan2(particle.pos.y - self.pos.y, particle.pos.x - self.pos.x)
                particle.vel += pygame.Vector2(7, 0).rotate(2 * angle)
            else:
                angle = math.atan2(particle.pos.y - self.pos.y, particle.pos.x - self.pos.x)    #If the particle is outside the event horizon, they converge towards the center
                particle.vel += pygame.Vector2(7, 0).rotate(2 * angle)

    def draw_event_horizon(self):
        draw_dotted_circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.event_horizon_radius, width=2, num_dots=50)        #Using a circle made of dotted lines
        for r in range(int(self.rs), 0, -1):
            grey_value = int(255 * (r / self.rs))
            pygame.draw.circle(screen, (255-grey_value, 255-grey_value, 255-grey_value), (int(self.pos.x), int(self.pos.y)), r)         #Using concentric circles to represent the black hole - white at the centre, black as it moves away

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kerr Black Hole Simulation")
clock = pygame.time.Clock()

# Initialization
KerrBH = BlackHole(WIDTH / 2, HEIGHT / 2, 10000)

particles = []

# Button to send a horizontal beam of particles
beam_button = pygame.Rect(20, 20, 280, 35)
beam_button_color = (0, 255, 0)

def draw_dotted_circle(surface, color, center, radius, width=1, num_dots=100):
    angle_increment = 2 * math.pi / num_dots
    for i in range(num_dots):
        angle = i * angle_increment
        x = int(center[0] + radius * math.cos(angle))
        y = int(center[1] + radius * math.sin(angle))
        pygame.draw.circle(surface, color, (x, y), width)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if beam_button.collidepoint(event.pos):
                for y in range(0, int(HEIGHT), 10):             #Adjust this to control the distance between the particles in the beam
                    particles.append(Photon(WIDTH - 20, y))
            else:
                particles.append(Photon(event.pos[0], event.pos[1]))    #Also create a particle at the mouse click position

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, beam_button_color, beam_button)
    font = pygame.font.Font(None, 36)
    text = font.render("Send Horizontal Beam", True, (0, 0, 0))
    screen.blit(text, (30, 25))

    for p in particles:
        KerrBH.pull(p)
        p.update()
        p.show()

    KerrBH.update_particles()
    KerrBH.draw_event_horizon()

    pygame.display.flip()

    #Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
