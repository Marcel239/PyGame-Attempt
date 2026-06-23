# PyOpenGL 3D Models Project - README

## What this is

Five Python programs that progressively build on each other to display
and manipulate 3D models (a cube, a pyramid, and a triangular prism)
using PyOpenGL. Each file corresponds to one question in the assignment
brief and can be run completely independently.

| File              | Question | What it adds                                   |
|-------------------|----------|-------------------------------------------------|
| `q1_display.py`   | Q1       | Display + cycle through the 3 models            |
| `q2_translate.py` | Q2       | Q1 + move the model on all 3 axes                |
| `q3_color.py`     | Q3       | Q1+Q2 + per-face colouring, toggle on/off         |
| `q4_texture.py`   | Q4       | Q1+Q2+Q3 + per-face image texturing               |
| `q5_tint.py`      | Q5       | Q1+Q2+Q3+Q4 + tinted (coloured + textured) faces  |

Each later file is self-contained (it does not import an earlier file) -
it includes everything from the earlier questions plus that question's
new feature, so any single file can be marked on its own. Comments in
each file are tagged `# Q1:`, `# Q2:`, etc. to show which question each
block of code belongs to.

## Requirements

- Python 3.8+
- `pygame`
- `PyOpenGL`

Install with:

```
pip install pygame PyOpenGL
```

## How to run

Make sure `texture.png` is in the **same folder** as the script you are
running (it is required from `q4_texture.py` onwards; `q1_display.py`
and `q2_translate.py` don't use it). Then run any file directly, e.g.:

```
python q1_display.py
python q2_translate.py
python q3_color.py
python q4_texture.py
python q5_tint.py
```

A window will open showing the current model. Close the window or press
ESC at any time to quit.

## Controls

These controls accumulate as you move through the questions - e.g.
`q5_tint.py` supports every control listed below.

| Key                  | Action                                            | Added in |
|-----------------------|----------------------------------------------------|----------|
| SPACE                 | Cycle to the next model (Cube -> Pyramid -> Prism -> Cube -> ...) | Q1 |
| RIGHT ARROW / LEFT    | Translate the model along +X / -X                 | Q2 |
| UP ARROW / DOWN ARROW | Translate the model along +Y / -Y                 | Q2 |
| E / Q                 | Translate the model along +Z / -Z                 | Q2 |
| C                     | Toggle coloured faces on/off                      | Q3 (only in `q3_color.py`) |
| V                     | Cycle view mode (see below)                       | Q4 / Q5 |
| ESC / close window    | Quit the program                                  | Q1 |

Translation keys can be held down to keep moving smoothly in that
direction; the model keeps rotating slowly on its own the whole time so
all sides remain visible.

### View mode key (`V`)

- In `q3_color.py`, press **C** to toggle colouring on/off (this file
  only has two states: Normal and Coloured).
- In `q4_texture.py`, press **V** to cycle through three view modes:
  **Normal -> Coloured -> Textured -> back to Normal**.
- In `q5_tint.py`, press **V** to cycle through four view modes:
  **Normal -> Coloured -> Textured -> Tinted -> back to Normal**.

The window's title bar always shows the current model name, the current
translation offset, and (from Q3 onwards) the current view mode, so you
can see the current state at a glance while testing.

## Notes for the marker

- All three models are always re-centred on the origin and the camera
  distance is calculated from each model's own size, so the camera is
  never inside the model and every model appears centred on screen,
  regardless of which model is currently selected.
- The model cycling order is always fixed (Cube -> Pyramid -> Prism) and
  wraps back to the Cube after the Prism.
- Translation is independent of the model's auto-rotation and of which
  model is currently selected - the translation offset persists when
  cycling models, so a model that has been moved away from the centre
  stays in that same screen position when you cycle to the next model.
- From `q3_color.py` onwards, every face of every model is given its own
  solid colour, the faces are fully opaque (back-face culling is used so
  you can never see through to the inside of the model), and the white
  wireframe edges are always drawn on top of the coloured/textured
  faces so they stay visible.
- `q4_texture.py` and `q5_tint.py` both require `texture.png` to be
  present in the same folder. If it cannot be found, the program will
  still run (Normal and Coloured modes will work as normal) but
  Textured/Tinted mode will simply have no effect, and a message will
  be printed to the console explaining why.
- `texture.png` is a simple wood-grain image used as the texture for
  every face of every model.



