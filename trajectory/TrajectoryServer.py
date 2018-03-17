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
from Kinematics import Kinematics
import json

app = Flask(__name__)
app.config.from_envvar('ROBOT_TRAJECTORY_SERVER_SETTINGS')
kinematics = Kinematics()

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

@app.route('/inverse_kinematics_path', methods=['GET'])
def inverse_kinematics_path():
    try:
        path = get_argument('path', lambda path_json: json.loads(path_json))
    except ValueError as e:
        return Response(f"Error parsing 'path' argument which has to be a JSON array of arrays of 3 elements (x, y, z): {e}", status=400)
    angles_path = kinematics.get_angles_from_path(path)
    return Response(f"{angles_path}", mimetype='text/html', status=200)

@app.route('/inverse_kinematics', methods=['GET'])
def inverse_kinematics():
    try:
        x = get_argument('x', lambda x: int(x))
        y = get_argument('y', lambda x: int(x))
        z = get_argument('z', lambda x: int(x))
    except ValueError as e:
        return Response(f"{e}", status=400)
    angles = kinematics.get_angles_from_coordinate(x, y, z)
    return Response(f"{angles}", mimetype='text/html', status=200)

@app.route('/move_to_coordinates', methods=['POST'])
def move_to_coordinates():
    try:
        path = get_argument('path', lambda path_json: json.loads(path_json))
    except ValueError as e:
        return Response(f"Error parsing 'path' argument which has to be a JSON array of arrays of 3 elements (x, y, z): {e}", status=400)
    angles_path = kinematics.get_angles_from_path(path)
    for angles in angles_path:
        for articulation, angle in enumerate(angles):
            try:
                motor_client.set_position(angle, articulation)
            except BaseException as e:
                error = traceback.format_exc()
                return Response(f"Error communicating with articulation {articulation} to move it to position {angle} with error: {error}", status=500)
    return Response(f"{angles_path}", mimetype='text/html', status=200)

@app.route('/move_to_coordinate', methods=['POST'])
def move_to_coordinate():
    try:
        x = get_argument('x', lambda x: int(x))
        y = get_argument('y', lambda x: int(x))
        z = get_argument('z', lambda x: int(x))
    except ValueError as e:
        return Response(f"{e}", status=400)
    angles = kinematics.get_angles_from_coordinate(x, y, z)
    motor_client = MotorClient(articulations_config)
    for articulation, angle in enumerate(angles):
        try:
            motor_client.set_position(angle, articulation)
        except BaseException as e:
            error = traceback.format_exc()
            return Response(f"Error communicating with articulation {articulation} to move it to position {angle} with error: {error}", status=500)
    return Response(f"{angles}", mimetype='text/html', status=200)

@app.route('/positions', methods=['GET'])
def positions():
    motor_client = MotorClient(articulations_config)
    articulation_positions = motor_client.get_articulation_positions()
    return Response(f"{articulation_positions}", mimetype='text/html', status=200)

@app.route('/move/<articulation>', methods=['POST'])
def move(articulation):
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
