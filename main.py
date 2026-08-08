import pygame
from tesseract import Tesseract
from functions import edge_list,rotate_xw,project

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

running = True
tesseract = Tesseract(0,0,0,0)
edges = edge_list(tesseract.vertices) # gets all the edges of tesseract
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    theta = 0.01
    
    rotated = rotate_xw(tesseract.vertices,theta)
    tesseract.vertices = rotated
    translated = rotated + tesseract.position
    projected_tesseract = project(translated)
    projected_tesseract = projected_tesseract*100 + (screen_width // 2, screen_height // 2)
    
    

    # --- your drawing code goes here ---
    for i,j in edges : 
        pygame.draw.line(surface=screen,color="gray",start_pos=projected_tesseract[i],end_pos=projected_tesseract[j])
    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()