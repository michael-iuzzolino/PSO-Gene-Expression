import numpy as np

class Agent:
    def __init__(self, x0, c1, c2, weight, i):
        self.id = i
        self.position_i = []          # particle position
        self.velocity_i = []          # particle velocity
        self.pos_best_i = []          # best position individual
        self.err_best_i = -1          # best error individual
        self.err_i = -1               # error individual

        self.num_dimensions = len(x0)

        self.weight = weight
        self.c1 = c1        # cognative constant
        self.c2 = c2        # social constant

        for i in range(self.num_dimensions):
            self.velocity_i.append(np.random.uniform(-1, 1))
            self.position_i.append(x0[i])

    # evaluate current fitness
    def evaluate(self, costFunc):
        self.err_i = costFunc(self.position_i)

        # check to see if the current position is an individual best
        if self.err_i < self.err_best_i or self.err_best_i==-1:
            self.pos_best_i=self.position_i
            self.err_best_i=self.err_i

    # update new particle velocity
    def update_velocity(self,pos_best_g):


        for dimension_i in range(self.num_dimensions):
            r1 = np.random.random()
            r2 = np.random.random()

            vel_cognitive = self.c1 * r1 * (self.pos_best_i[dimension_i] - self.position_i[dimension_i])
            vel_social = self.c2 * r2 * (pos_best_g[dimension_i] - self.position_i[dimension_i])
            self.velocity_i[dimension_i] = self.weight * self.velocity_i[dimension_i] + vel_cognitive + vel_social

    # update the particle position based off new velocity updates
    def update_position(self, bounds):
        for dimension_i in range(self.num_dimensions):
            self.position_i[dimension_i] = self.position_i[dimension_i] + self.velocity_i[dimension_i]

            # adjust maximum position if necessary
            if self.position_i[dimension_i] > bounds[dimension_i][1]:
                self.position_i[dimension_i] = bounds[dimension_i][1]

            # adjust minimum position if neseccary
            if self.position_i[dimension_i] < bounds[dimension_i][0]:
                self.position_i[dimension_i] = bounds[dimension_i][0]
