import numpy as np
import time

class Swarm():
    def __init__(self, Agent, num_agents, maxiter, agent_params, socket_params):

        self.num_agents = num_agents
        self.maxiter = maxiter

        # Global best errors and positions
        self.best_global_error      = -1                     # best error for group
        self.best_global_position   = []                     # best position for group

        # Init socket
        self._init_socket_params(**socket_params)

        # Create the swarm
        self._init_swarm(Agent, agent_params)

    def _init_socket_params(self, web_socket, socket_update_frequency, thread_stopper):
        self.web_socket = web_socket
        self.socket_update_frequency = socket_update_frequency
        self.thread_stopper = thread_stopper

    def _init_swarm(self, Agent, agent_params):
        self.swarm = [Agent(agent_i, **agent_params) for agent_i in range(self.num_agents)]

    def publish_to_websocket(self, timestep_i):

        socket_address = "pso_init" if timestep_i == 0 else "pso_end" if timestep_i == self.maxiter-1 else "pso_update"

        agent_histories_i = []
        for agent_i in self.swarm:
            agent_histories_i.append({
                "agent"     : agent_i.id,
                "position"  : [agent_i.current_position, agent_i.current_error]
            })

        self.web_socket.emit(socket_address,
            {
                'time_i'    : timestep_i,
                "history"   : agent_histories_i,
                "swarm"     : {
                    "best_position" : self.best_global_position,
                    "best_error"    : self.best_global_error
                }
            },
            namespace='/pso'
        )

        time.sleep(self.socket_update_frequency)

    def run(self):

        # begin optimization loop
        for timestep_i in range(self.maxiter):

            if self.thread_stopper.stopped:
                print("Exiting!")
                break

            # cycle through particles in swarm and evaluate fitness
            for agent_i in self.swarm:
                agent_i.evaluate()

                # determine if current particle is the best (globally)
                if agent_i.current_error < self.best_global_error or self.best_global_error == -1:
                    self.best_global_position = agent_i.current_position
                    self.best_global_error = float(agent_i.current_error)

            # Update position history
            self.publish_to_websocket(timestep_i)

            # Update agent positions and velocities
            for agent_i in self.swarm:
                agent_i.update_velocity(self.best_global_position)
                agent_i.update_position()

        # print final results
        print('GLOBAL -- Best Position: {}, Best Error: {}'.format(self.best_global_position, self.best_global_error))
