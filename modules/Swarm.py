import sys
import json
import numpy as np
import time

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

    def _save_data(self):
        write_data = {key : [list(values_i) for values_i in val] if key == "position" else val for key, val in self.history.items()}

        with open("experiments/results_{}_agents.json".format(self.num_agents), "w") as outfile:
            json.dump(write_data, outfile)

    def run(self):
        """
            PSO Algorithm here
        """
        # begin optimization loop
        for epoch_i in range(self.max_epochs):

            # cycle through particles in swarm and evaluate fitness
            agent_errors = []
            for agent_i in self.swarm:

                # Evaluate the agent
                agent_i.evaluate()

                # Update the agent errors
                agent_errors.append(agent_i.current_error)

                # determine if current particle is the best (globally)
                if (agent_i.current_error < self.best_global_error or self.best_global_error == -1) and agent_i.current_error > 0:
                    self.best_global_position = agent_i.current_position
                    self.best_global_error = float(agent_i.current_error)
                    self.best_global_feature_importances = agent_i.full_feature_importances

            swarm_error_stats_i = {
                "errors"        : agent_errors,
                "mean"          : np.mean(agent_errors),
                "std"           : np.std(agent_errors),
                "best_error"    : self.best_global_error
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

            # Update user with training info
            print("{} / {} -- Best Error: {}".format(epoch_i, self.max_epochs, self.best_global_error))

        # Save data
        self._save_data()
