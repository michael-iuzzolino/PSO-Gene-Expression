#------------------------------------------------------------------------------+
#
#   Michael L. Iuzzolino
#   Adopted from Nathan A. Rooy
#   https://nathanrooy.github.io/posts/2016-08-17/simple-particle-swarm-optimization-with-python/
#
#------------------------------------------------------------------------------+

#--- IMPORT DEPENDENCIES ------------------------------------------------------+

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

from modules.Swarm import Swarm

#--- COST FUNCTION ------------------------------------------------------------+

# function we are attempting to optimize (minimize)
def objective_function(x):
    func = np.square(x)
    return np.sum(func)

#--- MAIN ---------------------------------------------------------------------+


def plot(history, maxiter, bounds):
    for time_i in range(maxiter):
        for agent_id, agent_vals in history.items():
            agent_vals = np.array(agent_vals)
            plt.scatter(agent_vals[time_i,0], agent_vals[time_i,1], label=agent_id)
        plt.legend()
        plt.title("Timestep: {}".format(time_i))
        plt.xlim(bounds[0])
        plt.ylim(bounds[1])
        plt.pause(0.5)
        plt.cla()

def main():
    C1 = 1                            # cognative constant
    C2 = 2                           # social constant
    WEIGHT = 0.5                       # constant inertia weight (how much to weigh the previous velocity)
    maxiter = 10
    num_agents = 5
    bounds = [(-100,100), (-100,100)]   # input bounds [(x1_min,x1_max),(x2_min,x2_max)...]

    #--- RUN ----------------------------------------------------------------------+
    swarm_params = {
        "costFunc"      : objective_function,
        "bounds"        : bounds,
        "num_agents"    : num_agents,
        "maxiter"       : maxiter,
        "c1"            : C1,
        "c2"            : C2,
        "weight"        : WEIGHT
    }

    pso_swarm = Swarm(**swarm_params)

    history = pso_swarm.swarm_position_history

    plot(history, maxiter, bounds)
    #--- END ----------------------------------------------------------------------+

if __name__ == "__main__":
    main()
