"""
q2_translate.py

Assignment: PyOpenGL 3D Models Project - Question 2
Topic: Adding translation functionality to the models from Question 1.

Description:
    This program builds directly on q1_display.py. It still displays one
    of three wireframe models (cube, pyramid, prism) at a time, centred on
    screen with a camera that is never inside the model, and still allows
    cycling through the models with a key press. New for this question:
    the currently displayed model can now be translated along all three
    axes (X, Y, Z), in both the positive and negative direction, using six
    dedicated keys. If the model is cycled while it has been moved, the
    new model appears in the same translated position as the old one
    (the translation offset is not reset when cycling).

Comment markers used throughout this file:
    # Q1: ...  -> functionality carried over unchanged from Question 1
                  (window setup, model data, centring, camera distance,
                  cycling logic, drawing routine)
    # Q2: ...  -> new functionality added for Question 2

Controls:
    SPACE                  -> cycle to the next model (wraps back to the
                               first model after the last one)
    RIGHT ARROW / LEFT     -> translate the model along +X / -X
    UP ARROW / DOWN ARROW  -> translate the model along +Y / -Y
    E / Q                  -> translate the model along +Z / -Z
    ESC / closing window   -> quit the program

    Hold a translation key down to keep moving the model in that
    direction; release it to stop.
"""

import sys

import pygame
from pygame.locals import (
    DOUBLEBUF, OPENGL, QUIT, KEYDOWN,
    K_SPACE, K_ESCAPE,
    K_LEFT, K_RIGHT, K_UP, K_DOWN, K_q, K_e,
)
from OpenGL.GL import *
from OpenGL.GLU import *



# Q1: Model data (exactly as provided in the assignment brief, unchanged)

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

# Q1: fixed-order list of models, used for cycling.
MODELS = (
    ("Cube", Cube_Vertices, Cube_Edges),
    ("Pyramid", Pyramid_Vertices, Pyramid_Edges),
    ("Prism", Prism_Vertices, Prism_Edges),
)

# Q2: how fast the model moves (world units per second) while a
# translation key is held down.
TRANSLATE_SPEED = 1.5


# Q1: Helper functions (unchanged from Question 1)


def get_centre_and_radius(vertices):
    """Q1: Compute the centroid of a model's vertices and the largest
    distance from that centroid to any vertex (used for centring the
    model and for picking a safe camera distance)."""
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
    """Q1: Draw the wireframe model (edges as lines, vertices as points),
    shifted so the model's centroid sits at the origin."""
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



# Main program

def main():
    # Q1: window / OpenGL setup
    pygame.init()
    display_size = (800, 600)
    pygame.display.set_mode(display_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Q2 - Model Translation (PyOpenGL)")

    glEnable(GL_DEPTH_TEST)

    current_index = 0
    angle = 0.0

    # Q2: translation offset applied to the current model. This is

    offset_x, offset_y, offset_z = 0.0, 0.0, 0.0

    clock = pygame.time.Clock()

    while True:
        # Q2: time elapsed since the previous frame (seconds), used so
        # translation speed is consistent regardless of frame rate.
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_SPACE:
                    # Q1: cycle to the next model, wrapping back to the
                    # first model after the last one. Note that
                    # offset_x/offset_y/offset_z are NOT touched here,
                    # which is exactly what keeps the new model in the
                    # same position as the old one.
                    current_index = (current_index + 1) % len(MODELS)

        keys = pygame.key.get_pressed()

        if keys[K_RIGHT]:                       # Q2: +X (right)
            offset_x += TRANSLATE_SPEED * dt
        if keys[K_LEFT]:                        # Q2: -X (left)
            offset_x -= TRANSLATE_SPEED * dt

        if keys[K_UP]:                          # Q2: +Y (up)
            offset_y += TRANSLATE_SPEED * dt
        if keys[K_DOWN]:                        # Q2: -Y (down)
            offset_y -= TRANSLATE_SPEED * dt

        if keys[K_e]:                           # Q2: +Z (towards viewer)
            offset_z += TRANSLATE_SPEED * dt
        if keys[K_q]:                           # Q2: -Z (away from viewer)
            offset_z -= TRANSLATE_SPEED * dt

        # Q1: look up the currently selected model and its centring data
        name, vertices, edges = MODELS[current_index]
        centre, radius = get_centre_and_radius(vertices)

        # Q1: camera distance recalculated per model so the camera is
        # always safely outside the model's bounding sphere.
        camera_distance = radius * 3.0 + 3.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display_size[0] / display_size[1]), 0.1, 200.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Q2: apply the translation offset together with the fixed
        # camera pull-back distance in a single glTranslatef call.

        glTranslatef(offset_x, offset_y, offset_z - camera_distance)

        # Q1: rotate the model around its own centre so all faces are
        # visible over time.
        glRotatef(angle, 0.3, 1.0, 0.2)

        draw_model(vertices, edges, centre)

        pygame.display.set_caption(
            f"Q2 - Model Translation (PyOpenGL) - {name}  "
            f"offset=({offset_x:.1f}, {offset_y:.1f}, {offset_z:.1f})"
        )

        angle += 0.5
        pygame.display.flip()


if __name__ == "__main__":
    main()
