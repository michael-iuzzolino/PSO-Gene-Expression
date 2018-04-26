import numpy as np

random_initial_position = lambda boundaries : [np.random.uniform(boundaries[0][0], boundaries[0][1]), np.random.uniform(boundaries[0][0], boundaries[0][1])]

class Swarm():
    def __init__(self, costFunc, bounds, num_agents, maxiter, c1, c2, weight, Agent):
        self.err_best_g = -1                   # best error for group
        self.pos_best_g = []                   # best position for group

        self.maxiter = maxiter
        self.cost_function = costFunc
        self.bounds = bounds

        # establish the swarm
        self.swarm = [Agent(random_initial_position(self.bounds), c1, c2, weight, i) for i in range(num_agents)]

        self.swarm_position_history = []

    def run(self):

        # begin optimization loop
        for _ in range(self.maxiter):
            # cycle through particles in swarm and evaluate fitness
            agent_histories_i = []
            for agent_i in self.swarm:
                agent_i.evaluate(self.cost_function)

                # determine if current particle is the best (globally)
                if agent_i.err_i < self.err_best_g or self.err_best_g == -1:
                    self.pos_best_g = list(agent_i.position_i)
                    self.err_best_g = float(agent_i.err_i)

                agent_histories_i.append({
                    "agent_id" : agent_i.id,
                    "position" : agent_i.position_i
                })

            # Update position history
            self.swarm_position_history.append(agent_histories_i)

            # cycle through swarm and update velocities and position
            for agent_i in self.swarm:
                agent_i.update_velocity(self.pos_best_g)
                agent_i.update_position(self.bounds)

        # print final results
        print('GLOBAL -- Best Position: {}, Best Error: {}'.format(self.pos_best_g, self.err_best_g))
