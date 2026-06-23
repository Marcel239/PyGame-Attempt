"""
q3_color.py

Assignment: PyOpenGL 3D Models Project - Question 3
Builds on q1_display.py and q2_translate.py.

Description:
    Adds a colouring feature on top of Questions 1 and 2. Each surface
    (face) of the currently displayed model is filled with a different
    solid colour, while the model's edges remain white and are drawn on
    top of the coloured faces. The feature can be switched on and off
    with a key press, and does not affect the model's position,
    orientation, or scale.

Comment markers used throughout this file:
    # Q1: ...  -> functionality carried over unchanged from Question 1
                  (window setup, centring, camera distance, cycling)
    # Q2: ...  -> functionality carried over unchanged from Question 2
                  (translation controls)
    # Q3: ...  -> new functionality added for Question 3 (face colouring)

Controls:
    SPACE                   -> cycle to the next model
    RIGHT ARROW / LEFT      -> translate the model along +X / -X
    UP ARROW / DOWN ARROW   -> translate the model along +Y / -Y
    E / Q                   -> translate the model along +Z / -Z
    C                       -> toggle coloured surfaces on/off
    ESC / closing window    -> quit the program
"""

import sys

import pygame
from pygame.locals import (
    DOUBLEBUF, OPENGL, QUIT, KEYDOWN,
    K_SPACE, K_ESCAPE,
    K_LEFT, K_RIGHT, K_UP, K_DOWN, K_q, K_e, K_c,
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

# Q2: translation speed (world units per second).
TRANSLATE_SPEED = 1.5


# Q3: Face definitions (vertex indices per face, outward-winding verified)
# and the colour assigned to each face.


# Cube: 6 quad faces.
CUBE_FACES = (
    (3, 2, 1, 0),   # back   (z = -1)
    (4, 5, 7, 6),   # front  (z = +1)
    (0, 1, 5, 4),   # right  (x = +1)
    (6, 7, 2, 3),   # left   (x = -1)
    (4, 6, 3, 0),   # bottom (y = -1)
    (1, 2, 7, 5),   # top    (y = +1)
)

# Pyramid: 1 quad-ish base (triangle here, since only 3 base vertices are
# given in the brief) + 3 triangular sides.
PYRAMID_FACES = (
    (0, 1, 2),      # base
    (1, 0, 3),      # side A
    (2, 1, 3),      # side B
    (0, 2, 3),      # side C
)

# Prism: 2 triangular ends + 3 rectangular sides.
PRISM_FACES = (
    (0, 1, 2),      # front triangle (z = +1)
    (5, 4, 3),      # back triangle  (z = -1)
    (3, 4, 1, 0),   # bottom quad
    (4, 5, 2, 1),   # right slope quad
    (5, 3, 0, 2),   # left slope quad
)

# Q3: one distinct, fully opaque colour per face. Re-used (cycled) if a
# model ever has more faces than colours listed here.
FACE_COLORS = (
    (0.85, 0.20, 0.20),   # red
    (0.20, 0.70, 0.30),   # green
    (0.20, 0.40, 0.85),   # blue
    (0.90, 0.80, 0.20),   # yellow
    (0.75, 0.25, 0.80),   # magenta
    (0.20, 0.80, 0.80),   # cyan
)


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


def get_faces_for(name):
    """Q3: Return the correct face list for the given model name."""
    if name == "Cube":
        return CUBE_FACES
    if name == "Pyramid":
        return PYRAMID_FACES
    return PRISM_FACES


def draw_model(vertices, edges, centre, faces, show_color):
    """
    Draw the model. If show_color is True, each face listed in `faces`
    is first filled in with its assigned colour (Q3); the white wireframe
    edges (Q1) are always drawn on top afterwards, so edges stay visible
    and white regardless of the colouring toggle.
    """
    cx, cy, cz = centre

    if show_color:
        # Back-face culling discards the inside of each face so that,
        # combined with the verified outward winding above, every
        # surface is opaque and the inside of the model is never
        # visible through it.
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # A small polygon offset stops the white edge lines (drawn right
        # after, at the same depth) from visually flickering/z-fighting
        # against the coloured faces.
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)

        for i, face in enumerate(faces):
            glColor3fv(FACE_COLORS[i % len(FACE_COLORS)])
            glBegin(GL_POLYGON)
            for idx in face:
                x, y, z = vertices[idx]
                glVertex3f(x - cx, y - cy, z - cz)
            glEnd()

        glDisable(GL_POLYGON_OFFSET_FILL)
        glDisable(GL_CULL_FACE)

    # Q1: --- white wireframe edges, always drawn ---
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    for edge in edges:
        for idx in edge:
            x, y, z = vertices[idx]
            glVertex3f(x - cx, y - cy, z - cz)
    glEnd()

    # Q1: vertices highlighted as points, so missing points are obvious.
    glColor3f(1.0, 0.55, 0.0)
    glPointSize(6)
    glBegin(GL_POINTS)
    for x, y, z in vertices:
        glVertex3f(x - cx, y - cy, z - cz)
    glEnd()


# Main program


def main():
    # Q1: window / OpenGL setup
    pygame.init()
    display_size = (800, 600)
    pygame.display.set_mode(display_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Q3 - Model Colouring (PyOpenGL)")

    glEnable(GL_DEPTH_TEST)

    current_index = 0
    angle = 0.0
    offset_x, offset_y, offset_z = 0.0, 0.0, 0.0  # Q2
    show_color = True  # Q3: colouring starts switched on

    clock = pygame.time.Clock()

    while True:
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
                    # Q1: cycle model; translation offset is untouched so
                    # the new model keeps the same position (Q2).
                    current_index = (current_index + 1) % len(MODELS)
                if event.key == K_c:
                    # Q3: toggle coloured surfaces on/off.
                    show_color = not show_color

        # Q2: translation controls (held keys move the model smoothly)
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            offset_x += TRANSLATE_SPEED * dt
        if keys[K_LEFT]:
            offset_x -= TRANSLATE_SPEED * dt
        if keys[K_UP]:
            offset_y += TRANSLATE_SPEED * dt
        if keys[K_DOWN]:
            offset_y -= TRANSLATE_SPEED * dt
        if keys[K_e]:
            offset_z += TRANSLATE_SPEED * dt
        if keys[K_q]:
            offset_z -= TRANSLATE_SPEED * dt

        # Q1: look up the currently selected model
        name, vertices, edges = MODELS[current_index]
        centre, radius = get_centre_and_radius(vertices)
        camera_distance = radius * 3.0 + 3.0

        faces = get_faces_for(name)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display_size[0] / display_size[1]), 0.1, 200.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(offset_x, offset_y, offset_z - camera_distance)  # Q2
        glRotatef(angle, 0.3, 1.0, 0.2)  # Q1

        draw_model(vertices, edges, centre, faces, show_color)

        pygame.display.set_caption(
            f"Q3 - Model Colouring (PyOpenGL) - {name} | "
            f"offset=({offset_x:.1f}, {offset_y:.1f}, {offset_z:.1f}) | "
            f"Colour: {'ON' if show_color else 'OFF'} (press C to toggle)"
        )

        angle += 0.5
        pygame.display.flip()


if __name__ == "__main__":
    main()
