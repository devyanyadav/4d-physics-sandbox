import numpy as np
import pygame
from tesseract import Tesseract
from functions import *
from rotation import *
from camera import Camera
from physics import rk4_step, DT

pygame.init()

# ---------- settings ----------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
FPS = 60
PIXELS_PER_UNIT = 100  # projected unit coordinates -> screen pixels

# Simulated seconds per real second (1.0 = real time, 0.1 = 10x slower).
# Only scales the time fed to the accumulator; the integrator step DT is unchanged.
# Changed only by the [ and ] keys, clamped to the range below.
time_scale = 0.1
TIME_SCALE_MIN = 0.05
TIME_SCALE_MAX = 8.0
paused = False  # toggled only by space
# Safety cap on physics steps per frame. If a slow frame needs more, the backlog is dropped.
MAX_STEPS_PER_FRAME = 10

# Diagnostic: once per real second print min separation, max speed, and whether positions are finite.
# Set to False (or delete the DEBUG blocks) when you no longer need it.
DEBUG = True

# Fixed eye-to-glass distances for the projection (NOT the camera's position)
Z_DIST = 20
W_DIST = 20
MAX_SCALE = 4                          # largest per-axis zoom allowed before an object is culled
NEAR_CLIP_MARGIN = Z_DIST / MAX_SCALE  # object is culled when (Z_DIST - z) or (W_DIST - w) drops below this

MOVE_SPEED = 3             # world units per second
KEY_ROT_SPEED = 1.5        # radians per second
MOUSE_SENSITIVITY = 0.001  # radians per pixel of mouse movement
OBJECT_SPIN = 0            # fixed rotation angle applied to every object each frame (does not accumulate); 0 = off
#the lower ends and higher ends of wall per axis
WALL_LO = 0
WALL_HI = 10
MAX_HI = 15 #the higher_end of wall can't grow past this


# ---------- setup ----------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)  # pygame's default font, used for the on-screen sim time
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)  # keep the cursor inside the window for mouse look

# ---------- scene ----------
tesseracts = [Tesseract(1, 2, 3, 1), Tesseract(6, 4, 3, 6),Tesseract(5,1,6,2)]
masses = np.array([5.0, 10.5,30.0])
charges = np.array([1.0, 1.0,-1.0])

# Starting state. Constants: never modified, reset copies from them.
INITIAL_POSITIONS = np.array([t.position for t in tesseracts], dtype=float)
INITIAL_VELOCITIES = np.array([[-1.0, 1.0, 0.0, 4.0],
                               [0.0, -1.0, 0.0, 0.0],
                               [1.2,3.0,1.0,4.2]])

# Live physics state, written only by the physics step (and reset). The view loop only reads positions.
positions = INITIAL_POSITIONS.copy()
velocities = INITIAL_VELOCITIES.copy()

# Fixed per-object geometry: vertex offsets from the object's centre, and the edges between them.
tesseracts_model_vertices = [np.asarray(t.vertices) for t in tesseracts]
half_sides = np.array([half_side(v) for v in tesseracts_model_vertices])
tesseracts_edges = [edge_list(t.vertices) for t in tesseracts]

# ---------- camera ----------
camera = Camera()
# Spawn pose, kept as constants for reset (np.array makes a copy, so later movement can't change them)
INITIAL_CAMERA_POSITION = np.array(camera.position, dtype=float)
INITIAL_CAMERA_ORIENTATION = np.array(camera.orientation, dtype=float)
camera_position = camera.position
camera_orientation = camera.orientation

# ---------- main loop ----------
running = True
accumulator = 0.0  # simulated seconds the physics still owes
sim_time = 0.0     # simulated seconds since the last reset
wall_on = True
lo = WALL_LO
hi = WALL_HI
message_text = ""
message_expires = 0
debug_timer = 0.0  # real seconds since the last diagnostic print
while running:
    frame_time = clock.tick(FPS) / 1000  # real seconds since the previous frame
    # While paused nothing is owed, so unpausing doesn't cause a burst of catch-up steps.
    if not paused:
        accumulator += frame_time * time_scale

    # ---------- events ----------
    mouse_dx = 0
    mouse_dy = 0
    step_once = False  # set by N while paused: run exactly one DT step this frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False  # cursor is locked, so esc is the way out
        if event.type == pygame.MOUSEMOTION:
            # event.rel instead of get_rel(), which gives (0, 0) on my trackpad
            mouse_dx += event.rel[0]
            mouse_dy += event.rel[1]
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # reset: scene, simulation clock and camera back to their starting state
            positions = INITIAL_POSITIONS.copy()
            velocities = INITIAL_VELOCITIES.copy()
            accumulator = 0.0
            sim_time = 0.0
            paused = False  # speed (time_scale) is kept
            camera.position = INITIAL_CAMERA_POSITION.copy()
            camera.orientation = INITIAL_CAMERA_ORIENTATION.copy()
            camera_position = camera.position        # re-read: this loop holds its own references
            camera_orientation = camera.orientation
            #resets the wall
            lo = WALL_LO
            hi = WALL_HI
            wall_on = True
            #resets any message
            message_text = ""
            message_expires = 0
        # sim speed and pause: KEYDOWN, so one press does one thing (get_pressed fires every frame)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_LEFTBRACKET:
                time_scale = max(TIME_SCALE_MIN, time_scale / 2)
            elif event.key == pygame.K_RIGHTBRACKET:
                time_scale = min(TIME_SCALE_MAX, time_scale * 2)
            elif event.key == pygame.K_n and paused:
                accumulator += DT  # owe exactly one step
                step_once = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                if wall_on:
                    wall_on = False
                elif can_resize(positions, half_sides, lo, hi):
                    wall_on = True
                else:
                    message_text = "can't turn walls on: object outside box"
                    message_expires = pygame.time.get_ticks() + 1500
            else:
                new_lo, new_hi = lo, hi
                if event.key == pygame.K_z:   # lo down (box grows)
                    new_lo = lo - 1
                elif event.key == pygame.K_x: # lo up (box shrinks)
                    new_lo = lo + 1
                elif event.key == pygame.K_c: # hi down (box shrinks)
                    new_hi = hi - 1
                elif event.key == pygame.K_v: # hi up (box grows)
                    new_hi = hi + 1

                if (new_lo, new_hi) != (lo, hi):
                    shrinking = new_lo > lo or new_hi < hi
                    if new_hi > MAX_HI:
                        message_text = "box can't grow past the cull range"
                        message_expires = pygame.time.get_ticks() + 1500
                    elif shrinking and not can_resize(positions, half_sides, new_lo, new_hi):
                        message_text = "box can't shrink: object in the way"
                        message_expires = pygame.time.get_ticks() + 1500
                    else:
                        lo, hi = new_lo, new_hi
    # ---------- camera input ----------
    # Mouse motion is summed over the frame and applied as one xz and one yz rotation.
    # Rotations don't commute, so applying many small ones per event gave an inconsistent order.
    if mouse_dx or mouse_dy:
        camera_orientation = camera.direction_xz(mouse_dx * MOUSE_SENSITIVITY)
        camera_orientation = camera.direction_yz(mouse_dy * MOUSE_SENSITIVITY)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_k]:
        # k held: movement keys rotate the camera in the w planes instead of moving it
        if keys[pygame.K_d]:
            camera_orientation = camera.direction_xw(KEY_ROT_SPEED * frame_time)
        if keys[pygame.K_a]:
            camera_orientation = camera.direction_xw(-KEY_ROT_SPEED * frame_time)
        if keys[pygame.K_e]:
            camera_orientation = camera.direction_yw(KEY_ROT_SPEED * frame_time)
        if keys[pygame.K_q]:
            camera_orientation = camera.direction_yw(-KEY_ROT_SPEED * frame_time)
        if keys[pygame.K_w]:
            camera_orientation = camera.direction_zw(KEY_ROT_SPEED * frame_time)
        if keys[pygame.K_s]:
            camera_orientation = camera.direction_zw(-KEY_ROT_SPEED * frame_time)
    else:
        # movement follows the camera's own axes, not the world's
        if keys[pygame.K_d]:
            camera_position = camera.travel_x(MOVE_SPEED * frame_time)
        if keys[pygame.K_a]:
            camera_position = camera.travel_x(-MOVE_SPEED * frame_time)
        if keys[pygame.K_w]:
            camera_position = camera.travel_z(MOVE_SPEED * frame_time)
        if keys[pygame.K_s]:
            camera_position = camera.travel_z(-MOVE_SPEED * frame_time)
        if keys[pygame.K_e]:
            camera_position = camera.travel_y(MOVE_SPEED * frame_time)
        if keys[pygame.K_q]:
            camera_position = camera.travel_y(-MOVE_SPEED * frame_time)

    # ---------- physics ----------
    # Spend the owed time in fixed steps of DT (0 or more per frame), all objects together.
    # Runs when not paused, or when paused with a single step requested (N).
    steps = 0
    frame_hits = []
    if not paused or step_once:
        while accumulator >= DT and steps < MAX_STEPS_PER_FRAME:
            positions, velocities = rk4_step(positions, velocities, masses, DT, charges)
            if wall_on:
                positions,velocities,hits = apply_walls(positions,velocities,half_sides,lo,hi)
                frame_hits.extend(hits)
            accumulator -= DT
            sim_time += DT
            steps += 1
        if accumulator >= DT:
            accumulator = 0.0  # stopped by the step cap, not by running out of owed time: drop the backlog

    if frame_hits:
        parts = []
        for i, a, side in frame_hits:
            parts.append(f"obj {i+1} {'+' if side > 0 else '-'}{'xyzw'[a]}")
        message_text = "hit: " + ", ".join(parts)
        message_expires = pygame.time.get_ticks() + 1500

    # ---------- diagnostic ----------
    if DEBUG:
        debug_timer += frame_time
        if debug_timer >= 1.0:
            debug_timer = 0.0
            separations = np.sqrt(((positions[:, None, :] - positions[None, :, :]) ** 2).sum(axis=-1))
            np.fill_diagonal(separations, np.inf)  # ignore each object's distance to itself
            print(f"sim {sim_time:.1f}s  min sep {separations.min():.2f}  "
                  f"max |v| {np.abs(velocities).max():.2f}  finite {np.isfinite(positions).all()}")

    # ---------- view transform ----------
    # positions and the model vertices are the permanent copies.
    # Everything computed here is rebuilt every frame and never written back.
    projected_tesseracts = []
    for i, model_vertices in enumerate(tesseracts_model_vertices):
        world_position = positions[i]
        spun_vertices = double_rotation(rotate_yz, rotate_zw, OBJECT_SPIN, OBJECT_SPIN, model_vertices)

        # translation only: object position relative to the camera
        position_rel_camera, _ = change_view_position(camera_position, world_position)
        # rotation only: undo the camera's orientation
        view_position, view_vertices = change_view_orientation(camera_orientation, spun_vertices, position_rel_camera)
        camera_space_vertices = view_vertices + view_position

        # project() returns None when the object is too close and gets culled
        projected_tesseracts.append(project(camera_space_vertices, W_DIST, Z_DIST, NEAR_CLIP_MARGIN))

    # ---------- drawing ----------
    screen.fill((0, 0, 0))
    for edges, projected in zip(tesseracts_edges, projected_tesseracts):
        if projected is not None:
            screen_points = projected * PIXELS_PER_UNIT + SCREEN_CENTER
            for a, b in edges:
                pygame.draw.line(screen, "gray", screen_points[a], screen_points[b])
    # on-screen text, drawn last so it sits on top of the objects
    sim_time_text = font.render(f"sim time {sim_time:.1f} s", True, (255, 255, 255))
    screen.blit(sim_time_text, (10, 10))
    speed_label = f"speed {time_scale:g}x" + ("  PAUSED" if paused else "")
    screen.blit(font.render(speed_label, True, (255, 255, 255)), (260, 10))
    status = f"walls: ON [{lo}, {hi}]" if wall_on else "walls: OFF"
    screen.blit(font.render(status, True, (255, 255, 255)), (10, 40))
    if pygame.time.get_ticks() < message_expires:
        message = font.render(message_text, True, (255, 255, 255))
        screen.blit(message, (10, 70))

    pygame.display.flip()

pygame.quit()