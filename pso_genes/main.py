import numpy as np

from modules.Swarm import Swarm
from modules.DataHandler import DataHandler

num_agents = 100
maxiter = 20
C1 = 1.49
C2 = 1.49
W = 0.55

DATA_LIMIT = 1000
PCA_INIT = True

PLOT_GENE_ACTIVITY = True

def main():
    data = DataHandler()
    data.load(DATA_LIMIT, PCA_INIT, num_agents)

    #--- RUN ----------------------------------------------------------------------+
    swarm_params = {
        "num_agents"                : num_agents,
        "maxiter"                   : maxiter,
        "agent_params"                  : {
            "c1"                        : C1,
            "c2"                        : C2,
            "weight"                    : W,
            "data"                      : data,
            "init_type"                 : "pca" if PCA_INIT else "uniform_random"
        },
        "plot_gene_activity"            : PLOT_GENE_ACTIVITY
    }

    pso_swarm = Swarm(**swarm_params)
    pso_swarm.run()
    #--- END ----------------------------------------------------------------------+

if __name__ == "__main__":
    main()
