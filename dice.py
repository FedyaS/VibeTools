import pygame
from pygame.locals import *
from math import cos, sin, pi, sqrt
import random

class Die:
    def __init__(self, cube_size, position=(0, 0, 0)):
        self.cube_size = cube_size
        self.position = list(position)  # [x, y, z] y is height
        self.velocity = [0, 0, 0]
        self.angular_velocity = [0, 0, 0]
        self.rx = random.uniform(0, 2*pi)
        self.ry = random.uniform(0, 2*pi)
        self.rz = random.uniform(0, 2*pi)
        self.dragging = False
        self.stopped = False

        # Original vertices
        s = cube_size
        self.vertices = [
            (-s, -s, -s),
            (s, -s, -s),
            (s, s, -s),
            (-s, s, -s),
            (-s, -s, s),
            (s, -s, s),
            (s, s, s),
            (-s, s, s)
        ]

        # Faces
        self.faces = [
            [0, 1, 2, 3],  # front z-
            [1, 5, 6, 2],  # right x+
            [5, 4, 7, 6],  # back z+
            [4, 0, 3, 7],  # left x-
            [3, 2, 6, 7],  # top y+
            [4, 5, 1, 0]   # bottom y-
        ]

        # Face numbers
        self.face_numbers = [2, 4, 5, 3, 1, 6]  # front, right, back, left, top, bottom

        # Original normals
        self.face_normals = [
            (0, 0, -1),
            (1, 0, 0),
            (0, 0, 1),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0)
        ]

        # Dot positions for 1 to 6
        self.dot_positions = [
            [(0.5, 0.5)],  # 1
            [(0.25, 0.25), (0.75, 0.75)],  # 2
            [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],  # 3
            [(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)],  # 4
            [(0.25, 0.25), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (0.75, 0.75)],  # 5
            [(0.25, 0.25), (0.25, 0.5), (0.25, 0.75), (0.75, 0.25), (0.75, 0.5), (0.75, 0.75)]  # 6
        ]

    def rotate3d(self, point, rx, ry, rz):
        x, y, z = point
        # Rotate around x
        c = cos(rx)
        s = sin(rx)
        y1 = y * c - z * s
        z1 = y * s + z * c
        # Rotate around y
        c = cos(ry)
        s = sin(ry)
        x2 = x * c + z1 * s
        z2 = -x * s + z1 * c
        # Rotate around z
        c = cos(rz)
        s = sin(rz)
        x3 = x2 * c - y1 * s
        y3 = x2 * s + y1 * c
        return x3, y3, z2

    def get_rotated_normal(self, normal, rx, ry, rz):
        return self.rotate3d(normal, rx, ry, rz)

    def update(self, dt, bounds):
        if self.dragging:
            return

        # Gravity and velocity
        self.velocity[1] -= 9.81 * dt * 10  # Scaled gravity

        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt

        self.rx += self.angular_velocity[0] * dt
        self.ry += self.angular_velocity[1] * dt
        self.rz += self.angular_velocity[2] * dt

        # Bounce on floor
        if self.position[1] <= self.cube_size:
            self.position[1] = self.cube_size
            self.velocity[1] = -self.velocity[1] * 0.7
            self.velocity[0] *= 0.95
            self.velocity[2] *= 0.95
            self.angular_velocity = [random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)]

        # Friction if on floor
        if self.position[1] == self.cube_size:
            self.velocity[0] *= 0.98
            self.velocity[2] *= 0.98
            self.angular_velocity = [a * 0.98 for a in self.angular_velocity]

        # Wall bounces
        if abs(self.position[0]) > bounds[0] - self.cube_size:
            self.velocity[0] = -self.velocity[0] * 0.8
            self.position[0] = (bounds[0] - self.cube_size) * (1 if self.position[0] > 0 else -1)
        if abs(self.position[2]) > bounds[1] - self.cube_size:
            self.velocity[2] = -self.velocity[2] * 0.8
            self.position[2] = (bounds[1] - self.cube_size) * (1 if self.position[2] > 0 else -1)

        # Check if stopped
        speed = sum(v**2 for v in self.velocity) ** 0.5
        ang_speed = sum(a**2 for a in self.angular_velocity) ** 0.5
        if speed < 0.1 and ang_speed < 0.1 and self.position[1] == self.cube_size:
            self.velocity = [0, 0, 0]
            self.angular_velocity = [0, 0, 0]
            self.stopped = True

    def get_projected_bounds(self, rotated_vertices, center_x, center_y, f):
        proj_vertices = []
        for rx, ry, rz in rotated_vertices:
            scale = f / (f + rz)
            x_proj = center_x + rx * scale
            y_proj = center_y - ry * scale  # Flip y
            proj_vertices.append((x_proj, y_proj))
        min_x = min(p[0] for p in proj_vertices)
        max_x = max(p[0] for p in proj_vertices)
        min_y = min(p[1] for p in proj_vertices)
        max_y = max(p[1] for p in proj_vertices)
        return min_x, min_y, max_x, max_y

    def draw(self, screen, center_x, center_y, f):
        # Rotate vertices
        rotated_vertices = []
        for v in self.vertices:
            rv = self.rotate3d(v, self.rx, self.ry, self.rz)
            rv = (rv[0] + self.position[0], rv[1] + self.position[1], rv[2] + self.position[2])
            rotated_vertices.append(rv)

        # Draw faces
        for i, face in enumerate(self.faces):
            v1 = rotated_vertices[face[0]]
            v2 = rotated_vertices[face[1]]
            v3 = rotated_vertices[face[2]]
            normal = self.get_rotated_normal(self.face_normals[i], self.rx, self.ry, self.rz)
            if normal[2] > 0:  # Simple backface culling
                proj_points = []
                for vi in face:
                    rx, ry, rz = rotated_vertices[vi]
                    scale = f / (f + rz)
                    x_proj = center_x + rx * scale
                    y_proj = center_y - ry * scale  # Flip y for positive up
                    proj_points.append((x_proj, y_proj))
                pygame.draw.polygon(screen, (255, 255, 255), proj_points)

                # Draw dots
                num = self.face_numbers[i]
                dots = self.dot_positions[num - 1]
                # Get basis for face
                pa = self.vertices[face[0]]
                pb = self.vertices[face[1]]
                pd = self.vertices[face[3]]
                u_vec = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2])
                v_vec = (pd[0] - pa[0], pd[1] - pa[1], pd[2] - pa[2])
                for u, v in dots:
                    local = (pa[0] + u * u_vec[0] + v * v_vec[0],
                             pa[1] + u * u_vec[1] + v * v_vec[1],
                             pa[2] + u * u_vec[2] + v * v_vec[2])
                    rdot = self.rotate3d(local, self.rx, self.ry, self.rz)
                    rdot = (rdot[0] + self.position[0], rdot[1] + self.position[1], rdot[2] + self.position[2])
                    scale = f / (f + rdot[2])
                    x_proj = center_x + rdot[0] * scale
                    y_proj = center_y - rdot[1] * scale
                    dot_radius = 0.1 * self.cube_size * scale
                    pygame.draw.circle(screen, (0, 0, 0), (x_proj, y_proj), dot_radius)

    def get_top_face(self):
        max_y = -float('inf')
        top_num = 0
        for i in range(6):
            rn = self.get_rotated_normal(self.face_normals[i], self.rx, self.ry, self.rz)
            if rn[1] > max_y:
                max_y = rn[1]
                top_num = self.face_numbers[i]
        return top_num


def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("3D Dice Simulator")
    clock = pygame.time.Clock()
    f = 400  # Focal length
    center_x = width // 2
    center_y = height // 2
    bounds = (300, 300)  # x,z bounds

    dice = [
        Die(50, (-100, 50, 0)),
        Die(50, (0, 50, 0)),
        Die(50, (100, 50, 0))
    ]

    dragging_die = None
    mouse_prev = None

    font = pygame.font.SysFont(None, 50)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                for die in dice[::-1]:  # Check from front
                    rotated_vertices = [die.rotate3d(v, die.rx, die.ry, die.rz) for v in die.vertices]
                    rotated_vertices = [(rv[0] + die.position[0], rv[1] + die.position[1], rv[2] + die.position[2]) for rv in rotated_vertices]
                    min_x, min_y, max_x, max_y = die.get_projected_bounds(rotated_vertices, center_x, center_y, f)
                    if min_x < mouse[0] < max_x and min_y < mouse[1] < max_y:
                        dragging_die = die
                        die.dragging = True
                        die.stopped = False
                        die.velocity = [0, 0, 0]
                        die.angular_velocity = [0, 0, 0]
                        mouse_prev = mouse
                        break
            if event.type == MOUSEBUTTONUP:
                if dragging_die:
                    mouse_curr = pygame.mouse.get_pos()
                    dx = (mouse_curr[0] - mouse_prev[0]) / dt
                    dy = (mouse_curr[1] - mouse_prev[1]) / dt
                    dragging_die.velocity = [dx * 0.01, 20, dy * 0.01]  # Throw with upward velocity
                    dragging_die.angular_velocity = [random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)]
                    dragging_die.dragging = False
                    dragging_die = None

        if dragging_die:
            mouse = pygame.mouse.get_pos()
            dx = mouse[0] - center_x
            dz = mouse[1] - center_y
            dragging_die.position = [dx, dragging_die.cube_size + 100, dz]
            # Optional rotation during drag
            dragging_die.rx += (mouse[0] - mouse_prev[0]) * 0.01
            dragging_die.ry += (mouse[1] - mouse_prev[1]) * 0.01
            mouse_prev = mouse

        for die in dice:
            die.update(dt, bounds)
            die.draw(screen, center_x, center_y, f)
            if die.stopped:
                result = die.get_top_face()
                text = font.render(str(result), True, (255, 0, 0))
                # Draw near the die, but for simplicity, draw at bottom
                screen.blit(text, (center_x + die.position[0] - 20, height - 50))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()