#Main rule differences which need be included
#Ko and superko rules
#Suicide
#Eyes in Seki(and determination of seki when eyes don't count)
#Scoring system(area/territory/stone/others?)
#Komi/pierule/balance
#How the game ends
#Resolving life&death disputes after end of game
#Handicap setup
#Starting position
#Time controls

import pygame
import time
pygame.init()
#set up screen
screen_width=1500
screen_height=750
size=[screen_width,screen_height]
screen=pygame.display.set_mode(size)

#Other visual parameters
top_bar_height=50
game_font=pygame.font.SysFont("Times New Roman",30)

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
#SUICIDE_LEGAL=True
#SUPERKO="Positional"

#prints a message to the top bar
def display_message(textbox,message):
    textbox.text=message
    textbox.draw()

#Textbox class
class textBox:
    def __init__(self, name, font=game_font, screen=screen, x=0,y=0,width=100,height=20,background=(255,255,255),border=(0,0,0),textcolor=(0,0,0),text=""):
        self.name=name
        self.x=x
        self.y = y
        self.width = width
        self.height = height
        self.background=background
        self.border=border
        self.textcolor=textcolor
        self.text=text
        self.font=font
        self.screen = screen
    def draw(self):
        self.rect = pygame.draw.rect(self.screen,self.background,(self.x,self.y,self.width,self.height))
        pygame.draw.rect(self.screen,self.border,(self.x,self.y,self.width,self.height),width=1)
        text_surface=self.font.render(self.text,False,self.textcolor)
        text_rect=text_surface.get_rect(center=(self.x+self.width/2,self.y+self.height/2))
        self.screen.blit(text_surface,text_rect)
    def within(self,x,y):
        return x>=self.x and x<=self.x+self.width and y>=self.y and y<=self.y+self.height

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
        #Funny, int casting interacts weird with negatives. Negative numbers round up, positive numbers round down
        #so we just make sure it isn't negative
        if x-self.x<0 or y-self.y<0:
            return None
        result_x=int((x-self.x)/self.space_length)
        result_y=int((y-self.y)/self.space_length)
        if result_x>=0 and result_x<self.board_size and result_y>=0 and result_y<self.board_size:
            return (result_x,result_y)
        else:
            return None
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

class gameState:#state of a game in progress(before end of game and agreement phase)
    def __init__(self,board,rule_config):#Initialize game at start from initial board
        self.turn=1#1=black's turn, 2=white's turn
        self.board=board#Board object representing current position and history
        self.black_prisoners=0#Current number of prisoners taken by black
        self.white_prisoners=0#Current number of prisoners taken by white
        if type(rule_config.komi)==int:
            self.white_prisoners+=rule_config.komi#add fixed komi
        self.black_prisoners_history=[self.black_prisoners]
        self.white_prisoners_history=[self.white_prisoners]
        self.rule_config=rule_config
        #ADD: allow handicap setups, initial prisoner counts beyond just komi, etc
    def play_at_pos(self,board_pos):#play at a position if such a play is legal
        new_position=self.is_legal(board_pos)
        if new_position:
            #add captured prisoners
            for i in range(len(new_position)):
                for j in range(len(new_position)):
                    if self.board.position[i][j]==1 and new_position[i][j]==0:#black piece was taken, add to white prisoners
                        self.white_prisoners+=1
                    elif self.board.position[i][j]==2 and new_position[i][j]==0:#white piece was taken, add to black prisoners
                        self.black_prisoners+=1
                    elif board_pos[0]==i and board_pos[1]==j and new_position[i][j]==0:#suicide stone was taken, add to prisoners of whose turn it is
                        if self.turn==1:#black's turn, white gets the suicide prisoners
                            self.white_prisoners+=1
                        elif self.turn==2:#white's turn, black gets the suicide prisoners
                            self.black_prisoners+=1
            self.board.position=new_position#change to new position
            self.turn=3-self.turn#switch turn
            self.board.history.append(copy_list(self.board.position))#add to history
            self.black_prisoners_history.append(self.black_prisoners)
            self.white_prisoners_history.append(self.white_prisoners)
            global top_bar
            if state.turn==1:
                display_turn(top_bar,"Black to play.")
            else:
                display_turn(top_bar,"White to play.")
    #check if move is legal given history. If so return position after move, otherwise return None
    def is_legal(self,move_pos):
        global top_bar#so we can display rules messages on the top bar
        new_position=move_with_capture(self.board.position,move_pos,self.turn)
        if new_position==None:
            return None
        if not self.rule_config.suicide and new_position[move_pos[0]][move_pos[1]]==0:
            display_message(top_bar,"Suicide is illegal")
            return None
        if self.rule_config.superko=="Positional" and new_position in self.board.history:            
            display_message(top_bar,"Repeating position is illegal")
            return None
        return new_position
    #CONTINUE: Allow passing, ending, pierule komi

class ruleConfig:#A configuration of the rules we use for any particular game
    def __init__(self,superko="Positional",suicide=True,sekieyes=True,scoring="Area",komi="Pierule",ending="TwoPass",disputes="FourPass",handicap=0,startpos=blank_position(19),timecontrols=None):
        self.superko=superko#
        self.suicide=suicide#
        self.sekieyes=sekieyes#
        self.scoring=scoring#
        self.komi=komi#
        self.ending=ending#
        self.disputes=disputes#
        self.handicap=handicap#
        self.startpos=startpos#
        self.timecontrols=timecontrols#

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

def stateUndo(state):#FIX: top bar is sometimes the wrong colour after undoing? IDK why...
    #if game hasn't started, do nothing
    if not(len(state.board.history)==len(state.black_prisoners_history) and len(state.board.history)==len(state.white_prisoners_history)):
        print("Error: History lists unmatched!")
        return state
    if len(state.board.history)<=1:
        return state
    lastPosition=copy_list(state.board.history[-2])#CHECK: Does ko and superko still work properly on undo?
    state.turn=3-state.turn#swap turn
    state.board.position=lastPosition#turn to last position
    state.black_prisoners=state.black_prisoners_history[-2]
    state.white_prisoners=state.white_prisoners_history[-2]
    state.board.history.pop()#remove last turn on history
    state.black_prisoners_history.pop()
    state.white_prisoners_history.pop()
    return state

#check if move is legal given history. If so return position after move, otherwise return None    
#def is_legal(history,position,move_pos,player_turn):
#    new_position=move_with_capture(position,move_pos,player_turn)
#    if new_position==None:
#        return None
#    if not SUICIDE_LEGAL and new_position[move_pos[0]][move_pos[1]]==0:
#        print("Suicide is illegal")
#        return None
#    if SUPERKO=="Positional" and new_position in history:            
#        print("Repeating position is illegal")
#        return None
#    return new_position

#Create board and gamestate
board_size=19
space_length=int((screen_height-top_bar_height)/board_size)
board_length=board_size*space_length
board_x=int((screen_width-board_length)/2)
board_y=int((screen_height-top_bar_height-board_length)/2)+top_bar_height
state=gameState(Board(board_x,board_y,space_length,board_size),ruleConfig(ending="nimgoTies",komi=7))
#cur_board=Board(board_x,board_y,space_length,board_size)

#Create top bar, display "black to play" on it
top_bar=textBox(name="topBar",x=board_x,y=0,width=board_length,height=top_bar_height,background=(0,0,0),border=(255,255,255),textcolor=(255,255,255),text="")
display_message(top_bar,"Black to play.")
#Create prisoner count bars
black_prisoner_bar=textBox(name="blackPrisonerBar",x=5,y=0,width=board_x-10,height=top_bar_height,background=(0,0,0),border=(255,255,255),textcolor=(255,255,255),text="")
display_message(black_prisoner_bar,"Black Prisoners: "+str(state.black_prisoners))
white_prisoner_bar=textBox(name="whitePrisonerBar",x=board_x+board_length+5,y=0,width=board_x-10,height=top_bar_height,text="")
display_message(white_prisoner_bar,"White Prisoners: "+str(state.white_prisoners))

#create buttons list
buttons=[]
#add buttons for resigning
buttons.append(textBox(name="blackResign",x=5,y=screen_height-top_bar_height-5,width=board_x-10,height=top_bar_height,background=(0,0,0),border=(255,255,255),textcolor=(255,255,255),text="Black Resign"))
buttons.append(textBox(name="whiteResign",x=board_x+board_length+5,y=screen_height-top_bar_height-5,width=board_x-10,height=top_bar_height,text="White Resign"))
display_message(buttons[0],"Black Resign")
display_message(buttons[1],"White Resign")
if state.rule_config.ending=="nimgo" or state.rule_config.ending=="nimgoTies":#create buttons for black and white to return prisoners
    buttons.append(textBox(name="blackPrisonerReturn",x=5,y=screen_height-2*top_bar_height-10,width=board_x-10,height=top_bar_height,background=(0,0,0),border=(255,255,255),textcolor=(255,255,255),text="Return Prisoner"))
    display_message(buttons[-1],"Return Prisoner")
    buttons.append(textBox(name="whitePrisonerReturn",x=board_x+board_length+5,y=screen_height-2*top_bar_height-10,width=board_x-10,height=top_bar_height,text="Return Prisoner"))
    display_message(buttons[-1],"Return Prisoner")
if state.rule_config.ending=="nimgoTies":#create button for black to declare tie when white has no prisoners left
    buttons.append(textBox(name="blackDeclareTie",x=5,y=screen_height-3*top_bar_height-15,width=board_x-10,height=top_bar_height,background=(0,0,0),border=(255,255,255),textcolor=(255,255,255),text="Declare Tie"))
    display_message(buttons[-1],"Declare Tie")
def display_turn(top_bar,turn):
    if state.turn==1:
        top_bar.background=(0,0,0)
        top_bar.border=(255,255,255)
        top_bar.textcolor=(255,255,255)
        display_message(top_bar,"Black to play.")#must come after the other changes, since this is when the bar is actually drawn
    else:
        top_bar.background=(255,255,255)
        top_bar.border=(0,0,0)
        top_bar.textcolor=(0,0,0)
        display_message(top_bar,"White to play.")

#player_turn=1#black's turn first
last_mouse_board_pos=None#initialize mouse position on board
do_hover=False#Whether to hover a ghost stone over a position(used to avoid too many legality checks)
ctrl_held=False#Whether ctrl key is held
game_over=False#For now, freeze the game when it is over
while True:
    x,y=pygame.mouse.get_pos()
    mouse_board_pos=state.board.mouse_over(x,y)
    if not mouse_board_pos:#display turn if we're outside the board
        display_turn(top_bar,state.turn)
    for event in pygame.event.get():#update when placing down stones
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:#Left mouse button is 1, right is 3, middle is 2
            if mouse_board_pos:
                state.play_at_pos(mouse_board_pos)
                #after playing at position, display new prisoner counts
                display_message(black_prisoner_bar,"Black Prisoners: "+str(state.black_prisoners))
                display_message(white_prisoner_bar,"White Prisoners: "+str(state.white_prisoners))
            else:#if outside the board, check for button presses
                for button in buttons:
                    if button.within(x,y):
                        if button.name=="blackResign" and state.turn==1:#black resignation on black's turn
                            top_bar.background=(255,255,255)
                            top_bar.border=(0,0,0)
                            top_bar.textcolor=(0,0,0)
                            display_message(top_bar,"White wins by resignation!")
                            game_over=True
                        elif button.name=="whiteResign" and state.turn==2:#white resignation on white's turn
                            top_bar.background=(0,0,0)
                            top_bar.border=(255,255,255)
                            top_bar.textcolor=(255,255,255)
                            display_message(top_bar,"Black wins by resignation!")
                            game_over=True
                        elif button.name=="blackPrisonerReturn" and state.turn==1 and state.black_prisoners>0:#return black prisoner instead of black turn
                            state.black_prisoners-=1
                            #add to history
                            state.black_prisoners_history.append(state.black_prisoners)
                            state.white_prisoners_history.append(state.white_prisoners)
                            state.board.history.append(copy_list(state.board.position))
                            display_message(black_prisoner_bar,"Black Prisoners: "+str(state.black_prisoners))#display new number of black prisoners
                            state.turn=2#change turn
                        elif button.name=="whitePrisonerReturn" and state.turn==2 and state.white_prisoners>0:#return white prisoner instead of black turn
                            state.white_prisoners-=1
                            #add to history
                            state.black_prisoners_history.append(state.black_prisoners)
                            state.white_prisoners_history.append(state.white_prisoners)
                            state.board.history.append(copy_list(state.board.position))
                            display_message(white_prisoner_bar,"White Prisoners: "+str(state.white_prisoners))#display new number of white prisoners
                            state.turn=1#change turn
                        elif button.name=="blackDeclareTie" and state.turn==1 and state.white_prisoners==0:#Allows black to declare a tie if White is out of prisoners
                            top_bar.background=(128,128,128)
                            top_bar.border=(0,0,0)
                            top_bar.textcolor=(0,0,0)
                            display_message(top_bar,"Game is a tie!")
                            game_over=True

        elif event.type==pygame.KEYDOWN and event.key==pygame.K_LCTRL:
            ctrl_held=True
        elif event.type==pygame.KEYUP and event.key==pygame.K_LCTRL:
            ctrl_held=False
        elif event.type==pygame.KEYDOWN and event.key==pygame.K_z and ctrl_held:
            state=stateUndo(state)
            #display new prisoner counts and turn after undoing
            display_turn(top_bar,state.turn)
            display_message(black_prisoner_bar,"Black Prisoners: "+str(state.black_prisoners))
            display_message(white_prisoner_bar,"White Prisoners: "+str(state.white_prisoners))

    state.board.display_board()#display board
    if mouse_board_pos!=last_mouse_board_pos:#check for hover whenever mouse pos changes
        if mouse_board_pos and state.is_legal(mouse_board_pos):
            do_hover=True
        else:
            do_hover=False
    if do_hover:
        state.board.hover_stone(mouse_board_pos,state.turn)
        display_turn(top_bar,state.turn)

    last_mouse_board_pos=mouse_board_pos
    pygame.display.flip()
    if game_over:
        break#CONTINUE: find something better to do when the game is over
