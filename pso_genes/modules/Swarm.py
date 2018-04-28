import sys
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns

from modules.Agent import Agent

class Swarm():
    def __init__(self, num_agents, maxiter, agent_params, plot_gene_activity):

        self.num_agents = num_agents
        self.maxiter = maxiter
        self.plot_gene_activity = plot_gene_activity

        # Global best errors and positions
        self.best_global_error      = -1                     # best error for group
        self.best_global_position   = []                     # best position for group

        self.best_global_error_history = []
        self.best_global_position_history = []

        # Create the swarm
        self._init_swarm(agent_params)

    def _init_swarm(self, agent_params):
        self.swarm = [Agent(agent_i, **agent_params) for agent_i in range(self.num_agents)]

    def plot(self):
        try:
            while True:
                for history_i, (history, best_error_i) in enumerate(zip(self.best_global_position_history, self.best_global_error_history)):
                    num_genes = history.shape[0]
                    num_cols = 10
                    num_rows = int(np.ceil(num_genes / float(num_cols)))
                    reshaped_global_positions = history.reshape(num_rows, num_cols)

                    gene_names = np.array(self.swarm[0].data.gene_list)
                    reshaped_global_gene_names = gene_names.reshape(num_rows, num_cols)

                    plot_params = {
                        "cmap"          : ListedColormap(["#ffcccc", "#99ff99"]),
                        "linewidths"    : 1.5,
                        "annot"         : reshaped_global_gene_names,
                        "fmt"           : '',
                        "cbar"          : False
                    }
                    sns.heatmap(reshaped_global_positions, **plot_params)
                    plt.title("Timestep: {} / {} \n Best Error: {:0.4f}".format(history_i, len(self.best_global_position_history), best_error_i))
                    plt.axis('off')
                    plt.pause(1)
                    plt.cla()

        except KeyboardInterrupt:
            print("Exiting")

    def run(self):
        # begin optimization loop
        for timestep_i in range(self.maxiter):

            sys.stdout.write("\r{} / {} -- Best Error: {}".format(timestep_i, self.maxiter, self.best_global_error))
            sys.stdout.flush()

            # cycle through particles in swarm and evaluate fitness
            for agent_i in self.swarm:
                agent_i.evaluate()

                # determine if current particle is the best (globally)
                if agent_i.current_error < self.best_global_error or self.best_global_error == -1:
                    self.best_global_position = agent_i.current_position
                    self.best_global_error = float(agent_i.current_error)

            # Update agent positions and velocities
            for agent_i in self.swarm:
                agent_i.update_velocity(self.best_global_position)
                agent_i.update_position()

            # Store timestep global best
            self.best_global_error_history.append(self.best_global_error)
            self.best_global_position_history.append(self.best_global_position)

        if self.plot_gene_activity:
            self.plot()

        # print final results
        print("\n\n")
        print("Finished PSO!")
        print('GLOBAL -- Best Error: {}'.format(self.best_global_error))
        print("Best positions: ")
        for gene_i, gene_state in enumerate(self.best_global_position):
            gene_name = self.swarm[0].data.gene_list[gene_i]
            gene_state_str = "on" if gene_state else "off"
            print("\t{:20s} : {:8s}".format(gene_name, gene_state_str))
