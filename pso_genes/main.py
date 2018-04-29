import numpy as np

from modules.Swarm import Swarm
from modules.DataHandler import DataHandler

TESTING = False

MAX_EPOCHS = 5 if TESTING else 50
NUM_GENES = 10 if TESTING else 150

# Params to tune
C1 = 2          # 1.49445
C2 = 2          # 1.49445
W = 0.4         # 0.729
VMIN = -4
VMAX = 4

PCA_INIT = False

PLOT_GENE_ACTIVITY = True

def main():
    data = DataHandler()
    data.load(NUM_GENES, PCA_INIT)

    #--- RUN ----------------------------------------------------------------------+
    swarm_params = {
        "num_agents"                : data.num_agents,
        "max_epochs"                : MAX_EPOCHS,
        "agent_params"                  : {
            "c1"                        : C1,
            "c2"                        : C2,
            "v_min"                     : VMIN,
            "v_max"                     : VMAX,
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
