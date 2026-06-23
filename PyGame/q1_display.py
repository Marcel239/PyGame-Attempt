"""
q1_display.py

Assignment: PyOpenGL 3D Models Project - Question 1
Topic: Creating the OpenGL window and displaying a basic model on screen.

Description:
    This program opens an OpenGL window (via pygame) and renders one of
    three wireframe models at a time: a cube, a pyramid, or a triangular
    prism. The currently displayed model is always centred on screen, and
    the camera distance is calculated automatically for each model so the
    camera is never placed inside the model. Pressing SPACE cycles
    forward through the models in a fixed order, wrapping back around to
    the first model after the last one has been shown.

Controls:
    SPACE                 -> show the next model (cycles back to the
                             start after the last model)
    ESC / closing window  -> quit the program

"""

import sys

import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_SPACE, K_ESCAPE
from OpenGL.GL import *
from OpenGL.GLU import *


# 1. Model data (exactly as provided in the assignment brief)

Cube_Vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1),
)

Cube_Edges = (
    (0, 1), (0, 3), (0, 4),
    (2, 1), (2, 3), (2, 7),
    (6, 3), (6, 4), (6, 7),
    (5, 1), (5, 4), (5, 7),
)

Pyramid_Vertices = (
    (1, -1, 1),
    (-1, -1, 1),
    (0, -1, -1),
    (1, 1, 0.5),
)

Pyramid_Edges = (
    (0, 1), (0, 2), (0, 3),
    (2, 1), (2, 3), (3, 1),
)

Prism_Vertices = (
    (-1, -1, 1),
    (1, -1, 1),
    (0, 1, 1),
    (-1, -1, -1),
    (1, -1, -1),
    (0, 1, -1),
)

Prism_Edges = (
    (0, 1), (0, 2), (1, 2),
    (3, 4), (3, 5), (4, 5),
    (0, 3), (1, 4), (2, 5),
)

# Fixed, ordered list of models so the cycling order never changes between

MODELS = (
    ("Cube", Cube_Vertices, Cube_Edges),
    ("Pyramid", Pyramid_Vertices, Pyramid_Edges),
    ("Prism", Prism_Vertices, Prism_Edges),
)


# 2. Helper functions

def get_centre_and_radius(vertices):
    """
    Compute the centroid (average position) of a model's vertices and the
    largest distance from that centroid to any single vertex.

    The centroid is used to re-centre the model on the origin so it always
    appears in the middle of the screen, no matter where its raw
    coordinates happen to sit. The radius is used to work out a safe camera
    distance so the camera never ends up inside the model.
    """
    n = len(vertices)
    cx = sum(v[0] for v in vertices) / n
    cy = sum(v[1] for v in vertices) / n
    cz = sum(v[2] for v in vertices) / n

    radius = 0.0
    for (x, y, z) in vertices:
        dist = ((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2) ** 0.5
        radius = max(radius, dist)

    return (cx, cy, cz), radius


def draw_model(vertices, edges, centre):
    cx, cy, cz = centre

    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex_index in edge:
            x, y, z = vertices[vertex_index]
            glVertex3f(x - cx, y - cy, z - cz)
    glEnd()

    glColor3f(1.0, 0.55, 0.0)
    glPointSize(7)
    glBegin(GL_POINTS)
    for (x, y, z) in vertices:
        glVertex3f(x - cx, y - cy, z - cz)
    glEnd()


# 3. Main program

def main():
    pygame.init()
    display_size = (800, 600)
    pygame.display.set_mode(display_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Q1 - Model Display (PyOpenGL)")

    glEnable(GL_DEPTH_TEST)

    current_index = 0
    angle = 0.0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_SPACE:
                    # Move to the next model, wrapping back to index 0
                    # (the first model) once the last model is reached.
                    # The MODELS tuple order is fixed, so the displayed
                    # order never changes.
                    current_index = (current_index + 1) % len(MODELS)

        name, vertices, edges = MODELS[current_index]
        centre, radius = get_centre_and_radius(vertices)

        # Camera distance is derived from this specific model's size, so
        # the camera always stays comfortably outside the model's
        # bounding sphere - i.e. it never ends up inside the model -
        # regardless of which of the three models is being shown.
        camera_distance = radius * 3.0 + 3.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display_size[0] / display_size[1]), 0.1, 200.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -camera_distance)
        glRotatef(angle, 0.3, 1.0, 0.2)  # slow auto-rotate to show all sides

        draw_model(vertices, edges, centre)

        pygame.display.set_caption(
            f"Q1 - Model Display (PyOpenGL) - {name}  "
            f"[SPACE = next model, ESC = quit]"
        )

        angle += 0.5
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
