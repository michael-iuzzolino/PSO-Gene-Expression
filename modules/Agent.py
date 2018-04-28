import numpy as np

class Agent:
    def __init__(self, id, bounds, c1, c2, weight, objective):
        self.id = id
        self.objective = objective      # Objective Function
        self.weight = weight            # Momentum
        self.c1 = c1                    # cognative constant
        self.c2 = c2                    # social constant
        self.bounds = bounds

        # Set dimensionality of space
        self.dimensions = len(bounds)

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
        self.current_velocity = []
        self.current_position = []
        for dimension_i in range(self.dimensions):
            velocity_i = np.random.uniform(-1, 1)
            position_i = np.random.uniform(self.bounds[dimension_i][0], self.bounds[dimension_i][1])

            self.current_velocity.append(velocity_i)
            self.current_position.append(position_i)

    # evaluate current fitness
    def evaluate(self):
        self.current_error = 0
        for dimension_i in range(self.dimensions):
            self.current_error += self.objective(self.current_position[dimension_i])

        # check to see if the current position is an individual best
        if self.current_error < self.best_error or self.best_error == -1:
            self.best_position = self.current_position
            self.best_error = self.current_error

    # update new particle velocity
    def update_velocity(self, best_global_position):

        new_velocities = []
        for dimension_i in range(self.dimensions):
            r1 = np.random.random()
            r2 = np.random.random()

            # Velocity update based on agent best history
            cognitive_velocity  = self.c1 * r1 * (self.best_position[dimension_i] - self.current_position[dimension_i])

            # Velocity update based on global best history
            social_velocity     = self.c2 * r2 * (best_global_position[dimension_i] - self.current_position[dimension_i])

            # Set current velocity
            new_velocity_i = self.weight * self.current_velocity[dimension_i] + cognitive_velocity + social_velocity

            new_velocities.append(new_velocity_i)

        self.current_velocity = new_velocities

    # update the particle position based off new velocity updates
    def update_position(self):

        for dimension_i in range(self.dimensions):
            # Update current position
            self.current_position[dimension_i] += self.current_velocity[dimension_i]

            # Constrain position to bounds
            # -----------------------------------------
            # adjust maximum position if necessary
            if self.current_position[dimension_i] > self.bounds[dimension_i][1]:
                self.current_position[dimension_i] = self.bounds[dimension_i][1]

            # adjust minimum position if neseccary
            if self.current_position[dimension_i] < self.bounds[dimension_i][0]:
                self.current_position[dimension_i] = self.bounds[dimension_i][0]
            # -----------------------------------------
