from _variables import *
from grid import Grid
from numba import njit
import numpy as np
from PIL import Image, ImageFilter
import pygame
import sys

def blur(surface, strength=7, scale=0.5):
    """Takes in a surface and returns a blurred version of it"""
    size = (int(WIDTH * scale), int(HEIGHT * scale))  #size of scaled down surface
    small_surface = pygame.transform.scale(surface, size)  #scaled down surface
    image = Image.frombytes('RGB', size, pygame.image.tostring(small_surface, "RGB"))  #converts surface to an image
    blurred = image.filter(ImageFilter.GaussianBlur(strength))  #adds a blur filter to the image
    return pygame.transform.scale(pygame.image.fromstring(blurred.tobytes(), size, "RGB"), (WIDTH, HEIGHT))  #converts the image into a pygame Surface and scales up

N = config.count
class Simulation:
    def __init__(self):
        """Initialisation of Simulation environment"""
        self.positions = np.random.rand(N, 2) * np.array([WIDTH, HEIGHT])  #the positions of all the particles
        self.velocities = np.zeros((N, 2))  #the velocities of all the particles
        self.particles = np.random.randint(0, len(colours), size=N)  #the particle types - determines their nature towards each other
        self.attraction_matrix = np.zeros((len(colours), len(colours)))  #the attraction matrix - determines how one type interacts with another
        self.grid = Grid(WIDTH, HEIGHT, 2 * config.influence)  #the grid - spacial partitioning technique to optimise detection of nearby particles
    
    @njit()  #numba's just-in-time compiler decorator
    def force(pos_a, pos_b, type_a, type_b, attraction_matrix, influence, beta=0.3):
        """Calculates the force between two particles"""
        dx = pos_b[0] - pos_a[0]  #difference in x co-ordinates
        dy = pos_b[1] - pos_a[1]  #difference in y co-ordinates
        distance = (dx * dx + dy * dy) ** 0.5  #eucleudian distance between the particles
        unit_dx = dx / distance  #unit distance in the x-direction
        unit_dy = dy / distance  #unit distance in the y-direction
        distance /= influence  #normalised distance
        force_magnitude = 0  #as default | when normalised distance > 1, i.e: when distance > interaction radius
        if distance < beta: force_magnitude = -1 + (distance / beta)  #universal repulsive force - to prevent collapse of particle structures
        elif beta < distance < 1: force_magnitude = (distance - beta) / (1 - beta) * attraction_matrix[type_a, type_b]  #linear interpolation of force dependant on distance
        return np.array([force_magnitude * unit_dx, force_magnitude * unit_dy])  #scaled force

    def update(self):
        """Logic to update positions and velocities of particles"""
        accelerations = np.zeros((N, 2))  #accelerations calculated every frame, therefore set to 0
        self.grid.clear()  #reset the grid
        for i in range(N): self.grid.insert(self.positions[i], i)  #populate the grid with the particle positions
        for i in range(N):  #for each particle, query neighbors within a square of side 2 * interaction radius - to get a full list of particles within its range
            position = self.positions[i]
            query = (
                max(position[0] - config.influence, 0),
                max(position[1] - config.influence, 0),
                2 * config.influence,
                2 * config.influence
            )
            nearby_particles = self.grid.query(query)  #list of particles within range that it could be affected by
            
            force = np.zeros(2)  #force initialised to 0
            for (_, j) in nearby_particles:  #loops over the nearby indexes
                if j == i:  #if the particle is itself
                    continue
                force += Simulation.force(
                    position,
                    self.positions[j],
                    self.particles[i],
                    self.particles[j],
                    self.attraction_matrix,
                    config.influence
                )
            accelerations[i] = force * config.influence 

        for i in range(N):  #adds the effect of the edge force - to prevent particles from escaping the simulation space
            position = self.positions[i]
            force = np.array([0.0, 0.0])
            if position[0] < config.fringe: force[0] = (config.fringe - position[0]) / config.fringe * config.repulsion  #left 
            elif position[0] > WIDTH - config.fringe: force[0] = - (position[0] - (WIDTH - config.fringe)) / config.fringe * config.repulsion  #right
            if position[1] < config.fringe: force[1] = (config.fringe - position[1]) / config.fringe * config.repulsion  #top
            elif position[1] > HEIGHT - config.fringe: force[1] = - (position[1] - (HEIGHT - config.fringe)) / config.fringe * config.repulsion  #bottom
            accelerations[i] += force

        self.velocities[:] = self.velocities * config.friction + accelerations * config.dt  #v = u + at 
        self.positions[:] = self.positions + self.velocities * config.dt  #r = r0 + vt

    def draw(self):
        """Iterates through the particles and draws them as circles"""
        for i in range(N):
            x, y = self.positions[i]
            pygame.draw.aacircle(screen, colours[self.particles[i] % len(colours)], (x, y), config.radius)

    def draw_menu(self, mouse, scroll, size = 50, font = pygame.font.SysFont("Consolas", 15), colour = (255, 253, 219)):
        """Draws the menu to edit the value of attraction between any pair of particle type/colour"""
        text = font.render(f"FPS: {int(clock.get_fps())}", True, colour)  #FPS of the program
        screen.blit(text, (10, 10))

        n = len(colours)
        for i in range(n):
            for j in range(n):
                box = pygame.Rect(WIDTH / 2 - (n * size) / 2 + j * size, HEIGHT / 2 - (n * size) / 2 + i * size, size, size)
                pygame.draw.rect(screen, colour, box, 1)

                text = font.render(f"{round(self.attraction_matrix[i][j], 1)}", True, colour)  #the attraction factor
                rect = text.get_rect(center=box.center)  #centre text in the box
                screen.blit(text, rect)  #draws it in correct place

                if box.collidepoint(mouse[0], mouse[1]):  #if the cursor is hovering over a box
                    self.attraction_matrix[i][j] += scroll  #move the value up or down depending on scroll direction
                    self.attraction_matrix[i][j] = min(1, max(-1, self.attraction_matrix[i][j]))  #clamp the value between 0 and 1

                if i == 0:  #top row of circles
                    pygame.draw.aacircle(screen, colours[j], (box.left + size / 2, box.top - size / 2), config.radius * 2)
                    pygame.draw.aacircle(screen, colour, (box.left + size / 2, box.top - size / 2), config.radius * 2, 1)  #outline
                if j == 0:  #left row of circles
                    pygame.draw.aacircle(screen, colours[i], (box.left - size / 2, box.top + size / 2), config.radius * 2)
                    pygame.draw.aacircle(screen, colour, (box.left - size / 2, box.top + size / 2), config.radius * 2, 1)  #outline

        rect = pygame.Rect(WIDTH / 2 - (n * size) / 2, HEIGHT / 2 - (n * size) / 2 + n * size, size * n, size)  #box underneath matrix
        text = font.render("Random", True, colour)
        rect = text.get_rect(center=rect.center)  #centre text in the rectangle
        if rect.collidepoint(mouse[0], mouse[1]) and scroll: self.attraction_matrix = np.random.uniform(-1, 1, (len(colours), len(colours)))  #if scroll when hovering over this box, randomly sets the attraction values
        screen.blit(text, rect)

    def run(self):
        """Runs the main simulation loop; handling events, updates and rendering"""
        menu = False  #menu to change attraction values
        while 1:
            screen.fill(background)
            clock.tick(fps)
            scroll = 0  #value of scroll
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  #quit program if ESC key pressed
                    pygame.quit()
                    sys.exit() 
                if event.type == pygame.MOUSEBUTTONDOWN:  #if the mouse is pressed down
                    if event.button == 1: menu = not menu  #toggle menu
                if event.type == pygame.MOUSEWHEEL: scroll += event.y / 50  #amount to change attraction factor by

            self.update()  #update the system
            self.draw()  #draw the system

            if menu: self.draw_menu(pygame.mouse.get_pos(), scroll)  #menu to alter attraction matrix

            screen.blit(blur(screen), (0, 0), special_flags=pygame.BLEND_RGBA_ADD)  #draws the blurred screen to add a bloom effect
    
            pygame.display.update()