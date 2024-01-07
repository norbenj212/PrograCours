#-*- coding: utf-8 -*-
from remote_play import * 
import math, os, time
from blessed import *
from random import randint

term = Terminal()

# other functions
def occupied_place(board,coord):
    """
    Checks if the place is occupied

    Parameters
    ------------
    board : the game board (list)
    coord : the coordinates of the chosen case (list)

    Return 
    -------
    occupied_verif : True if the place is occupied, False otherwise (bool)

    Version
    -------
    spécification : Thomas Busoni (v1 : 9/03/2023)
    implémentation : Thomas Busoni (v1 : 9/03/2023)
                                   (v2 : 16/03/2023)

    """
    return board[coord[1]][coord[0]]['ghost']

def isInRange(current_position, target_position):
    """
    Calculates the different movements of the ghosts 

    Parameters
    ------------
    current_position : position of the ghost (list)
    target_position : the target position (list)

    Return
    -------
    verif : True if action in range, False otherwise (bool)

    Version
    --------
    spécification : Thomas Busoni (v1 : 9/03/2023)
    implémentation : Thomas Busoni (v1 : 9/03/2023) 
    """

    if (current_position[0]-target_position[0] >= -1 and current_position[0]-target_position[0] <= 1) and (current_position[1]-target_position[1] >= -1 and current_position[1]-target_position[1] <= 1) :
        verif = True
    else : 
        verif = False
    return verif

def isGameFinished(board,turns_withoutattacks) :
    """Tells if the game is finished and who won
    
    Parameters :
    -----------
    board : the current state of the board (list)
    turns_withoutattacks : number of turns since the last fight (int)

    Returns :
    ---------
    winner : who won the game (returns 'nobody' if the game isn't finished) (str)
    end : True if the game is finished, False otherwise (bool)

    Versions :
    ---------
    spécification : Thomas Busoni (v1 : 9/03/2023)
    implémentation : Thomas Busoni (v1 : 9/03/2023)
                                   (v2 : 20/03/2023)
    """
    team1_ghosts = 0
    team2_ghosts = 0

    for lines in range(0, len(board)) :
        for columns in range(0, len(board[lines])) :
            if board[lines][columns]['ghost'] != False :
                if board[lines][columns]['ghost']['team'] == 1 :
                    team1_ghosts += 1
                else :
                    team2_ghosts += 1
    end = True
    if team1_ghosts == 0 :
        winner = 'team2'
    elif team2_ghosts == 0 :
        winner = 'team1'
    else : 
        winner = 'nobody'
        end = False
    if turns_withoutattacks >= 200 :
        end = True  
        winner = 'tie'
    return winner, end  

def outside_map(board, position) :
    """checks if the given position is inside or outside the map 
    Parameters :
    -----------
    board : the map (list)
    position : the coordinates you want to check (list)
    
    Returns :
    ---------
    isItOutside : True if the coordinates are outside the map, False otherwise (bool)

    Versions :
    ----------
    spécification : Louis Bomal (v1 : 09/03/2023)
    implémentation : Louis Bomal (v1 : 09/03/2023)
    """
    isItOutside =  False
    if (position[0] > len(board[1])-1 or position[0] < 0) or (position[1] > len(board)-1 or position[1] < 0):
        isItOutside = True
    return isItOutside

def map_creator(path) :
    """Returns a list standing for the map data(state of the game) 
    
    Parameters :
    ------------
    path : path of the .ght file with the map info (str) 
    
    Returns :
    ---------
    map : final list standing for the board (list)

    Version :
    ---------
    spécification : Louis Bomal (v1 : 16/02/2023)    
    implémentation : Louis Bomal (v1 : 28/02/2023)
                                 (v2 : 09/03/2023)
    """
    
    map_data = open('%s' % path, 'r')
    map_data = map_data.readlines()   
     
    #gets the length and width of the map
    map_length = int(map_data[1][0:2])
    map_width = int(map_data[1][3:5])
    
    spawn_point1 = []
    spawn_point2 = []
    #iniate the 2 spawnpoints of the ghosts
    spawn_point1.append(int(map_data[3][2]))
    spawn_point1.append(int(map_data[3][4]))
    spawn_point2.append(int(map_data[4][2:4]))
    spawn_point2.append(int(map_data[4][4:7]))

    mana_cases_list = []
    for magic_case in map_data[6:len(map_data)+1] :
        magic_case = magic_case.split(' ')
        for elements in range(0, len(magic_case)) :
            if elements == 2 :
                magic_case[elements] = magic_case[elements].strip('\n')
            if magic_case[elements] == '\n' :
                del magic_case[elements]
            else : 
                magic_case[elements] = int(magic_case[elements])
        mana_cases_list.append(magic_case)
    
    #create the list of list of dictionaries (the map)
    map = []
    for vertical_cases in range(0, map_width) :
        map.append([])
        for horizontal_cases in range(0, map_length) : 
            map[vertical_cases].append({})
            map[vertical_cases][horizontal_cases]['ghost'] = False
            map[vertical_cases][horizontal_cases]['raw_mana'] = 0
            map[vertical_cases][horizontal_cases]['spawnpoint'] = False
        
    for mana_case in mana_cases_list :
        map[mana_case[1]-1][mana_case[0]-1]['raw_mana'] += mana_case[2]
            
    map[spawn_point1[1]-1][spawn_point1[0]-1]['spawnpoint'] = 1
    map[spawn_point2[1]-1][spawn_point2[0]-1]['spawnpoint'] = 2
    map[spawn_point1[1]-1][spawn_point1[0]-1]['ghost'] = {'HP':100, 'team':1}
    map[spawn_point2[1]-1][spawn_point2[0]-1]['ghost'] = {'HP':100, 'team':2}
    return map

def display_map(board) :
    """displays the map on the terminal
    
    Parameters :
    ------------
    board : the current state board (list)
    
    Versions :
    ----------
    spécification : Louis Bomal (v1 : 21/02/2023)
    implémentation : Louis Bomal (v1 : 27/02/2023)
                                 (v2 : 25/03/2023)
    """
    
    print(term.clear + term.on_gray1('  '), end='')
    #creates the first lines with the numbers of the columns
    for lines in range(0, len(board[0])) : 
        number = '%s' % lines
        if len(number) == 1 :
            print(term.on_gray1('  %s ' % (lines+1)), end='')
        else : 
            print(term.on_gray1(' %s '  % (lines+1)), end='')

    vertical_index = 1
    print('\n', end='')
    for lines in range(0, len(board)) : 
        print(term.on_gray1('  '),end='')

        #takes the number of lines (number of vertical cases)
        for pattern in range(0,len(board[0])) : 
            #repeats x times the +--- pattern to create a horizontal line (x being the number of horizontal cases)
            print(term.on_gray1('+---'),end='')    
        print(term.on_gray1('+\n'), end='')

        #adds the vertical numbers of every cases and adds a space if the number is only one character long
        if len('%i'%vertical_index) == 2 :
            print(term.on_gray1('%i' % vertical_index), end= '')
        else : 
            print(term.on_gray1('%i ' % vertical_index), end = '')

        #increments vertical_index for the next line
        vertical_index +=1
        for columns in range(0, len(board[lines])) :
            #"elements in lines" stands for the number of elements in the map_data
            #1 if case is occupied by a ghost (temporary value)
            if board[lines][columns]['ghost'] != False :
                print('|', end = '')
                if board[lines][columns]['ghost']['team'] == 1 :
                    print(term.on_darkgreen('👻 '), end ='')
                else : 
                    print(term.on_crimson('👻 '), end ='')
            #2 if case is mana
            elif board[lines][columns]['raw_mana'] != 0 :
                print(term.on_gray1('|'), end = '')
                if board[lines][columns]['raw_mana'] == 500 :
                    print(term.on_navy('   '), end = '') 
                elif board[lines][columns]['raw_mana'] == 100 :
                    print(term.on_blue3('   '), end = '') 
                elif board[lines][columns]['raw_mana'] == 50 :
                    print(term.on_blue('   '), end = '') 
                elif board[lines][columns]['raw_mana'] == 30 :
                    print(term.on_royalblue('   '), end = '') 
                else :
                    print(term.on_skyblue1('   '), end = '')
            #3 if case is one of the spawn point
            elif board[lines][columns]['spawnpoint'] == 2 or board[lines][columns]['spawnpoint'] == 1 :
                print(term.on_gray1('|'), end = '')
                if board[lines][columns]['spawnpoint'] == 2 :
                    print(term.on_crimson(' 📍'), end = '')
                elif board[lines][columns]['spawnpoint'] == 1 :
                    print(term.on_darkgreen(' 📍'), end = '')
            #empty case
            else : 
                print(term.on_gray1('|   '), end = '')
        #adds the \n and the last |
        print('|\n', end = '')

    #this part forms the last line that closes the board from below
    last_line = '  '
    for pattern in range(0, len(board[0])) :
        last_line += '+---'
    last_line += '+'

    print(term.on_gray1(last_line))

def ghost_attack(board, ghost_coord, target_coord, player_mana, team) :
    """attacks on a specified case of the board
    
    Parameters :
    ------------
    board : the current state of the board (list)
    ghost_coord : coordinate of the ghost from where it will attack (list)
    target_coord :target that the ghost attacks (list)
    player_mana : mana of the player who attacks (int)
    team : which team ask for the order (int)

    Returns :
    ------------
    board : the new state of the board after the ghost attack (list)
    player_mana : mana of the player after his attack (int)
    is_there_an_attack : True if a ghost succesfully attacked (bool)

    Versions :
    ---------
    spécification : Thomas Busoni (V1 : 16/02/2023)
                                  (V2 : 09/03/2023)
    implémentation : Thomas Busoni (V1 : 09/03/2023)
                                   (v2 : 20/03/2023)
    """
    #decreases by one to fit the list index format
    ghost_coord[0] -= 1
    ghost_coord[1] -= 1
    target_coord[0] -= 1
    target_coord[1] -= 1

    is_there_an_attack = False
    #checks if the ghost and the target are not outside the board
    if not outside_map(board, ghost_coord) and not outside_map(board, target_coord):
        #checks if the attack is not out of range
        if isInRange(ghost_coord, target_coord):
        #checks if the ghost and the target are not outside the board
            #checks if there is a allied ghost that can attack or if the ghost is in the right team
            if occupied_place(board, ghost_coord) and board[ghost_coord[1]][ghost_coord[0]]['ghost']['team'] == team :
                if occupied_place(board, target_coord) :                                    
                    #execute the order
                    board[target_coord[1]][target_coord[0]]['ghost']['HP'] -= 10
                    player_mana += 10 
                    is_there_an_attack = True
                    #kills the ghost if under or equal 0HP         
                    if board[target_coord[1]][target_coord[0]]['ghost']['HP'] <= 0 :
                        board[target_coord[1]][target_coord[0]]['ghost'] = False      
    return board, player_mana, is_there_an_attack, target_coord, ghost_coord

def spawn_ghost(board, team, player_mana) :
    """Summons a ghost on the spawn point of the map, fails if case already occupied

    Parameters :
    ------------
    board : the current state of the board (list)
    team : which team wants to summmon a ghost (int)
    player_mana : mana of the player (int)
    
    Returns :
    ---------
    board : the new state of the board after the ghost has been summoned (list)
    player_mana : the mana of the player (int)
    
    Version :
    ---------
    spécification : Thomas Busoni (V1 : 16/02/2023)
                                  (V2 : 09/03/2023)
    implémentation : Julian Courtois (V1 : 09/03/2023)
                                     (V2 : 20/03/2023)
                                     (V3 : 25/03/2023)
    """
    for y in range(0, len(board)) : 
        for x in range(0, len(board[y])) :
            #checks for the right spawn point
            if board[y][x]['spawnpoint'] == team :
                #checks if the case is occupied
                if occupied_place(board, [x,y]) == False :
                    board[y][x]['ghost'] = {'HP': 100, 'team':team}
                    player_mana -= 300
    return board, player_mana

def heal(ghost_coord, board, player_mana, team, amount):
    """Heals the ghost for a certain amount of mana

    Parameters :
    ----------
    ghost_coord : where you want to cast your heal (list)
    player_mana : the current mana of the player before spending for the heal (int)
    board : the current state of the board (list)
    team : which team wants to heal a ghost (int)
    amount : how much you want to heal your ghost (int)
    

    Returns:
    --------
    board : the new state of the board (list)
    player_mana : the new amount of mana of the player after spending for a heal spell (int)

    Version :
    ---------
    spécification : Benjamin Daels (v.1 16/02/23)
    implémentation : Benjamin Daels (v1 : 28/02/2023)
                                    (v2 : 09/03/2023)
    """
    #decreases to fit the list index format
    ghost_coord[0] -=1
    ghost_coord[1] -= 1
    #checks if the given coordinates aren't outside the map
    if not outside_map(board, ghost_coord):
        #checks if ghost on the case
        if occupied_place(board, ghost_coord) :
            #checks if the player has enough mana to cast his heal
            if amount*2 <= player_mana :
                if board[ghost_coord[1]][ghost_coord[0]]['ghost']['team'] == team :
                    #heals the ghost
                    board[ghost_coord[1]][ghost_coord[0]]['ghost']['HP'] += amount
                    player_mana -= 2*amount
                    if board[ghost_coord[1]][ghost_coord[0]]['ghost']['HP'] >= 100 : 
                        board[ghost_coord[1]][ghost_coord[0]]['ghost']['HP'] = 100 
    return board, player_mana


def move(board, current_position, new_position, team):
    """Allows the user to control de movements of the ghosts

    Parameters :
    ------------
    board : the current state of the board (list)
    current_position : current position of the ghost (list)
    new_position : new position of the ghost (list)
    team : which team plays (int)
    
    Returns :
    --------
    board : the new state of the board after the move of the ghost (list)
    
    Version :
    ---------
    spécification : Julian Courtois (V1:16/02/2023)
    implémentation : Julian Courtois (V1 : 09/03/2023)
                                     (V2 : 20/03/2023)
    """
    #decreases by one to fit the list index format
    new_position[0] -=1
    new_position[1] -= 1
    current_position[0] -= 1
    current_position[1] -= 1
    #checks if the current position of the ghost or his next position is out of the board (to avoid index troubles)
    if not outside_map(board, new_position) :         
        #checks if the move is not out of range
        if isInRange(current_position, new_position) :            
            #checks if there is a ghost that can move
            if occupied_place(board, current_position) :
                #checks if the case where you want it to move isn't occupied by another ghost or a spawn point
                if not occupied_place(board, new_position)and board[new_position[1]][new_position[0]]['spawnpoint'] == False :
                    #the ghost moves if its in the right team
                    if board[current_position[1]][current_position[0]]['ghost']['team'] == team :
                        board[new_position[1]][new_position[0]]['ghost'] = board[current_position[1]][current_position[0]]['ghost']
                        board[current_position[1]][current_position[0]]['ghost'] = False                

    return board


def mana_collect(board, current_mana, current_position, team):
    """Returns the new mana of the player after passing on a mana case and collecting it
    
    Parameters :
    ------------
    board : the current state of the board (list)
    current_mana : current points of mana of the player (int)
    current_position : the coordinates of the ghost (list)
    team : which team wants to collect (int)

    Returns :
    ---------
    new_mana : new amount of mana of the player (int)
    board : new state of the board (without the case of mana that has been collected) (list)  

    Version :
    ---------
    spécification : Julian Courtois (v1:16/02/23)
    implémentation : Benjamin Daels (v1 :09/03/23)
    """
    current_position[0] -= 1
    current_position[1] -= 1
    new_mana = current_mana
    #check if the mana is on the case
    if board[current_position[1]][current_position[0]]['raw_mana']!=0 :
        #check if a ghost is on the case 
        if occupied_place(board, current_position) :
            #check if the ghost is in the right team
            if board[current_position[1]][current_position[0]]['ghost']['team'] == team :
                new_mana += board[current_position[1]][current_position[0]]['raw_mana']
                board[current_position[1]][current_position[0]]['raw_mana'] = 0
    return board, new_mana

def order_information_dico(order) :
    """Returns a dictionary with information about an order depending on the type of order received

    Parameters :
    ------------
    order : order received (str)

    Returns :
    --------
    information : dictionary with the info about the order (dict)

    Version :
    spécification : Benjamin Daels (v1:27/02/2023)
    implémentation : Benjamin Daels (v1:27/02/2023)
    """
    #order = '02-02:x03-03'
    information = {}
    order = order.split(':')
    #order = ['02-02','x03-03']
    order_list = order[0].split('-')
    #order_list = ['02','02']
    information['current_position'] = [int(order_list[0]), int(order_list[1])]
    if '+' in order[1] :
        amount = order[1].strip('+')
        information['amount'] = int(amount)  
    elif '@' in order[1] : 
        coord_list = order[1].split('-')
        coord_list[0] = coord_list[0].strip('@')
        information['new_position'] = [int(coord_list[0]), int(coord_list[1])]
    elif 'x' in order[1] : 
        coord_list2 = order[1].split('-')
        coord_list2[0] = coord_list2[0].strip('x')
        information['target_position'] = [int(coord_list2[0]), int(coord_list2[1])]
    return information 

def translator(order) :
    """returns all the information from the specified order

    Parameters :
    ------------
    order : order given by the player (str)

    Returns : 
    ---------
    attack_orders : list of all the attack orders given by the player (list) 
    heal_orders : list of all the heal orders given by the player (list)
    mana_collect_orders : list of all the mana collect orders given by the player (list)
    move_orders : list of all the move orders given by the player (list)
    spawn_ghost : True if the player orders to summon an ghost, False otherwise (bool)

    Version :
    ---------
    spécification : Louis BOMAL (v1: 23-02-23)
    implémentation : Louis BOMAL (v1 : 27/02/2023)
                                 (v2 : 02/03/2023)
    """
    #creates a list with all the "words" in the original string around the spaces characters
    order_list = order.split(' ')
    for orders in range(0,len(order_list)) :
        if order_list[orders] == '' :
            del order_list[orders]
    spawn_ghost = False
    heal_orders = []
    move_orders = []
    mana_collect_orders = []
    attack_orders = []
    
    #seeks a special character in all the orders of the string to determine their goal
    for orders in order_list :
        if 'ghost' in orders :
            spawn_ghost = True
        #sort the orders in those 4 lists 
        elif '+' in orders or '$' in orders or'@' in orders or'x' in orders :
            thedico = order_information_dico(orders)
            if 'x' in orders :
                    attack_orders.append(thedico)
            elif '@' in orders :
                    move_orders.append(thedico)
            
            elif '+' in  orders :
                    heal_orders.append(thedico)
            
            elif '$' in orders :
                mana_collect_orders.append(thedico)

    return attack_orders,heal_orders,mana_collect_orders,move_orders,spawn_ghost 

#AI related functions
#actual new functions for the IA
def strat(board, team) :
    """Returns one of the two designed strategies but also the number of ghosts of each team
    
    Parameters :
    ------------
    board : the current state of the board (list)
    team : team of the IA (int)

    Returns :
    ---------
    strategy : chosen strategy (str)
    allied_ghosts : number of allied ghosts (int)
    other_ghosts : number of enemy ghosts (int)

    Versions : 
    ----------
    spécification :
    implémentation :
    """
    allied_ghosts = 0
    other_ghosts = 0

    for lines in range(0, len(board)) : 
        for columns in range(0, len(board[lines])) :
            if occupied_place(board, [columns, lines]) != False :
                if board[lines][columns]['ghost']['team'] == team :
                    allied_ghosts += 1
                else : 
                    other_ghosts += 1

    if allied_ghosts >= other_ghosts :
        strategy = 'assault'
    else :
        strategy = 'retreat'
    return strategy, allied_ghosts, other_ghosts

def go_to_there(current_position, target_location) :
    """returns the next coordinates to got to in order to go to the new_position (can take multiple orders long)
    
    Parameters :
    -----------
    current_position : the current position of the ghost you want to move (list)
    target_location : the coordinates of the place you want to go (list)
    
    Returns :
    ---------
    next_coord : the coordinates of the next move (list)

    Versions :
    ----------
    specification : Louis BOMAL (v1 : 19-04-2023)    
    implémentation : Louis BOMAL (v2 : 19-04-2023)
    """
    next_coord = []
    #sets the next x position
    if current_position[0] < target_location[0] :
        next_coord.append(current_position[0]+1)
    elif current_position[0] > target_location[0] :
        next_coord.append(current_position[0]-1)
    else : 
        next_coord.append(current_position[0])

    #sets the next y position
    if current_position[1] < target_location[1] :
        next_coord.append(current_position[1]+1)
    elif current_position[1] > target_location[1] :
        next_coord.append(current_position[1]-1)
    else : 
        next_coord.append(current_position[1])
    
    return next_coord

def go_to_mana(board, team, spawn_coord) :
    """returns the movement orders that head towards mana cases

    Parameters :
    -----------
    board : the current state of the board (list)
    team : the team of the AI (int)
    spawn_coord : the coord of the spawnpoint of the AI team (list)

    Returns :
    ---------
    board : the new state of the board (list)
    orders : the movement orders (str)

    Versions :
    ----------
    specification :
    implémentation :
    """
    #checks the case where there's mana and put them in a list
    orders = ''
    mana_list = []
    for lines in range(0, len(board)) : 
        for columns in range(0, len(board[lines])) :
            if board[lines][columns]['raw_mana'] != 0 :
                if occupied_place(board, [columns, lines]) == False :
                    mana_list.append([board[lines][columns], columns, lines])
                    #returns False to tell that there are no reasons to go on using the rest of this function
    if len(mana_list) == 0 :                     
        return board, orders                                    
    mana = 0              
    for manaCases in range(0, len(mana_list)) :
        #if the cases have the same amount of mana, go to the least far away one
        if mana_list[manaCases][0]['raw_mana'] == mana :
            #gets the first distance
            x_diff = spawn_coord[0] - previous_coord[0]
            y_diff = spawn_coord[1] - previous_coord[1]
            if x_diff < 0 :
                x_diff = -x_diff
            if y_diff < 0 :
                y_diff = -y_diff
            global_diff_previous = x_diff + y_diff
            #gets the second distance
            x_diff2 = spawn_coord[0] - mana_list[manaCases][1]
            y_diff2 = spawn_coord[1] - mana_list[manaCases][2]
            if x_diff2 < 0:
                x_diff2 = -x_diff2
            if y_diff2 < 0 :
                y_diff2 = -y_diff2
            global_diff_current = x_diff2 + y_diff2
            #take the least far away coord
            if global_diff_current < global_diff_previous:
                mostmana_coord = [mana_list[manaCases][1], mana_list[manaCases][2]]
            previous_coord = [mana_list[manaCases][1],mana_list[manaCases][2]]
        elif mana_list[manaCases][0]['raw_mana'] > mana:
            mana = mana_list[manaCases][0]['raw_mana']
            mostmana_coord = [mana_list[manaCases][1], mana_list[manaCases][2]]
            previous_coord = [mana_list[manaCases][1],mana_list[manaCases][2]]
        
        
    #writes the actual orders to get to the mana case as soon as possible (with the most optimized way)
    for lines in range(0, len(board)) : 
        for columns in range(0, len(board[lines])) :
            if board[lines][columns]['ghost'] != False :
                if board[lines][columns]['ghost']['team'] == team :
                    if board[lines][columns]['ghost']['order']== False :
                        next_pos = go_to_there([columns, lines], mostmana_coord)
                        #sets to True to tell that the ghost has already executed an order
                        board[lines][columns]['ghost']['order'] = True
                        orders += '%s-%s:@%s-%s ' % (columns+1, lines+1, next_pos[0]+1, next_pos[1]+1)           
    return board, orders

def heal_orders(board, team, AI_mana) :
    """Returns heal orders 

    Parameters :
    ------------
    board : the current state of the board (list)
    team : team of the AI (int)
    AI_mana : current mana of the AI (int)

    Returns :
    ---------
    orders : heal orders written by the AI (str)

    Versions :
    ----------
    spécification :
    implémentation :
    """
    orders = ''
    for lines in range(0, len(board)) :
        for columns in range(0, len(board[lines])) : 
            if occupied_place(board, [columns, lines]) :
                if board[lines][columns]['ghost']['team'] == team :
                    if board[lines][columns]['ghost']['HP'] <= 50 :
                        amount = 100 - board[lines][columns]['ghost']['HP']
                        if AI_mana >= amount :
                            orders += '%s-%s:+%s ' % (columns+1, lines+1, amount)
                            AI_mana -= amount
    return orders

def attack_orders(board, team, current_position) :
    """Returns the orders related to attacking enemies

    Parameters :
    ------------
    board : current state of the board (list)
    team : team of the AI (int)
    current_position : current position of the ally ghost (list)

    Returns : 
    ---------
    board : new state of the board (list)
    order : order written by the function (str)

    Versions :
    ----------
    spécification :
    implémentation :
    """
    order = ''
    ghost_list = []

    for lines in range(0, len(board)) :
        for columns in range(0, len(board[lines])) :
            if occupied_place(board, [columns, lines]) :
                if board[lines][columns]['ghost']['team'] != team :
                    if isInRange(current_position, [columns, lines]) :
                        ghost_list.append([columns, lines, board[lines][columns]['ghost']['HP']])
    #if no ghost in range, return ''                
    if len(ghost_list) == 0 :
        return board, order          
                  
    most_low_hp_ghost_coord = [0,0]
    previous_hp = 100
    for ghost in range(0, len(ghost_list)) :
        if ghost_list[ghost][2] <= previous_hp :
            previous_hp = ghost_list[ghost][2]
            most_low_hp_ghost_coord[0] = ghost_list[ghost][0]
            most_low_hp_ghost_coord[1] = ghost_list[ghost][1]

    #checks if the ally ghost has already been attributed an order
    if board[current_position[1]][current_position[0]]['ghost']['order'] == False :  
        order += '%s-%s:x%s-%s ' % (current_position[0]+1, current_position[1]+1, most_low_hp_ghost_coord[0]+1, most_low_hp_ghost_coord[1]+1)
        board[current_position[1]][current_position[0]]['ghost']['order'] = True

    return board, order

def assault(board, team) :
    """Returns orders of the assault phase
    
    Parameters : 
    -----------
    board : current state of the board (list)
    team : team of the AI (int)
    
    Returns :
    ---------
    board : new state of the board (list)
    orders : orders written by the function (str)
    
    Versions :
    ---------
    spécification :
    implémentation : 
    """
    most_low_hp_ghost_coord = [0,0]
    previous_hp = 100
    orders = ''
    for lines in range(0, len(board)) :
        for columns in range(0, len(board[lines])) :
            if occupied_place(board, [columns, lines]) != False :
                if board[lines][columns]['ghost']['team'] != team : 
                    if board[lines][columns]['ghost']['HP'] <= previous_hp :
                        previous_hp = board[lines][columns]['ghost']['HP']
                        most_low_hp_ghost_coord[0] = columns 
                        most_low_hp_ghost_coord[1] = lines

    for lines in range(0, len(board)) :
        for columns in range(0, len(board[lines])) :
            if occupied_place(board, [columns, lines]) != False :
                if board[lines][columns]['ghost']['team'] == team :
                    #attacks if there's a ghost in range. If no ghost in range, go to the lowest HP one
                    board, attack_order = attack_orders(board, team, [columns, lines])
                    orders += attack_order
                    if board[lines][columns]['ghost']['order'] != True :
                        next_coord = go_to_there([columns, lines], most_low_hp_ghost_coord)
                        orders += '%s-%s:@%s-%s ' % (columns+1, lines+1, next_coord[0]+1, next_coord[1]+1)
                        board[lines][columns]['ghost']['order'] = True
    return board, orders

def retreat(board, team, spawn_coord) :
    """Returns the orders of the retreat phase
    
    Parameters :
    ------------
    board : current state of the board (list)
    team : team of the AI (int)
    spawn_coord : coordinates of the allied spawn point (list)

    Returns :
    ---------
    board : new state of the board (list)
    orders : orders written by the function (str)
    
    Versions :
    ----------
    spécification :
    implémentation :
    """

    orders = ''
    for lines in range(0, len(board)) :
        for columns in range(0, len(board[lines])) :
            if occupied_place(board, [columns, lines]) != False :
                if board[lines][columns]['ghost']['team'] == team :
                    if board[lines][columns]['ghost']['order'] != True :
                        next_coord = go_to_there([columns,lines], spawn_coord)
                        #checks if there's a ghost on the case where it wants to go (in order not to write a useless movement order)
                        if board[next_coord[1]][next_coord[0]]['ghost'] == False :
                            orders += '%s-%s:@%s-%s ' % (columns, lines, next_coord[0], next_coord[1])
                            board[lines][columns]['ghost']['order'] = True
                        if board[lines][columns]['ghost']['order'] == False :
                            board, attack_orders_var = attack_orders(board, team, [columns, lines])
                            orders += attack_orders_var
                            board[lines][columns]['ghost']['order'] = True
    return board, orders

def ghost_spawn(board, team, AI_mana) :
    """Returns a ghost spawn order under specific conditions

    Parameters
    ----------
    board : current state of the board (list)
    team : team of the AI (int)
    AI_mana : current mana of the AI (int)

    Returns :
    ---------
    order : order written by the function (str)

    Versions :
    ----------
    spécification :
    implémentation :
    """
    order = ''
    #if mana >= 1000, always summon a ghost
    if AI_mana >= 1000 :
        order = 'ghost '
    #gets the number of ghosts of each team via the strat() function. If there are less than 3 more allied ghosts than enemy ghosts, summon one
    strategy, allied_ghost, other_ghost = strat(board, team)
    diff = allied_ghost - other_ghost
    if AI_mana >= 500 :
        if diff <= 2 :
            order = 'ghost '            
    return order


def IA(board, team, AI_mana) :
    """Returns a string of orders generated by an AI

    Parameters :
    ------------
    board : the state of the board (list)
    team : the team of the AI (int)
    AI_mana : the mana of the IA (int)

    Returns :
    ---------
    orders : the orders the AI gives (str)

    Versions :
    ---------
    specification : Louis Bomal (v1 : 30/03/2023)    
    implémentation : 
    """


    orders = ''

    orders += ghost_spawn(board, team, AI_mana) 
    #sets a new value in the dictionnary of the ghost to use later, meant to prevent the IA from ordering two things from the same ghost
    for lines in range(0, len(board)) : 
        for columns in range(0, len(board[lines])) :
            if board[lines][columns]['spawnpoint'] == team :
                spawn_coord = [columns, lines]
            if occupied_place(board, [columns, lines]) != False :
                if board[lines][columns]['ghost']['team'] == team :
                    board[lines][columns]['ghost']['order'] = False
                    #write mana gathering orders if a ghost is on a case of mana
                    if board[lines][columns]['raw_mana'] != 0 :
                        orders += '%s-%s:$ ' % (columns+1, lines+1)
                        board[lines][columns]['ghost']['order'] = True
                        board[lines][columns]['raw_mana'] = 0

    board, mana_orders = go_to_mana(board, team, spawn_coord)
    orders += mana_orders

    #if there aren't any mana related orders left, go to the second phase (attack and defense)
    if mana_orders != '' :
        return orders
    
    #Enters in assault phase if allied ghost > enemy ghosts, in retreat phase otherwise
    strategy, allied_ghosts, other_ghosts = strat(board, team)
    
    if strategy == 'assault' :
        board, assault_orders = assault(board, team)
        orders += assault_orders
    else :
        board, retreat_orders = retreat(board, team, spawn_coord)
        orders += retreat_orders
    
    heal_orders_var = heal_orders(board, team, AI_mana)
    orders += heal_orders_var

    return orders



# main function
def play_game(map_path, group_1, type_1, group_2, type_2):
    """Play a game.
    
    Parameters
    ----------
    map_path: path of map file (str)
    group_1: group of player 1 (int)
    type_1: type of player 1 (str)
    group_2: group of player 2 (int)
    type_2: type of player 2 (str)
    
    Notes
    -----
    Player type is either 'human', 'AI' or 'remote'.
    
    If there is an external referee, set group id to 0 for remote player.

    Versions :
    ---------
    implémentation : Louis Bomal (v1 : 20/03/2023)
                                 (v2 : 25/03/2023)
    """
    #creates the initial state of the map according to the given file
    board = map_creator(map_path)

    playing_team = 1
    turn = 1
    end = False
    team1_mana = 500
    team2_mana = 500
    turns_without_attacks = 0

    #loop of the game
    while not end:
        #display the map
        display_map(board)
        print(' ')
        print('Tour %i :'% turn)
        print(term.bold_darkgreen('Le groupe %i a encore %i points de mana' %(group_1, team1_mana)))
        print(term.bold_crimson('Le groupe %i a encore %i points de mana' %(group_2, team2_mana)))

        #gets the orders
        if playing_team == 1:
            if type_1 == 'AI' :
                order_string = IA(board, 1, team1_mana)
            else :
                order_string = input('Tour du groupe %i : Entrez vos ordres : '% group_1)
        else : 
            if type_2 == 'AI' :
                order_string = IA(board, 2, team2_mana)
            else : 
                order_string = input('Tour du groupe %i : Entrez vos ordres : '% group_2)

        attack_orders, heal_orders, mana_collect_orders, move_orders, var_spawn_ghost = translator(order_string)
        is_there_an_attack = False

        
        #execute the 6 phase for the playing team
        if playing_team == 1 :
            #phase 1 : ghost spawn
            if var_spawn_ghost :                        
                if team1_mana >= 300 :  
                    board, team1_mana = spawn_ghost(board, playing_team, team1_mana)        
            #phase 2 : heal  
            for orders in range(0, len(heal_orders)) :
                board, team1_mana = heal(heal_orders[orders]['current_position'], board, team1_mana, playing_team, heal_orders[orders]['amount'])
            #phase 3 : mana collect
            for orders in range(0, len(mana_collect_orders)) :
                board, team1_mana = mana_collect(board, team1_mana, mana_collect_orders[orders]['current_position'], playing_team)
            #phase 4 : ghost fights
            for orders in range(0, len(attack_orders)) :
                board, team1_mana, is_there_an_attack, target_coord, ghost_coord = ghost_attack(board, attack_orders[orders]['current_position'], attack_orders[orders]['target_position'], team1_mana, playing_team)
            #phase 5 : moves
            for orders in range(0, len(move_orders)) :
                board = move(board, move_orders[orders]['current_position'], move_orders[orders]['new_position'], playing_team)
            #phase 6 : automatic mana regen
            team1_mana += 10
        else :
            if var_spawn_ghost :                        
                if team2_mana >= 300 :  
                    board, team2_mana = spawn_ghost(board, playing_team, team2_mana)               
            #phase 2 : heal 
            for orders in range(0, len(heal_orders)) :
                board, team2_mana = heal(heal_orders[orders]['current_position'], board, team2_mana, playing_team, heal_orders[orders]['amount'])
            #phase 3 : mana collect
            for orders in range(0, len(mana_collect_orders)) :
                board, team2_mana = mana_collect(board, team2_mana, mana_collect_orders[orders]['current_position'], playing_team)
            #phase 4 : ghost fights
            for orders in range(0, len(attack_orders)) :
                board, team2_mana, is_there_an_attack, target_coord, ghost_coord = ghost_attack(board, attack_orders[orders]['current_position'], attack_orders[orders]['target_position'], team2_mana, playing_team)
            #phase 5 : moves
            for orders in range(0, len(move_orders)) :
                board = move(board, move_orders[orders]['current_position'], move_orders[orders]['new_position'], playing_team)
            #phase 6 : automatic mana regen
            team2_mana += 10

        #increments the number of turns everytime the two teams give orders
        if playing_team == 1 :
            turn += 1

        #when the six phases , change the playing team to the other one
        if playing_team == 1 :
            playing_team = 2
        else :
            playing_team = 1
        #determine the number of turns without attacks
        if playing_team == 1 :
            if is_there_an_attack :
                turns_without_attacks = 0
            else :
                turns_without_attacks += 1

        winner, end = isGameFinished(board, turns_without_attacks)

        if winner == 'team1' :
            winner = group_1
        elif winner == 'team2' : 
            winner = group_2

        time.sleep(0.1)

    display_map(board)
    print(' ')
    print('Tour %i :'% turn)
    print(term.bold_darkgreen('Le groupe %i a encore %i points de mana' %(group_1, team1_mana)))
    print(term.bold_crimson('Le groupe %i a encore %i points de mana' %(group_2, team2_mana)))

    if winner == 'tie' :
        print(term.bold_green('La partie finit sur une égalité'))
    else :
        print(term.bold_green('Victoire du groupe %i (en %i tours)' % (winner, turn)))

play_game('./map.ght', 1, 'AI', 5, 'AI')