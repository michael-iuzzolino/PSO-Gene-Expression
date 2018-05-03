import numpy as np

from modules.config import *
from modules.Swarm import Swarm
from modules.DataHandler import DataHandler
from modules.Plotter import Plotter

def main():

    data_handler_params = {
        "data_dir"                  : DATA_PATH,
        "num_agents"                : NUM_AGENTS,
        "top_k_variable_genes"      : TOP_K_VARIABLE_GENES,
        "show_variability_plot"     : PLOT_GENE_VARIABILITY_ON_LOAD,
        "percentiles"               : PERCENTILES,
        "features"                  : FEATURES,
        "baseline_iterations"       : BASELINE_ITERATIONS,
        "num_subset_genes"          : NUM_SUBSET_GENES
    }

    data = DataHandler(**data_handler_params)

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
            "data"                      : data
        },
        "plot_gene_activity"            : PLOT_GENE_ACTIVITY
    }

    pso_swarm = Swarm(**swarm_params)
    pso_swarm.run()
    #--- END ----------------------------------------------------------------------+

    path = "results_5_agents.json"
    plotter = Plotter()
    plotter.plot_gene_activation_heatmap(pso_swarm.history, data.gene_name_list, data.baseline_error)
    plotter.data_analysis_plots(path)
if __name__ == "__main__":
    main()
