import pygame
from tesseract import Tesseract
from functions import edge_list, project, change_view_position, change_view_orientation
from rotation import *
from camera import Camera
from physics import rk4_step

pygame.init()

#settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
FPS = 60
PIXELS_PER_UNIT = 100

# eye-to-glass distances for the projection, fixed, NOT the camera's position
Z_DIST = 20
W_DIST = 20
MAX_SCALE = 4                          # biggest zoom allowed before an object is culled
NEAR_CLIP_MARGIN = Z_DIST / MAX_SCALE  # cull when (dist - coordinate) drops below this

MOVE_SPEED = 3
KEY_ROT_SPEED = 1.5      # radians per second
MOUSE_SENSITIVITY = 0.001
OBJECT_SPIN = 0        # object auto-rotation, off for now

#setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

#scene
tesseracts = [Tesseract(4,2,3,1),Tesseract(2,4,1,6)]
masses = np.array([5.0,10.5])
charges = np.array([1.0,-1.0])
velocities = np.array([[-1.0, 1.0, 0.0, 4.0],
                               [0.0, -1.0, 0.0, 0.0]])
positions = np.array([t.position for t in tesseracts], dtype=float)

if not(len(tesseracts) == 0) :
    tesseracts_world_position = []
    tesseracts_world_vertices = []
    tesseracts_edges = []
    for i in tesseracts : 
        tesseracts_world_position.append(i.position)
        tesseracts_world_vertices.append(i.vertices)
        tesseracts_edges.append(edge_list(i.vertices))

camera = Camera()
camera_position = camera.position
camera_orientation = camera.orientation

dt = 0
running = True

while running:
    dt = clock.tick(FPS) / 1000  # seconds since last frame

    #events
    mouse_dx = 0
    mouse_dy = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False  # cursor is locked, so esc is the way out
        if event.type == pygame.MOUSEMOTION:
            # event.rel instead of get_rel(), which gives (0, 0) on my trackpad
            mouse_dx += event.rel[0]
            mouse_dy += event.rel[1]

    # summed and applied once per frame: many tiny rotations in a random
    # order per frame feel jittery since rotations don't commute
    if mouse_dx or mouse_dy:
        camera_orientation = camera.direction_xz(mouse_dx * MOUSE_SENSITIVITY)
        camera_orientation = camera.direction_yz(mouse_dy * MOUSE_SENSITIVITY)

    #keyboard
    keys = pygame.key.get_pressed()
    if keys[pygame.K_k]:
        # k held: movement keys rotate the camera in the w planes instead of moving it
        if keys[pygame.K_d]:
            camera_orientation = camera.direction_xw(KEY_ROT_SPEED * dt)
        if keys[pygame.K_a]:
            camera_orientation = camera.direction_xw(-KEY_ROT_SPEED * dt)
        if keys[pygame.K_e]:
            camera_orientation = camera.direction_yw(KEY_ROT_SPEED * dt)
        if keys[pygame.K_q]:
            camera_orientation = camera.direction_yw(-KEY_ROT_SPEED * dt)
        if keys[pygame.K_w]:
            camera_orientation = camera.direction_zw(KEY_ROT_SPEED * dt)
        if keys[pygame.K_s]:
            camera_orientation = camera.direction_zw(-KEY_ROT_SPEED * dt)
    else:
        # movement follows the camera's own axes, not the world's
        if keys[pygame.K_d]:
            camera_position = camera.travel_x(MOVE_SPEED * dt)
        if keys[pygame.K_a]:
            camera_position = camera.travel_x(-MOVE_SPEED * dt)
        if keys[pygame.K_w]:
            camera_position = camera.travel_z(MOVE_SPEED * dt)
        if keys[pygame.K_s]:
            camera_position = camera.travel_z(-MOVE_SPEED * dt)
        if keys[pygame.K_e]:
            camera_position = camera.travel_y(MOVE_SPEED * dt)
        if keys[pygame.K_q]:
            camera_position = camera.travel_y(-MOVE_SPEED * dt)

    #view transform
    # world_* is the permanent copy, view_* is rebuilt every frame and never written back

        # physics: one step per frame for all objects; positions is the only thing written
    positions, velocities = rk4_step(positions, velocities, masses, dt, charges)

    # view transform: reads positions, never writes to it
    projected_tesseracts = []
    for i, world_vertices in enumerate(tesseracts_world_vertices):
        world_position = positions[i]
        world_vertices = double_rotation(rotate_yz, rotate_zw, OBJECT_SPIN, OBJECT_SPIN, world_vertices)

        position_rel_camera, _ = change_view_position(camera_position, world_position)
        view_position, view_vertices = change_view_orientation(camera_orientation, world_vertices, position_rel_camera)
        camera_space_vertices = view_vertices + view_position

        projected_tesseracts.append(project(camera_space_vertices, W_DIST, Z_DIST, NEAR_CLIP_MARGIN))
        
    #drawing
    screen.fill((0, 0, 0))
    for edges,projected in zip(tesseracts_edges,projected_tesseracts):
        if projected is not None:
            screen_points = projected * PIXELS_PER_UNIT + SCREEN_CENTER
            for i, j in edges:
                pygame.draw.line(screen, "gray", screen_points[i], screen_points[j])
    pygame.display.flip()

pygame.quit()