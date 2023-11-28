import gurobipy as gp


def player_one(): 
    # Setting up Gurobi environment. It silences the output messeges.
    # Not necessary, but just QoL thing.
    environment = gp.Env(empty = True)
    environment.setParam('OutputFlag', 0)
    environment.start()
    # Initializing the model
    m = gp.Model("player_one", env=environment) 
    # Adding variable for the expected utility
    U = m.addVar(vtype=gp.GRB.CONTINUOUS, name="U")
    # Adding variables for the action probabilities
    p1 = m.addVar(lb=0, vtype=gp.GRB.CONTINUOUS, name="p1")
    p2 = m.addVar(lb=0, vtype=gp.GRB.CONTINUOUS, name="p2")
    p3 = m.addVar(lb=0, vtype=gp.GRB.CONTINUOUS, name="p3")
    # Adding constraings for the expected utility
    m.addConstr(p2 - p3 >= U, "c0")
    m.addConstr(-p1 + p3 >= U, "c1")
    # Adding probability distribution constraint
    m.addConstr(p1 + p2 + p3 == 1, "pc2")
    # Setting objective
    m.setObjective(U, gp.GRB.MAXIMIZE)
    # Solving the model
    m.optimize()
    # Printing the results
    print("Player 1")
    print("U:", U.X)
    print("p1:", p1.X)
    print("p2:", p2.X)
    print("p3:", p3.X)

def player_two():
    environment = gp.Env(empty = True)
    environment.setParam('OutputFlag', 0)
    environment.start()
    m = gp.Model("player_two", env=environment) 
    U = m.addVar(vtype=gp.GRB.CONTINUOUS, name="U")
    # Adding variables in a vectorized form, first argument is how many of variables to create
    p = m.addVars(2, lb=0, vtype=gp.GRB.CONTINUOUS, name="p")
    m.addConstr(-p[1] <= U, "c0")
    m.addConstr(p[0] <= U, "c1")
    m.addConstr(-p[0] + p[1] <= U, "c2")
    m.addConstr(p[0] + p[1] == 1, "pc2")
    m.setObjective(U, gp.GRB.MINIMIZE)
    m.optimize()
    print("Player 2")
    print("U:", U.X)
    print("p1:", p[0].X)
    print("p2:", p[1].X)

if __name__ == "__main__":
  player_one()
  player_two()