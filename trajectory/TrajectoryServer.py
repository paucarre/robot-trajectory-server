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

app = Flask(__name__)
app.config.from_envvar('ROBOT_TRAJECTORY_SERVER_SETTINGS')

def get_articulation_ips():
    articulation_ips = [];
    number_of_articulations = app.config[f'NUMBER_OF_ARTICULATIONS']
    for articulation in range(0, number_of_articulations):
        articulation_ip_config = f"ARTICULATION_{articulation}_IP"
        articulation_ips.insert(len(articulation_ips), app.config[articulation_ip_config])
    return articulation_ips

articulation_ips = get_articulation_ips()

@app.route('/positions', methods=['GET'])
def positions_endpoint():
    motor_client = MotorClient(articulation_ips)
    articulation_positions = motor_client.get_articulation_positions()
    return Response(f"{articulation_positions}", mimetype='text/html', status=200)

@app.route('/move/<articulation>', methods=['POST'])
def move_to(articulation):
    motor_client = MotorClient(articulation_ips)
    position = request.args.get('position')
    if position is None:
        return Response("Bad Request: 'position' argument required", status=400)
    try:
        articulation = int(articulation)
        position_as_float= float(position)
    except BaseException as e:
        return Response(f"Bad Request: 'position' with value {position} is not a float or articulation {articulation} is not an integer", status=400)
    try:
        motor_client.set_position_(position_as_float, articulation)
        return Response(f"{position_as_float}", mimetype='text/html', status=200)
    except BaseException as e:
        error = traceback.format_exc()
        return Response(f"Error communicating with articulation {articulation} with error {error}", status=500)
