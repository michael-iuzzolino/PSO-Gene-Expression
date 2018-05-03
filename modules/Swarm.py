import sys
import json
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns

from modules.Agent import Agent

class Swarm():
    def __init__(self, num_agents, max_epochs, agent_params, plot_gene_activity):
        print("Creating swarm with {} agents...".format(num_agents))
        self.num_agents = num_agents
        self.max_epochs = max_epochs
        self.plot_gene_activity = plot_gene_activity

        # Global best errors and positions
        self.best_global_error      = -1                     # best error for group
        self.best_global_position   = []                     # best position for group

        self.history = {
            "position"              : [],
            "error"                 : [],
            "feature_importance"    : [],
            "num_genes_active"      : [],
            "error_stats"           : []
        }

        self.final_results = None

        # Create the swarm
        self._init_swarm(agent_params)

    def _init_swarm(self, agent_params):
        self.swarm = [Agent(agent_i, **agent_params) for agent_i in range(self.num_agents)]

    def plot(self):
        cbar_plotted = False # Prevents multiple cbar prints
        try:
            while True:
                for history_i, (history, best_error_i, best_feature_importance) in enumerate(zip(self.history["position"], self.history["error"], self.history["feature_importance"])):
                    print("\n")
                    print("History {}".format(history_i+1))
                    print("Feature importances")
                    for key, val in best_feature_importance.items():
                        print("\t{} : {}".format(key, val))
                    print("\n")
                    print("\n")

                    history = history[:100].reshape(100, 1)

                    num_genes = history.shape[0]
                    num_cols = 10
                    num_rows = int(np.ceil(num_genes / float(num_cols)))
                    reshaped_global_positions = history.reshape(num_rows, num_cols)

                    gene_names = self.swarm[0].data.gene_name_list[:100]

                    reshaped_global_gene_names = np.array(gene_names).reshape(num_rows, num_cols)

                    plot_params = {
                        "cmap"          : ListedColormap(["#ffcccc", "#99ff99"]),
                        "linewidths"    : 1.5,
                        "annot"         : reshaped_global_gene_names if len(reshaped_global_gene_names) < 100 else None,
                        "fmt"           : '',
                        "cbar"          : False if cbar_plotted else True
                    }
                    ax = sns.heatmap(reshaped_global_positions, **plot_params)

                    if not cbar_plotted:
                        cbar = ax.collections[0].colorbar
                        cbar.set_ticks([0.25, 0.75])
                        cbar.set_ticklabels(["OFF", "ON"])
                        cbar_plotted = True

                    plt.title("Timestep: {} / {} \n Best Error: {:0.4f}".format(history_i+1, len(self.history["position"]), best_error_i))
                    plt.axis('off')
                    plt.pause(0.005)
                    plt.cla()

        except KeyboardInterrupt:
            print("Exiting")

    def run(self):

        # begin optimization loop
        for timestep_i in range(self.max_epochs):

            print("{} / {} -- Best Error: {}".format(timestep_i, self.max_epochs, self.best_global_error))

            # cycle through particles in swarm and evaluate fitness
            agent_errors = []
            for agent_i in self.swarm:
                agent_i.evaluate()

                agent_errors.append(agent_i.current_error)

                # determine if current particle is the best (globally)
                if (agent_i.current_error < self.best_global_error or self.best_global_error == -1) and agent_i.current_error > 0:
                    self.best_global_position = agent_i.current_position
                    self.best_global_error = float(agent_i.current_error)
                    self.best_global_feature_importances = agent_i.full_feature_importances

            swarm_error_stats_i = {
                "errors"    : agent_errors,
                "mean"      : np.mean(agent_errors),
                "std"       : np.std(agent_errors)
            }

            # Update agent positions and velocities
            for agent_i in self.swarm:
                agent_i.update_velocity(self.best_global_position)
                agent_i.update_position()

            # Store timestep global best
            self.history["error"].append(self.best_global_error)
            self.history["position"].append(self.best_global_position)
            self.history["feature_importance"].append(self.best_global_feature_importances)
            self.history["error_stats"].append(swarm_error_stats_i)
            self.history["num_genes_active"].append(self.best_global_position[self.best_global_position > 0].shape[0])

        # Save data
        write_data = {}
        for key, val in self.history.items():
            if key == "position":
                new_data = []
                for values_i in val:
                    new_data.append(list(values_i))

                write_data[key] = new_data
            else:
                write_data[key] = val

        with open("experiments/results_{}_agents.json".format(self.num_agents), "w") as outfile:
            json.dump(write_data, outfile)

        if self.plot_gene_activity:
            self.plot()

        # print final results
        print("\n\n")
        print("Finished PSO!")
        print('GLOBAL -- Best Error: {}'.format(self.best_global_error))
        print("Best positions: ")
        for gene_i, gene_state in enumerate(self.best_global_position):
            gene_name = self.swarm[0].data.gene_name_list[gene_i]
            gene_state_str = "on" if gene_state else "off"
            print("\t{:20s} : {:8s}".format(gene_name, gene_state_str))
