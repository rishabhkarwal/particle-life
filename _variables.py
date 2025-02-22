import pygame
pygame.init()

clock = pygame.time.Clock()
fps = 30
background = (2, 2, 15) #background colour

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.NOFRAME)
"""
Example colour schemes
colours = [(255, 229, 173), (62, 0, 31), (152, 33, 118), (241, 26, 123)] #https://colorhunt.co/palette/f11a7b9821763e001fffe5ad
colours = [(226, 62, 87), (136, 48, 78), (82, 37, 70), (49, 29, 63)] #https://colorhunt.co/palette/e23e5788304e522546311d3f
colours = [(54, 79, 107), (63, 193, 201), (245, 245, 245), (252, 81, 133)] #https://colorhunt.co/palette/364f6b3fc1c9f5f5f5fc5185
colours = [(125, 90, 80), (180, 132, 108), (229, 178, 153), (252, 222, 192)] #https://colorhunt.co/palette/7d5a50b4846ce5b299fcdec0
colours = [(39, 55, 77), (82, 109, 130), (157, 178, 191), (221, 230, 237)] #https://colorhunt.co/palette/27374d526d829db2bfdde6ed
"""
colours = [(39, 55, 77), (82, 109, 130), (157, 178, 191), (221, 230, 237)] #https://colorhunt.co/palette/27374d526d829db2bfdde6ed

from dataclasses import dataclass
@dataclass(frozen=True)
class _:
    count: int = 200 #number of particles
    radius: int = 4 #radius of particle

    dt: float = 0.05 #the time step of the simulation

    damping: float = 1 #time for velocity to half due to friction

    influence: float = 100 #radius of influence for attractive/repulsive forces

    repulsion: float = 100 #magnitude of repulsion force - to keep particles within simulation space in an organic manner
    fringe: float = 50 #distance from the edge before the repulsion force pushes particles back in

    @property
    def friction(self) -> float:
        return 0.5 ** (self.dt / self.damping)

config = _()


