import threading
from threading import Lock

import sys
import os
import numpy as np
import json
import time

from flask import render_template, jsonify, request
from pso_app import app, socketio
import flask_socketio
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

sys.path.append('../modules')
from Swarm import Swarm
from Agent import Agent
from helper import ThreadStopper

from sklearn.ensemble import RandomForestRegressor

thread = None
thread_lock = Lock()

bounds = (0, 400)
objective_string = "abs((0.07*x - 10)**3 - 8*x + 500)"
objective = lambda x : eval(objective_string)
objective_values = [{"x" : x, "y" : objective(x)} for x in range(401)]

@socketio.on('connect', namespace='/pso')
def pso_connect():
    print("Connected.")


@socketio.on("updateObjective", namespace='/pso')
def set_new_objective_function(message):

    global objective_string
    objective_string = message["new_objective"]

    potential_np_functions = ["sin", "cos", "exp"]
    for np_func in potential_np_functions:
        objective_string = objective_string.replace(np_func, "np.{}".format(np_func))

    global objective
    objective = lambda x : eval(objective_string)

    global objective_values
    objective_values = [{"x" : x, "y" : objective(x)} for x in range(401)]

    socketio.emit("receive_objective_function",
        {
            "objective_function"    : objective_values,
            "objective_string"      : objective_string,
            "bounds"                : bounds
        },
        namespace='/pso'
    )

@socketio.on('get_objective_function', namespace='/pso')
def get_objective_function(message):
    # emit("receive_objective_function", data={"objective_function" : {"x" : objective_x, "y" : objective_y}})

    socketio.emit("receive_objective_function",
        {
            "objective_function"    : objective_values,
            "objective_string"      : objective_string,
            "bounds"                : bounds
        },
        namespace='/pso'
    )

@socketio.on('runPSO', namespace='/pso')
def initializePSO(message):
    global thread_stopper
    thread_stopper = ThreadStopper()
    message["thread_stopper"] = thread_stopper
    thread = threading.Thread(target=run_pso, kwargs=message)
    thread.start()

@socketio.on('stopPSO', namespace='/pso')
def stopPSO(message):
    print("Stopping PSO...")
    print(message)
    thread_stopper.stop()

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


#--- MAIN ---------------------------------------------------------------------+
def run_pso(C1, C2, W, maxiter, num_agents, thread_stopper):

    #--- RUN ----------------------------------------------------------------------+
    swarm_params = {
        "objective"                 : objective,
        "bounds"                    : bounds,
        "num_agents"                : num_agents,
        "maxiter"                   : maxiter,
        "c1"                        : C1,
        "c2"                        : C2,
        "weight"                    : W,
        "Agent"                     : Agent,
        "web_socket"                : socketio,
        "socket_update_frequency"   : 1,
        "thread_stopper"            : thread_stopper
    }

    pso_swarm = Swarm(**swarm_params)
    pso_swarm.run()
    #--- END ----------------------------------------------------------------------+
