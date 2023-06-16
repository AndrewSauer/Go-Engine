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

#contains all the info required to display the board

#prints a message to the top bar
def display_message(message):
    print(message)#change this to show it on screen

#shows the board and pieces on screen
class Board:
    def __init__(self,x,y,space_length,board_size):
        self.x=x
        self.y=y
        self.space_length=space_length
        self.board_size=board_size
        self.position=blank_position(board_size)
    def display_board(self):
        global img
        if not len(self.position)==self.board_size:
            print("Fatal error: Invalid position matrix!")
            print(self.position)
            exit()
        for i in range(self.board_size):
            if not len(self.position[i])==self.board_size:
                print("Fatal error: Invalid position matrix!")
                print(self.position)
                exit()
            for j in range(self.board_size):
                if self.position[i][j]==1:
                    space_image=img['black']
                elif self.position[i][j]==2:
                    space_image=img['white']
                elif i==0:
                    if j==0:
                        space_image=img['top_left']
                    elif j==board_size-1:
                        space_image=img['bottom_left']
                    else:
                        space_image=img['left']
                elif i==self.board_size-1:
                    if j==0:
                        space_image=img['top_right']
                    elif j==self.board_size-1:
                        space_image=img['bottom_right']
                    else:
                        space_image=img['right']
                elif j==0:
                    space_image=img['top']
                elif j==self.board_size-1:
                    space_image=img['bottom']
                elif self.board_size==19 and i in [3,9,15] and j in [3,9,15]:
                    space_image=img['star']
                else:
                    space_image=img['space']
                new_space_image=pygame.transform.scale(space_image,(self.space_length,self.space_length))
                screen.blit(new_space_image,(self.x+i*self.space_length,self.y+j*self.space_length))

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
cur_board=Board(board_x,board_y,space_length,board_size)
cur_board.position[0][0]=1
cur_board.position[18][18]=2
cur_board.display_board()
pygame.display.flip()
