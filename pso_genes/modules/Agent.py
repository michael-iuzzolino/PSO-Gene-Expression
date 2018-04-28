import numpy as np
from sklearn.ensemble import RandomForestRegressor

class Agent:
    def __init__(self, id, c1, c2, weight, data):
        self.id = id

        self.c1 = c1                    # cognative constant
        self.c2 = c2                    # social constant
        self.weight = weight            # Momentum
        self.data = data

        # Set dimensionality of space
        self.gene_dimensions = data.num_genes

        # Current Information
        self.current_position = []          # particle position
        self.current_velocity = []          # particle velocity
        self.current_error = -1             # error individual

        # Individual History
        self.best_position = []            # best position individual
        self.best_error = -1               # best error individual

        # Initialize position and velocity
        self._init_particle()

    def _init_particle(self):
        self.current_velocity = np.zeros(self.gene_dimensions)
        self.current_position = np.zeros(self.gene_dimensions)

        for gene_i in range(self.gene_dimensions):
            self.current_velocity[gene_i] = np.random.uniform(-1, 1)
            self.current_position[gene_i] = 1 if np.random.uniform() > 0.5 else 0


    def evaluate(self):
        self.current_error = 0

        # # DEBUGGING
        # print("Current Position")
        # print(self.current_position)
        # raw_input("")

        active_gene_indices = np.where(self.current_position == 1)

        if active_gene_indices[0].shape[0] == 0:
            self.current_error = 500

        else:
            X, y = self.data.get_expression_levels(active_gene_indices)

            self.random_forest = RandomForestRegressor(oob_score=True)
            self.random_forest.fit(X, y)
            self.current_error = self.random_forest.oob_score_

        # # DEBUGGING
        # print("Error: {}".format(self.current_error))
        # raw_input("")

        # check to see if the current position is an individual best
        if self.current_error < self.best_error or self.best_error == -1:
            self.best_position = self.current_position
            self.best_error = self.current_error

    def update_velocity(self, best_global_position):
        new_velocities = []
        for gene_i in range(self.gene_dimensions):
            r1 = np.random.random()
            r2 = np.random.random()

            # Velocity update based on agent best history
            cognitive_velocity  = self.c1 * r1 * (self.best_position[gene_i] - self.current_position[gene_i])

            # Velocity update based on global best history
            social_velocity     = self.c2 * r2 * (best_global_position[gene_i] - self.current_position[gene_i])

            # Set current velocity
            new_velocity_i = self.weight * self.current_velocity[gene_i] + cognitive_velocity + social_velocity

            new_velocities.append(new_velocity_i)

        self.current_velocity = new_velocities

    def _velocity_sigmoid(self, gene_i):
        return 1 / float(1 + np.exp(-self.current_velocity[gene_i]))

    def update_position(self):
        # Update current position
        for gene_i in range(self.gene_dimensions):
            self.current_position[gene_i] = 1 if self._velocity_sigmoid(gene_i) > np.random.uniform() else 0
