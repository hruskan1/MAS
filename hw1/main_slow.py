from cgt_bandits.nodes import ChanceNode, TerminalNode, PersonalNode
from cgt_bandits import export_efg
from cgt_bandits import export_dot
from enum import IntEnum
import pygambit
import itertools
import numpy as np
import sys
from typing import List,Tuple


class Player(IntEnum):
    PLAYER = 0
    BANDIT = 1


def define_game(maze:np.array, bandit_cnt, prob):
    # Describe the tree of possible playthroughs of the game based on the 
    # maze and the rules. Start with each node in a unique infoset, then 
    # consider the information the players have at each point and encode it.
    
    
    return place_bandits(maze,bandit_cnt,prob,0,[])

def place_bandits(maze,bandit_cnt,prob:float,gold:int=0,history=[]):
    # Bandit can take arbitrary subset of possible spaces
    info = tuple(history)
    infoset = hash(info)
    r,c = np.nonzero(maze == 'E')
    s = [(r[i],c[i]) for i in range(len(r))]
    subsets = frozenset(itertools. combinations(s, bandit_cnt))
    childrens = []
    actions = []
    for subset in subsets:
        action = ",".join([str(pos) for pos in subset])
        actions.append(action)
        childrens.append(build_player(maze,bandit_cnt,frozenset(subset),prob,gold,history+[action]))
    
       
    return PersonalNode(f"Bandits\n set locations", infoset, Player.BANDIT, childrens, actions)  
    

def build_player(maze,bandit_cnt:int,bandit_pos:Tuple,prob:float,gold:int=0,history=[]):
    # The information player know is the maze with current and obtained gold.
    # Encod the actual player position with S, all places where he was denote as # (he cannot return)
    player_history = tuple(history[1:])
    #player_history = tuple([(i,h) for i,h in enumerate(history[1:]) if h == 'fight' or h == 'let_go'])
    info = tuple([tuple(maze.reshape(-1).tolist()),gold,bandit_cnt,player_history]) #(Need to add results of fights with bandits)
    #info = tuple(history)
    infoset = hash(info) 
    
    childrens = []

    actions = []
    for action,result,grid_pos in get_feasible_actions_with_results(maze):
        actions.append(action)
        new_maze = maze.copy()
        new_maze[new_maze=='S'] = '#'
        new_maze[grid_pos[0],grid_pos[1]] = 'S'
        
        
        #print(f"{action=}\t{result=}\t{grid_pos[0],grid_pos[1]}\n{new_maze}")
       
        if result == '-': #can move
            childrens.append(build_player(new_maze,bandit_cnt,bandit_pos,prob,gold, history + [action])) 
        
        elif result == 'E': #Bandit (E mark ereased, but player can not return back)
            x,y = np.nonzero(new_maze=='S')
            
            if (x[0],y[0]) in bandit_pos:
                childrens.append(build_bandit(new_maze,bandit_cnt,bandit_pos,prob,gold,history + [action]))
            else:
                childrens.append(build_player(new_maze,bandit_cnt,bandit_pos,prob,gold, history + [action])) 
                
        elif result == 'G':
            childrens.append(build_player(new_maze,bandit_cnt,bandit_pos,prob,gold+1,history + [action]))
        
        elif result == 'D': #can end
            childrens.append(TerminalNode('Player escapes',[gold+2]))
        
    if len(actions) == 0: #no valid move
        childrens.append(TerminalNode('Player cannot move',[0]))
    debug_x,debug_y = np.nonzero(maze=='S')
    return PersonalNode(f"P: {debug_x[0],debug_y[0]}\n G: {gold}", infoset, Player.PLAYER, childrens, actions)


def build_bandit(maze,bandit_cnt:int,bandit_pos:tuple,prob:float,gold:int=0,history=[]):
    #TODO get infoset correctly - missing information about result of the outcome
    bandit_history = tuple([history[0]] + [h for h in history[1:] if h == 'fight' or h == 'let_go'])
    info = tuple([bandit_cnt,bandit_history,bandit_pos])
    infoset = hash(info)
    #print(f"{infoset=},{bandit_cnt=}\n{bandit_history}")
    
    actions =['fight','let_go']
    childrens = [build_fight(maze,bandit_cnt-1,bandit_pos,prob,gold,history+[actions[0]]),
                 build_player(maze,bandit_cnt-1,bandit_pos,prob,0,history+[actions[1]])]
    debug_x,debug_y = np.nonzero(maze=='S')
    return PersonalNode(f"Bandit\n{debug_x[0],debug_y[0]}",infoset,Player.BANDIT,childrens,actions)

def build_fight(maze,bandit_cnt,bandit_pos,prob:float,gold:int=0,history=[]):
    probs = [1-prob,prob]
    actions = ['player wins','player lose']
    childrens = [build_player(maze,bandit_cnt,bandit_pos,prob,gold,history+[actions[0]]),
                  TerminalNode('Player dies',[0])]
    return ChanceNode('Fight', childrens, actions, probs)
    

def get_feasible_actions_with_results(maze)->List[Tuple[str]]:
    r, c  = np.nonzero(maze=='S')
    feasible_actions_with_results = []
    # 4 neighbourhood   
    for action,dr in zip(['up','down'],[-1,1]):
        if maze[r + dr,c] != '#':
            
            feasible_actions_with_results.append([action,maze[r + dr,c][0],[r+dr,c]])
            
    for action,dc in zip(['left','right'],[-1,1]):
        if maze[r, c + dc] != '#':
            feasible_actions_with_results.append([action,maze[r,c + dc][0],[r,c+dc]])
    
    return feasible_actions_with_results
    
    

def read_maze(io):
    bandit_cnt, prob = np.fromstring(io.readline(), sep=' ')
    lines = [list(lin) for lin in map(str.strip, io.readlines()) if lin]
    maze = np.array(lines)

    return maze, int(bandit_cnt), prob


def draw_game(root, filename="out.pdf"):
    "You can use this to visualize your games."
    # File IO not allowed on BRUTE! GraphViz is required to render graphs.

    dot = export_dot.nodes_to_dot(root)
    dot.write_pdf(filename)


def game_value(efg):
    "You can use this to check the solution for small games."
    # Standard output on BRUTE must not contain debugging messages!

    equilibrium = pygambit.nash.enummixed_solve(efg, rational=False)
    print(equilibrium[0].payoff(efg.players[0]), file=sys.stderr)


if __name__ == '__main__':
    maze, bandit_cnt, prob = read_maze(sys.stdin)
    root = define_game(maze, bandit_cnt, prob)    

    # NOT on BRUTE!
    #draw_game(root,filename="miners.pdf")

    #efg = export_efg.nodes_to_efg(root)

    # NOT on BRUTE!
    #game_value(efg)

    # Print the efg representation.
    # Yes on BRUTE
    #print(repr(efg)) 
