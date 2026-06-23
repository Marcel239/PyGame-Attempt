"""
q5_tint.py

Assignment: PyOpenGL 3D Models Project - Question 5
Builds on q1_display.py, q2_translate.py, q3_color.py, and q4_texture.py.

Description:
    Adds a fourth view mode, "Tinted", which combines Question 3's
    per-face colours with Question 4's per-face texturing: each face is
    drawn with the wood texture from Question 4, multiplied by that
    same face's colour from Question 3, so the texture is visibly tinted
    a different colour on every face while the wood grain is still
    visible underneath. The user can cycle through all four view modes
    with a single key. Switching view modes never affects object
    swapping, translation, rotation, scale, or orientation.

Comment markers used throughout this file:
    # Q1: ...  -> functionality carried over unchanged from Question 1
    # Q2: ...  -> functionality carried over unchanged from Question 2
    # Q3: ...  -> functionality carried over unchanged from Question 3
    # Q4: ...  -> functionality carried over unchanged from Question 4
    # Q5: ...  -> new functionality added for Question 5 (tinting)

Controls:
    SPACE                   -> cycle to the next model
    RIGHT ARROW / LEFT      -> translate the model along +X / -X
    UP ARROW / DOWN ARROW   -> translate the model along +Y / -Y
    E / Q                   -> translate the model along +Z / -Z
    V                       -> cycle view mode: Normal -> Coloured ->
                               Textured -> Tinted -> back to Normal
    ESC / closing window    -> quit the program
"""

import sys

import pygame
from pygame.locals import (
    DOUBLEBUF, OPENGL, QUIT, KEYDOWN,
    K_SPACE, K_ESCAPE,
    K_LEFT, K_RIGHT, K_UP, K_DOWN, K_q, K_e, K_v,
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
# and the colour assigned to each face. (Unchanged from Question 3.)

CUBE_FACES = (
    (3, 2, 1, 0),   # back   (z = -1)
    (4, 5, 7, 6),   # front  (z = +1)
    (0, 1, 5, 4),   # right  (x = +1)
    (6, 7, 2, 3),   # left   (x = -1)
    (4, 6, 3, 0),   # bottom (y = -1)
    (1, 2, 7, 5),   # top    (y = +1)
)

PYRAMID_FACES = (
    (0, 1, 2),      # base
    (1, 0, 3),      # side A
    (2, 1, 3),      # side B
    (0, 2, 3),      # side C
)

PRISM_FACES = (
    (0, 1, 2),      # front triangle (z = +1)
    (5, 4, 3),      # back triangle  (z = -1)
    (3, 4, 1, 0),   # bottom quad
    (4, 5, 2, 1),   # right slope quad
    (5, 3, 0, 2),   # left slope quad
)

FACE_COLORS = (
    (0.85, 0.20, 0.20),   # red
    (0.20, 0.70, 0.30),   # green
    (0.20, 0.40, 0.85),   # blue
    (0.90, 0.80, 0.20),   # yellow
    (0.75, 0.25, 0.80),   # magenta
    (0.20, 0.80, 0.80),   # cyan
)

# Q4: per-vertex (u, v) texture coordinates for a triangular or
# quad face (unchanged from Question 4).
TRIANGLE_UV = ((0.0, 0.0), (1.0, 0.0), (0.5, 1.0))
QUAD_UV = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))


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


# Q4: Texture loading (unchanged from Question 4)


def load_texture(filename="texture.png"):
    """Load an image file from disk and upload it as an OpenGL texture.
    Returns the texture ID, or None if loading fails."""
    try:
        surface = pygame.image.load(filename)
        surface = pygame.transform.flip(surface, False, True)
        texture_data = pygame.image.tostring(surface, "RGBA", 1)
        width, height = surface.get_size()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        return tex_id
    except Exception as exc:
        print(f"Q4: failed to load texture '{filename}': {exc}")
        print("Q4: make sure texture.png is in the same folder as this script.")
        return None

# Drawing


def draw_model(vertices, edges, centre, faces, view_mode, texture_id):
    """
    Draw the model in one of four view modes:
        0 = Normal    (wireframe only, as in Q1/Q2)
        1 = Coloured  (per-face solid colours, as in Q3)
        2 = Textured  (per-face image texture, as in Q4)
        3 = Tinted    (texture + per-face colour tint, new in Q5)
    In every mode, the white wireframe edges are always drawn on top so
    the model outline stays visible and white regardless of view mode.
    """
    cx, cy, cz = centre

    if view_mode == 1:
        # Q3: coloured surfaces
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
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

    elif view_mode in (2, 3) and texture_id is not None:
        # Q4 (mode 2) / Q5 (mode 3): textured, optionally tinted surfaces.
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)

        for i, face in enumerate(faces):
            if view_mode == 3:
                # Q5: set the face colour BEFORE drawing the textured
                # polygon. OpenGL's default texture environment
                # (GL_MODULATE) multiplies this colour with every texel
                # sampled from the texture, producing a tinted result -
                # e.g. a red tint (1, 0.2, 0.2) over the wood texture
                # darkens its green/blue channels and leaves a reddish,
                # textured face.
                glColor3fv(FACE_COLORS[i % len(FACE_COLORS)])
            else:
                # Q4: white -> texture is shown with its true colours,
                # i.e. no tint applied.
                glColor3f(1.0, 1.0, 1.0)

            uv_set = TRIANGLE_UV if len(face) == 3 else QUAD_UV
            glBegin(GL_POLYGON)
            for idx, (u, v) in zip(face, uv_set):
                x, y, z = vertices[idx]
                glTexCoord2f(u, v)
                glVertex3f(x - cx, y - cy, z - cz)
            glEnd()

        glDisable(GL_POLYGON_OFFSET_FILL)
        glDisable(GL_CULL_FACE)
        glDisable(GL_TEXTURE_2D)

    # Q1: white wireframe edges, always drawn on top in every view mode.
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    for edge in edges:
        for idx in edge:
            x, y, z = vertices[idx]
            glVertex3f(x - cx, y - cy, z - cz)
    glEnd()

    # Q1: vertices highlighted as points.
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
    pygame.display.set_caption("Q5 - Model Tinting (PyOpenGL)")

    glEnable(GL_DEPTH_TEST)

    # Q4: load the texture once, up front.
    texture_id = load_texture("texture.png")

    current_index = 0
    angle = 0.0
    offset_x, offset_y, offset_z = 0.0, 0.0, 0.0  # Q2

    # Q5: 0 = Normal, 1 = Coloured, 2 = Textured, 3 = Tinted
    view_mode = 0
    view_mode_names = ("Normal", "Coloured", "Textured", "Tinted")

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
                    # Q1: cycle model; translation offset (Q2) and view
                    # mode (Q5) are both untouched, so swapping models
                    # never breaks position or the current view mode.
                    current_index = (current_index + 1) % len(MODELS)
                if event.key == K_v:
                    # Q5: cycle Normal -> Coloured -> Textured -> Tinted
                    view_mode = (view_mode + 1) % 4

        # Q2: translation controls
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

        draw_model(vertices, edges, centre, faces, view_mode, texture_id)

        pygame.display.set_caption(
            f"Q5 - Model Tinting (PyOpenGL) - {name} | "
            f"offset=({offset_x:.1f}, {offset_y:.1f}, {offset_z:.1f}) | "
            f"View: {view_mode_names[view_mode]} (press V to cycle)"
        )

        angle += 0.5
        pygame.display.flip()


if __name__ == "__main__":
    main()
