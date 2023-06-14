import pygame
pygame.init()
#set up screen
screen_width=1500
screen_height=750
top_bar_height=50
size=[screen_width,screen_height]
screen=pygame.display.set_mode(size)

#prints a message to the top bar
def display_message(message):
    print(message)#change this to show it on screen

#shows the board on screen, without pieces
def display_board(screen_width,screen_height,top_bar_height,board_size):
    space_length=int((screen_height-top_bar_height)/board_size)
    board_length=board_size*space_length
    board_x=int((screen_width-board_length)/2)
    board_y=int((screen_height-top_bar_height-board_length)/2)+top_bar_height
    for i in range(board_size):
        for j in range(board_size):
            if i==0:
                if j==0:
                    space_image="./Sprites/top_left.png"
                elif j==board_size-1:
                    space_image="./Sprites/bottom_left.png"
                else:
                    space_image="./Sprites/left.png"
            elif i==board_size-1:
                if j==0:
                    space_image="./Sprites/top_right.png"
                elif j==board_size-1:
                    space_image="./Sprites/bottom_right.png"
                else:
                    space_image="./Sprites/right.png"
            elif j==0:
                space_image="./Sprites/top.png"
            elif j==board_size-1:
                space_image="./Sprites/bottom.png"
            elif board_size==19 and i in [3,9,15] and j in [3,9,15]:
                space_image="./Sprites/star.png"
            else:
                space_image="./Sprites/space.png"
            space_image=pygame.transform.scale(pygame.image.load(space_image),(space_length,space_length))
            screen.blit(space_image,(board_x+i*space_length,board_y+j*space_length))
    pygame.display.flip()
display_board(screen_width,screen_height,top_bar_height,19)
