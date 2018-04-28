import sys
import numpy as np
import time

from modules.Agent import Agent

class Swarm():
    def __init__(self, num_agents, maxiter, agent_params):

        self.num_agents = num_agents
        self.maxiter = maxiter

        # Global best errors and positions
        self.best_global_error      = -1                     # best error for group
        self.best_global_position   = []                     # best position for group

        # Create the swarm
        self._init_swarm(agent_params)

    def _init_swarm(self, agent_params):
        self.swarm = [Agent(agent_i, **agent_params) for agent_i in range(self.num_agents)]

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

        # print final results
        print("\n\n")
        print("Finished PSO!")
        print('GLOBAL -- Best Error: {}'.format(self.best_global_error))
        print("Best positions: ")
        for gene_i, gene_state in enumerate(self.best_global_position):
            gene_name = self.swarm[0].data.gene_list[gene_i]
            gene_state_str = "on" if gene_state else "off"
            print("{} : {}".format(gene_name, gene_state_str))
