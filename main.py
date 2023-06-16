import pygame
pygame.init()
#set up screen
screen_width=1500
screen_height=750
top_bar_height=50
size=[screen_width,screen_height]
screen=pygame.display.set_mode(size)

#load images
img_keys=['left','right','top','bottom','top_left','top_right','bottom_left','bottom_right','space','star','black','white']
img={}
for k in img_keys:
    img[k]=pygame.image.load("./Sprites/"+k+".png")

#prints a message to the top bar
def display_message(message):
    print(message)#change this to show it on screen

#shows the board and pieces on screen
def display_board(x,y,space_length,position):
    global img
    board_size=len(position)
    for i in range(board_size):
        if not len(position[i])==board_size:
            print("Fatal error: Invalid position matrix!")
            print(position)
            exit()
        for j in range(board_size):
            if position[i][j]==1:
                space_image=img['black']
            elif position[i][j]==2:
                space_image=img['white']
            elif i==0:
                if j==0:
                    space_image=img['top_left']
                elif j==board_size-1:
                    space_image=img['bottom_left']
                else:
                    space_image=img['left']
            elif i==board_size-1:
                if j==0:
                    space_image=img['top_right']
                elif j==board_size-1:
                    space_image=img['bottom_right']
                else:
                    space_image=img['right']
            elif j==0:
                space_image=img['top']
            elif j==board_size-1:
                space_image=img['bottom']
            elif board_size==19 and i in [3,9,15] and j in [3,9,15]:
                space_image=img['star']
            else:
                space_image=img['space']
            new_space_image=pygame.transform.scale(space_image,(space_length,space_length))
            screen.blit(new_space_image,(x+i*space_length,y+j*space_length))

def blank_position(board_size):
    result=[]
    for i in range(board_size):
        result.append([])
        for j in range(board_size):
            result[i].append(0)
    return result
board_size=19
space_length=int((screen_height-top_bar_height)/board_size)
board_length=board_size*space_length
board_x=int((screen_width-board_length)/2)
board_y=int((screen_height-top_bar_height-board_length)/2)+top_bar_height
cur_position=blank_position(board_size)
cur_position[0][0]=1
cur_position[18][18]=2
display_board(board_x,board_y,space_length,cur_position)
pygame.display.flip()
