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

thread = None
thread_lock = Lock()

@socketio.on('connect', namespace='/pso')
def pso_connect():
    print("Connected.")
    # global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task(target=background_thread)


@socketio.on('runPSO', namespace='/pso')
def initPSOparams(message):
    print(message)
    run_pso(**message)

@app.route('/')
def index():
    return render_template('index.html')


#--- MAIN ---------------------------------------------------------------------+
def run_pso(C1, C2, W, maxiter, num_agents):

    bounds = [(-100,100), (-100,100)]   # input bounds [(x1_min,x1_max),(x2_min,x2_max)...]

    def objective_function(x):
        error = 0.0
        for x_i in x:
            error += (x_i * x_i) - (10 * np.cos(2 * np.pi * x_i)) + 10
        return error

    #--- RUN ----------------------------------------------------------------------+
    swarm_params = {
        "costFunc"      : objective_function,
        "bounds"        : bounds,
        "num_agents"    : num_agents,
        "maxiter"       : maxiter,
        "c1"            : C1,
        "c2"            : C2,
        "weight"        : W,
        "Agent"         : Agent
    }

    pso_swarm = Swarm(**swarm_params)
    pso_swarm.run()

    for i, history_i in enumerate(pso_swarm.swarm_position_history):
        socket_address = "pso_init" if i == 0 else "pso_end" if (i == len(pso_swarm.swarm_position_history) - 1) else "pso_update"
        socketio.emit(socket_address,
            {
                'time_i'    : i,
                "history"   : [{
                    "agent" : "agent_{}".format(i),
                    "position" : [np.random.randint(-10, 10), np.random.randint(-10, 10)]
                } for i in range(num_agents)]
            },
            namespace='/pso'
        )
        time.sleep(2)

    return jsonify({"result" : True})
    #--- END ----------------------------------------------------------------------+
