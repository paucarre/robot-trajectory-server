import uwsgi
import requests
import random
import os
import re
import threading
import time
import numpy as np
from flask import Flask, Response, request, render_template
import datetime
import json
import sys
import socket
import traceback
from MotorClient import MotorClient
from fabrik.FabrikSolver import FabrikSolver
from fabrik.JointChain import JointChain
from fabrik.Joint import Joint
from fabrik.ConformalGeometricAlgebra import ConformalGeometricAlgebra
import math

app = Flask(__name__)
app.config.from_envvar('ROBOT_TRAJECTORY_SERVER_SETTINGS')
cga = ConformalGeometricAlgebra(1e-11)

def get_articulations_config():
    articulations = []
    number_of_articulations = app.config[f'NUMBER_OF_ARTICULATIONS']
    for articulation in range(0, number_of_articulations):
        config = {}
        config['ip'] = app.config[f"ARTICULATION_{articulation}_IP"]
        config['length'] = app.config[f"ARTICULATION_{articulation}_LENGTH"]
        articulations.insert(len(articulations), config)
    print(articulations)
    return articulations

articulations_config = get_articulations_config()

def get_joint_chain():
    first_joint = Joint(math.pi, 40.0)
    second_joint = Joint(math.pi, 40.0)
    joint_chain = JointChain([first_joint, second_joint])
    return joint_chain

def get_argument(argument, transform):
    value = request.args.get(argument)
    if value is None:
        raise ValueError(f"Bad Request: '{argument}' argument required")
    else:
        try:
            value = transform(value)
        except BaseException as e:
            error = traceback.format_exc()
            raise ValueError(f"Bad Request: '{argument}' with value {value} is not valid: {error}")
        return value

@app.route('/trajectory', methods=['GET'])
def trajectory_endpoint():
    try:
        x = get_argument('x', lambda x: int(x))
        y = get_argument('y', lambda x: int(x))
        z = get_argument('z', lambda x: int(x))
    except ValueError as e:
        return Response(f"{e}", status=400)
    joint_chain = get_joint_chain()
    target_point = cga.point(x, y, z)
    fabrik_solver = FabrikSolver()
    positions = fabrik_solver.solve(joint_chain, target_point)
    rotors = fabrik_solver.toRotors(positions)
    angles = [cga.angleFromRotor(rotor) for rotor in rotors]
    motor_client = MotorClient(articulations_config)
    for articulation, angle in enumerate(angles):
        try:
            motor_client.set_position(angle, articulation)
        except BaseException as e:
            error = traceback.format_exc()
            return Response(f"Error communicating with articulation {articulation} to move it to position {angle} with error: {error}", status=500)
    return Response(f"{angles}", mimetype='text/html', status=200)

@app.route('/positions', methods=['GET'])
def positions_endpoint():
    motor_client = MotorClient(articulations_config)
    articulation_positions = motor_client.get_articulation_positions()
    return Response(f"{articulation_positions}", mimetype='text/html', status=200)

@app.route('/move/<articulation>', methods=['POST'])
def move_endpoint(articulation):
    motor_client = MotorClient(articulations_config)
    try:
        position_as_float = get_argument('position', lambda x: float(x))
    except ValueError as e:
        return Response(f"{e}", status=400)
    try:
        articulation = int(articulation)
    except BaseException as e:
        return Response(f"Bad Request:  articulation {articulation} is not an integer", status=400)
    try:
        motor_client.set_position(position_as_float, articulation)
        return Response(f"{position_as_float}", mimetype='text/html', status=200)
    except BaseException as e:
        error = traceback.format_exc()
        return Response(f"Error communicating with articulation {articulation} with error {error}", status=500)
