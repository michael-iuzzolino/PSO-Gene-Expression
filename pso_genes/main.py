import numpy as np

from modules.Swarm import Swarm
from modules.DataHandler import DataHandler

num_agents = 20
maxiter = 10
C1 = 1.49
C2 = 1.49
W = 0.25

DATA_LIMIT = 100

def main():
    data = DataHandler()
    data.load(DATA_LIMIT)

    #--- RUN ----------------------------------------------------------------------+
    swarm_params = {
        "num_agents"                : num_agents,
        "maxiter"                   : maxiter,
        "agent_params"                  : {
            "c1"                        : C1,
            "c2"                        : C2,
            "weight"                    : W,
            "data"                      : data
        }
    }

    pso_swarm = Swarm(**swarm_params)
    pso_swarm.run()
    #--- END ----------------------------------------------------------------------+

if __name__ == "__main__":
    main()
