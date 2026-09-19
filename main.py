import pygame
from tesseract import Tesseract
from functions import edge_list,project,change_view_position,change_view_orientation
from rotation import *
from camera import *

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

running = True
tesseract = Tesseract(1,2,6,1)
tesseract_position = tesseract.position
tesseract_vertices = tesseract.vertices

camera = Camera()
camera_orientation = camera.orientation
camera_position = camera.position

dt=0

edges = edge_list(tesseract.vertices) # gets all the edges of tesseract
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            dx,dy = event.rel
            print(dx,dy)
            sensitivity = 0.001
            camera_orientation =camera.direction_xz(dx*sensitivity)
            camera_orientation =camera.direction_yz(dy*sensitivity)


    screen.fill((0, 0, 0))
    theta = 0
    # print(camera_orientation)
   
    view_space_position,_= change_view_position(camera_position,tesseract_position)
    
   
    rotated = double_rotation(rotate_xw,rotate_yz,theta,theta,tesseract_vertices)
    view_tesseract_position,view_space_vertex =change_view_orientation(camera_orientation,rotated,view_space_position)
    tesseract_vertices = rotated
    translated = view_space_vertex + view_tesseract_position
    


    #projection
    projected_tesseract = project(translated,camera_position[3] +5,camera_position[2] +5)
    projected_tesseract = projected_tesseract*100 + (screen_width // 2, screen_height // 2)


    
    keys = pygame.key.get_pressed()

    #movement of camera
    if keys[pygame.K_f]:
        camera_position = camera.travel_y(3*dt)
    if keys[pygame.K_r]:
        camera_position = camera.travel_y(-3*dt)
    if keys[pygame.K_d]:
        camera_position = camera.travel_x(3*dt)
    if keys[pygame.K_a]:
        camera_position = camera.travel_x(-3*dt)
    if keys[pygame.K_s]:
        camera_position = camera.travel_z(3*dt)
    if keys[pygame.K_w]:
        camera_position = camera.travel_z(-3*dt)
    if keys[pygame.K_e]:
        camera_position = camera.travel_w(3*dt)
    if keys[pygame.K_q]:
        camera_position = camera.travel_w(-3*dt)

    #direction of camera
    # if dx:
    #     sensitivity = 0.01
    #     camera_orientation =camera.direction_xz(dx*sensitivity)
    #     camera_orientation =camera.direction_yz(dy*sensitivity)
    # else : 
    #     camera_orientation = camera.default()

    # print(camera.orientation)

    

    dt = clock.tick(60) / 1000
    # --- drawing code here ---
    for i,j in edges : 
        pygame.draw.line(surface=screen,color="gray",start_pos=projected_tesseract[i],end_pos=projected_tesseract[j])
    

    pygame.display.flip()
    

pygame.quit()