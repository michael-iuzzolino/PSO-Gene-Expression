import numpy as np
from sklearn.ensemble import RandomForestRegressor

class Agent:
    def __init__(self, id, c1, c2, v_min, v_max, weight, data):

        self.id = id                    # Set agent ID
        self.data = data                # Data Handler object

        # Hyper-parameters
        self.c1 = c1                    # cognative constant
        self.c2 = c2                    # social constant
        self.v_min = v_min              # Init v_min
        self.v_max = v_max              # Init v_max
        self.weight = weight            # Momentum

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
        # Initialize velocities
        self.current_velocity = np.zeros(self.gene_dimensions)
        for gene_i in range(self.gene_dimensions):
            self.current_velocity[gene_i] = np.random.uniform(self.v_min, self.v_max)

        # Initialize positions
        self.current_position = np.zeros(self.gene_dimensions)
        for gene_i in range(self.gene_dimensions):
            self.current_position[gene_i] = 1 if np.random.uniform() > 0.5 else 0

    def _calculate_feature_importances(self, active_gene_indices):

        # Initialize object to hold full dict of feature importances
        self.full_feature_importances = {}

        # Get the raw feature importances from the regressor
        self.feature_importances = self.random_forest.feature_importances_

        # Get the number of active genes for the agent; e.g., 10010   -> 2 active genes
        num_active_genes = active_gene_indices[0].shape[0]

        # Select the active gene names
        active_gene_names = np.array(self.data.gene_name_list)[active_gene_indices]

        # Gene importances
        # -----------------------------------------------------------------------------------------------
        gene_importances = { gene_name : self.feature_importances[gene_i] for gene_i, gene_name in enumerate(active_gene_names)}

        # Append to full feature importances
        for key, val in gene_importances.items():
            self.full_feature_importances[key] = val
        # -----------------------------------------------------------------------------------------------

        # Other importances
        # -----------------------------------------------------------------------------------------------
        other_importances = {}
        starting_index = num_active_genes
        for key, val in self.data.encoding_sizes.items():
            other_importances[key] = np.sum(self.feature_importances[starting_index:starting_index+val])
            starting_index += val

        # Append to full feature importances
        for key, val in other_importances.items():
            self.full_feature_importances[key] = val
        # -----------------------------------------------------------------------------------------------

    def evaluate(self):

        # Get the active gene indicies
        active_gene_indices = np.where(self.current_position == 1)

        # If all turned off, set error very high
        if active_gene_indices[0].shape[0] == 0:
            self.current_error = 500

        else:
            # Get X, y from data handler for active genes only
            X, y = self.data.get_expression_levels(active_gene_indices)

            # Instantiate random forest regressor
            self.random_forest = RandomForestRegressor(oob_score=True)

            # Fit the regressor
            self.random_forest.fit(X, y)

            # Obtain oob score
            self.current_error = self.random_forest.oob_score_

            # Get feature importances
            self._calculate_feature_importances(active_gene_indices)

        # Set beset position/besterror to current position/error for first iteration
        if self.best_error == -1:
            self.best_position = self.current_position
            self.best_error = self.current_error

        # Check to see if the current position is an individual best
        elif self.current_error < self.best_error and self.current_error > 0:
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
