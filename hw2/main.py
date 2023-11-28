import sys
from collections import defaultdict 
from typing import List,Tuple

import contextlib
import pygambit
from cgt_bandits import import_efg
from cgt_bandits.nodes import ChanceNode, PersonalNode, TerminalNode

import pprint

import gurobipy as gp
from gurobipy import GRB

from enum import IntEnum
class Player(IntEnum):
    PLAYER = 0
    BANDIT = 1


def sqf(I, Sigma, A, seq, g):
    """The Sequence form linear program defined in terms of the parameters
    I, Sigma, A, seq, g for 2 player zero sum game.
    
    Args:
        I (Tuple[Set[str],Set[str])): Infosets of an (opposite) player. For each infoset a v value is computed 
        Sigma (Tuple[List[str],List[str]): A sequence of a player. For each sequence a r value is computed 
            (Assume each action is encoded as an char (ideally from ([a-z][A-Z])).
        A (callable | iterable): A mapping from I (infosets) to an powerset of actions (One literal of Sigma)
        seq (callable | iterable): A mapping from I (infosets) to a Sigma, which returns the sequence leading to the information set i
        g (deafualt dict): A mapping from all possible tuple of sequences to the utilities (for a given player)
        maximize: Should we maximize or minimize the sqf (Corresponds to scenario if player 1 or player 2 plays.)
    """
    environment = gp.Env(empty = True)
    environment.setParam('OutputFlag', 0)
    environment.start()
    m = gp.Model("SQF",env=environment)
    I1,i2 = (I[0],I[1])
    
    v = m.addVars(i2,lb=-float('inf'),ub=float('inf'), vtype=gp.GRB.CONTINUOUS, name="v") 
    r = m.addVars(Sigma, lb=0,ub=1, vtype=gp.GRB.CONTINUOUS, name="r")
        
    # constraints on R
    m.addConstr(r[(' ',)] == 1,name='{} sequence')    
    for my_infoset in I1:
        my_seq_prefix = seq[my_infoset]
        lhs = gp.quicksum([r[my_seq_prefix + tuple([a])] for a in A[my_infoset]])
        m.addConstr(lhs == r[my_seq_prefix],name=f'{my_infoset} sequence')
         
    # Constraints on eny infoset and action
    for eny_infoset in i2: 
        for a in A[eny_infoset]:
            s_eny = seq[eny_infoset] + tuple([a])
            lhs = gp.quicksum([v[j] for j in i2 if seq[j] == s_eny]) + gp.quicksum([g[(s,s_eny)]*r[s] for s in Sigma])
            m.addConstr(lhs >= v[eny_infoset],name=f"{eny_infoset}_{a}")
            
    # Objective
    obj = gp.quicksum([g[(s,(' ',))]*r[s] for s in Sigma]) + gp.quicksum([v[j] for j in i2 if seq[j] == (' ',)])
    m.setObjective(obj,GRB.MAXIMIZE)
    m.optimize()
    m.display()
    return m.ObjVal


def extract_parameters(root):
    """Converts an extensive form game into the SQF parameters:
    I, Sigma, A, seq, g."""

    # Implement this second. It does not matter how you implement the
    # parameters -- functions, classes, or dictionaries, anything will work.
    
    def _get_params(node,I:Tuple[set,set],sigma:Tuple[set,set],A:dict,seq:dict,g:defaultdict[(set,set) : int],current_seq:list=[(" ",0),(" ",1)],current_coef:float=1):
        
        if isinstance(node,ChanceNode):    
            for child,prob in zip(node.children,node.action_probs):
                _get_params(child,I,sigma,A,seq,g,current_seq,current_coef * float(prob))
                        
        elif isinstance(node,PersonalNode):
            action_names = []
            I[node.player].add(node.infoset) # Infoset
            player_seq = [c[0] for c in current_seq if c[1] == node.player]
            seq.update({node.infoset : tuple(player_seq)})
            
            for child,action in zip(node.children,node.action_names): 
                action = f'empty{node.infoset}' if action == '' else action + f'{node.infoset}'
                action_names.append(action)
                sigma[node.player].add(tuple(player_seq + [action]))
                _get_params(child,I,sigma,A,seq,g,current_seq + [(action,node.player)],current_coef)
            
            A.update({node.infoset : tuple(action_names)})
                
        elif isinstance(node,TerminalNode):
            player_key = tuple([c[0] for c in current_seq if c[1] == Player.PLAYER])
            bandit_key = tuple([c[0] for c in current_seq if c[1] == Player.BANDIT])
            g.update({ (player_key,bandit_key) : current_coef * float(node.payoffs[Player.PLAYER]),
                       (bandit_key,player_key) : current_coef * float(node.payoffs[Player.BANDIT])})
            
    I = (set(),set())
    sigma = (set([tuple(' ')]),set([tuple(' ')]))
    A = dict()
    seq = dict()
    g = defaultdict(lambda: 0)
    _get_params(root,I,sigma,A,seq,g)
    return I,sigma,A,seq,g


def payoff(efg_root):
    """Computes the value of the extensive form game"""

    I,sigma,A,seq,g = extract_parameters(efg_root)
    
    with contextlib.redirect_stdout(sys.stderr):
        v_player = sqf(*[I,sigma[0],A,seq,g])
        
        #J = [I[1],I[0]]
        #v_bandit = sqf(*[J,sigma[1],A,seq,g])

    return v_player


if __name__ == "__main__":
    efg = sys.stdin.read()
    game = pygambit.Game.parse_game(efg)
    root = import_efg.efg_to_nodes(game)
    ret = payoff(root)
    print(ret)
