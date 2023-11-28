import gurobipy as gp


def exercise_19_p1(): 
    # Setting up Gurobi environment. It silences the output messeges.
    # Not necessary, but just QoL thing.
    environment = gp.Env(empty = True)
    environment.setParam('OutputFlag', 0)
    environment.start()
    # Initializing the model
    p2_info_sets = ["i_root", "i1", "i2", "i3"]
    p1_sequences = [" ","A", "B", "C", "AD", "AE", "BF", "BG"]

    m = gp.Model("player_one", env=environment) 
    # Adding variable for the expected utility
    
    r = m.addVars(p1_sequences, lb=0, vtype=gp.GRB.CONTINUOUS, name="r")
    v = m.addVars(p2_info_sets, vtype=gp.GRB.CONTINUOUS, name="v")

    m.addConstr(r[" "] == 1, "Empty Sequence");
    m.addConstr(r["A"] + r["B"] + r["C"] == r[" "])
    m.addConstr(r["AD"] + r["AE"] == r["A"])
    m.addConstr(r["BF"] + r["BG"] == r["B"])

    m.addConstr(v["i_root"] <= v["i1"] + v["i2"])
    m.addConstr(v["i1"] <= r["AD"] * 4 + r["AE"] * 3 + r["BF"] * 0 + r["BG"] * 2)
    m.addConstr(v["i1"] <= r["AD"] * (-1) + r["AE"] * 1 + r["B"] * (-5))
    m.addConstr(v["i2"] <= r["C"] * 3)
    m.addConstr(v["i2"] <= r["C"] * 4)
    m.setObjective(v["i_root"], gp.GRB.MAXIMIZE)
    m.optimize()
    for (key, val) in v.items():
        print(key, val.X)
    for (key, val) in r.items():
        print(key, val.X)


def exercise_19_p2():
    # environment = gp.Env(empty = True)
    # environment.setParam('OutputFlag', 0)
    # environment.start()
    m = gp.Model("player_two") 
    # Initializing the model
    p1_info_sets = ["I1", "I2", "I3"]
    p2_sequences = [" ","a", "b", "c", "d"]
    r = m.addVars(p2_sequences, lb=0, vtype=gp.GRB.CONTINUOUS, name="r")
    v = m.addVars(p1_info_sets, vtype=gp.GRB.CONTINUOUS, name="v")

    m.addConstr(r[" "] == 1, "Empty Sequence");
    m.addConstr(r["a"] + r["b"] == r[" "])
    m.addConstr(r["c"] + r["d"] == r[" "])
    
    m.addConstr(v["I1"] >= v["I2"])
    m.addConstr(v["I1"] >= v["I3"] + r["b"] * (-5))
    m.addConstr(v["I1"] >= r["c"] * 3 + r["d"] * 4)
    m.addConstr(v["I2"] >= r["a"] * 4 + r["b"] * (-1))
    m.addConstr(v["I2"] >= r["a"] * 3 + r["b"] * (1))
    m.addConstr(v["I3"] >= r["a"] * 0 )
    m.addConstr(v["I3"] >= r["a"] * 2 )
    m.setObjective(v["I1"], gp.GRB.MINIMIZE)
    
    m.optimize()
    
    m.display()
    for (key, val) in v.items():
        print(key, val.X)
    for (key, val) in r.items():
        print(key, val.X)
    return m.ObjVal


def exercise_19_p2_primal():
    # environment = gp.Env(empty = True)
    # environment.setParam('OutputFlag', 0)
    # environment.start()
    m = gp.Model("player_two") 
    # Initializing the model
    p1_info_sets = ["I1", "I2", "I3"]
    p2_sequences = [" ","a", "b", "c", "d"]
    r = m.addVars(p2_sequences, lb=0, vtype=gp.GRB.CONTINUOUS, name="r")
    v = m.addVars(p1_info_sets,lb=-float('inf'), vtype=gp.GRB.CONTINUOUS, name="v")

    m.addConstr(r[" "] == 1, "Empty Sequence");
    m.addConstr(r["a"] + r["b"] == r[" "])
    m.addConstr(r["c"] + r["d"] == r[" "])
    
    m.addConstr(v["I1"] <= v["I2"])
    m.addConstr(v["I1"] <= v["I3"] +  r["b"] * (5))
    m.addConstr(v["I1"] <= r["c"] * (-3) + r["d"] * (-4))
    m.addConstr(v["I2"] <= r["a"] * (-4) + r["b"] * (1))
    m.addConstr(v["I2"] <= r["a"] * (-3) + r["b"] * (-1))
    m.addConstr(v["I3"] <= r["a"] * 0 )
    m.addConstr(v["I3"] <= r["a"] * (-2) )
    m.setObjective(v["I1"], gp.GRB.MAXIMIZE)
    
    m.optimize()    
    return m.ObjVal

def exercise_20_p1(): 
    # Setting up Gurobi environment. It silences the output messeges.
    # Not necessary, but just QoL thing.
    environment = gp.Env(empty = True)
    environment.setParam('OutputFlag', 0)
    environment.start()
    # Initializing the model
    p2_info_sets = ["i_root", "i1"]
    p1_sequences = [" ","A", "B", "C", "D", "CE", "CF"]

    m = gp.Model("player_one", env=environment) 
    # Adding variable for the expected utility
    
    r = m.addVars(7, lb=0, vtype=gp.GRB.CONTINUOUS, name="r")
    v = m.addVars(2, vtype=gp.GRB.CONTINUOUS, name="v")

    m.addConstr(r[0] == 1, "Empty Sequence");
    m.addConstr(r[1] + r[2]  == r[0])
    m.addConstr(r[3] + r[4] == r[0])
    m.addConstr(r[5] + r[6] == r[3])

    m.addConstr(v[0] <= v[1] + r[1] * 1 * (1/3) + r[4] * 2 * (2/3))
    m.addConstr(v[1] <= r[2] * 3 * (1/3) + r[3] * 2 * (2/3))
    m.addConstr(v[1] <= r[2] * (-2)* (1/3) + r[5] * 5*  (2/3) + r[6] * 0 * (2/3))
    m.setObjective(v[0], gp.GRB.MAXIMIZE)
    m.optimize()
    for ((key, val), p2_iset) in zip(v.items(), p2_info_sets):
        print(p2_iset, val.X)
    for ((key, val), p1_sequence) in zip(r.items(), p1_sequences):
        print(p1_sequence, val.X)


def exercise_20_p2():
    environment = gp.Env(empty = True)
    environment.setParam('OutputFlag', 0)
    environment.start()
    m = gp.Model("player_two", env=environment) 
    # Initializing the model
    p1_info_sets = ["I_root", "I1", "I2", "I3"]
    p2_sequences = [" ","a", "b"]
    r = m.addVars(3, lb=0, vtype=gp.GRB.CONTINUOUS, name="r")
    v = m.addVars(4, vtype=gp.GRB.CONTINUOUS, name="v")
    
    m.addConstr(r[0] == 1, "Empty Sequence");
    m.addConstr(r[1] + r[2] == r[0])
    
    m.addConstr(v[0] >= v[1] + v[2])
    m.addConstr(v[1] >= r[0] * 1 * (1/3))
    m.addConstr(v[1] >= r[1] * 3 * (1/3) + r[2] * (-2) * (1/3))
    m.addConstr(v[2] >= v[3] + r[1] * 2 * (2/3))
    m.addConstr(v[2] >= r[0] * 2 * (2/3))
    m.addConstr(v[3] >= r[2] * 5 * (2/3))
    m.addConstr(v[3] >= r[2] * 0 * (2/3))
    m.setObjective(v[0], gp.GRB.MINIMIZE)
    m.optimize()
    for ((key, val), p1_iset) in zip(v.items(), p1_info_sets):
        print(p1_iset, val.X)
    for ((key, val), p2_sequence) in zip(r.items(), p2_sequences):
        print(p2_sequence, val.X)


if __name__ == "__main__":
  #exercise_19_p1()
  exercise_19_p2()
  exercise_19_p2_primal()
#   exercise_20_p1()
#   exercise_20_p2()
#   player_two()