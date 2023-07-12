import pygame
import time
pygame.init()
#set up screen
screen_width=1500
screen_height=750
top_bar_height=50
size=[screen_width,screen_height]
screen=pygame.display.set_mode(size)

def copy_list(l):
    if type(l)==list:
        result=[]
        for i in l:
            result.append(copy_list(i))
        return result
    else:
        return l

#load images
img_keys=['left','right','top','bottom','top_left','top_right','bottom_left','bottom_right','space','star','black','white']
img={}
for k in img_keys:
    img[k]=pygame.image.load("./Sprites/"+k+".png")

#Rules constants
SUICIDE_LEGAL=True
SUPERKO="Positional"

#prints a message to the top bar
def display_message(message):
    print(message)#change this to show it on screen

#shows the board and pieces on screen
class Board:
    def __init__(self,x,y,space_length,board_size):
        global img
        self.x=x
        self.y=y
        self.space_length=space_length
        self.board_size=board_size
        self.position=blank_position(board_size)
        self.img={}
        self.history=[blank_position(board_size)]#history of all board positions
        for key in img.keys():
            self.img[key]=pygame.transform.scale(img[key],(self.space_length,self.space_length))
    def display_board(self):
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
                    space_image=self.img['black']
                elif self.position[i][j]==2:
                    space_image=self.img['white']
                elif i==0:
                    if j==0:
                        space_image=self.img['top_left']
                    elif j==board_size-1:
                        space_image=self.img['bottom_left']
                    else:
                        space_image=self.img['left']
                elif i==self.board_size-1:
                    if j==0:
                        space_image=self.img['top_right']
                    elif j==self.board_size-1:
                        space_image=self.img['bottom_right']
                    else:
                        space_image=self.img['right']
                elif j==0:
                    space_image=self.img['top']
                elif j==self.board_size-1:
                    space_image=self.img['bottom']
                elif self.board_size==19 and i in [3,9,15] and j in [3,9,15]:
                    space_image=self.img['star']
                else:
                    space_image=self.img['space']
                screen.blit(space_image,(self.x+i*self.space_length,self.y+j*self.space_length))
    def mouse_over(self,x,y):#From mouse coordinates, determine which if any space mouse is hovering over
        result_x=int((x-self.x)/self.space_length)
        result_y=int((y-self.y)/self.space_length)
        if result_x>=0 and result_x<self.board_size and result_y>=0 and result_y<self.board_size:
            return (result_x,result_y)
    def hover_stone(self,tup,stone):#hover a stone over a board position, if it is empty (stone=1: black, stone=2: white)
        if self.position[tup[0]][tup[1]]==0 and (stone==1 or stone==2):
            alpha=128
            if stone==1:
                ghost_stone_image=self.img['black'].convert_alpha()
            elif stone==2:
                ghost_stone_image=self.img['white'].convert_alpha()
            ghost_stone_image.set_alpha(alpha)
            screen.blit(ghost_stone_image,(self.x+tup[0]*self.space_length,self.y+tup[1]*self.space_length))              
def blank_position(board_size):
    result=[]
    for i in range(board_size):
        result.append([])
        for j in range(board_size):
            result[i].append(0)
    return result

#remove groups without liberties of color 1=black or 2=white
def remove_surrounded(position,color):
    grouped=copy_list(position)#0=group not found yet, 1=group found and checked, 2=current group we're checking
    for i in range(len(grouped)):
        for j in range(len(grouped[i])):
            grouped[i][j]=0#an array of zeros the same size as position
    new_position=copy_list(position)
    for i in range(len(position)):
        for j in range(len(position)):#we only support square boards
            if position[i][j]==color and grouped[i][j]==0:#if the stone hasn't been shown to be part of a group yet:
                #Find the group, and remove it if no liberties
                tuples=[(i,j)]#stones we know are part of the group, but haven't yet checked for liberties and adjacent stones
                checked=[]#stones we've checked already as part of the group
                liberties=False#flip to true if we ever find a liberty
                while len(tuples)>0:
                    tup=tuples.pop()#deal with the last one
                    checked.append(tup)
                    grouped[tup[0]][tup[1]]=1
                    if tup[0]>0 and position[tup[0]-1][tup[1]]==color and grouped[tup[0]-1][tup[1]]==0:#check left for group stone
                        tuples.append((tup[0]-1,tup[1]))
                    if tup[1]>0 and position[tup[0]][tup[1]-1]==color and grouped[tup[0]][tup[1]-1]==0:#check up for group stone
                        tuples.append((tup[0],tup[1]-1))
                    if tup[0]<len(position)-1 and position[tup[0]+1][tup[1]]==color and grouped[tup[0]+1][tup[1]]==0:#check right for group stone
                        tuples.append((tup[0]+1,tup[1]))
                    if tup[1]<len(position)-1 and position[tup[0]][tup[1]+1]==color and grouped[tup[0]][tup[1]+1]==0:#check down for group stone
                        tuples.append((tup[0],tup[1]+1))
                    if not liberties and tup[0]>0 and position[tup[0]-1][tup[1]]==0:#check for liberties
                        liberties=True
                    if not liberties and tup[1]>0 and position[tup[0]][tup[1]-1]==0:
                        liberties=True
                    if not liberties and tup[0]<len(position)-1 and position[tup[0]+1][tup[1]]==0:
                        liberties=True
                    if not liberties and tup[1]<len(position)-1 and position[tup[0]][tup[1]+1]==0:
                        liberties=True
                #Now we've set all stones in the group to 1.
                #remove stones in the group if no liberties
                if not liberties:
                    for tup in checked:
                        new_position[tup[0]][tup[1]]=0
    return new_position

#take in current board position, position of move, and player moving
#return the board position after the move, or None if the move position is already occupied
def move_with_capture(position,move_pos,player_turn):
    new_position=copy_list(position)
    if new_position[move_pos[0]][move_pos[1]]==0:
        new_position[move_pos[0]][move_pos[1]]=player_turn
    else:
        return None
    new_position=remove_surrounded(new_position,3-player_turn)
    new_position=remove_surrounded(new_position,player_turn)
    return new_position

#check if move is legal given history. If so return position after move, otherwise return None    
def is_legal(history,position,move_pos,player_turn):
    new_position=move_with_capture(position,move_pos,player_turn)
    if new_position==None:
        return None
    if not SUICIDE_LEGAL and new_position[move_pos[0]][move_pos[1]]==0:
        print("Suicide is illegal")
        return None
    if SUPERKO=="Positional" and new_position in history:            
        print("Repeating position is illegal")
        return None
    return new_position

board_size=19
space_length=int((screen_height-top_bar_height)/board_size)
board_length=board_size*space_length
board_x=int((screen_width-board_length)/2)
board_y=int((screen_height-top_bar_height-board_length)/2)+top_bar_height
cur_board=Board(board_x,board_y,space_length,board_size)
player_turn=1#black's turn first
last_mouse_board_pos=None#initialize mouse position on board
do_hover=False#Whether to hover a ghost stone over a position(used to avoid too many legality checks)
while True:
    x,y=pygame.mouse.get_pos()
    mouse_board_pos=cur_board.mouse_over(x,y)
    for event in pygame.event.get():#update when placing down stones
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:#Left mouse button is 1, right is 3, middle is 2
            if mouse_board_pos:
                new_position=is_legal(cur_board.history,cur_board.position,mouse_board_pos,player_turn)
                if new_position:
                    cur_board.position=new_position
                    player_turn=3-player_turn
                    cur_board.history.append(copy_list(cur_board.position))
    cur_board.display_board()
    if not mouse_board_pos:#we don't hover when we're not over a square
        do_hover=False
    if mouse_board_pos and mouse_board_pos!=last_mouse_board_pos:#check for hover whenever mouse pos changes
        if is_legal(cur_board.history,cur_board.position,mouse_board_pos,player_turn):
            do_hover=True
        else:
            do_hover=False
    if do_hover:
        cur_board.hover_stone(mouse_board_pos,player_turn)        
    last_mouse_board_pos=mouse_board_pos
    pygame.display.flip()
