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
        position_as_int = float(positon)
    except BaseException as e:
        return Response(f"Bad Request: 'position' with value {positon} is not a float", status=400)
    print(content)
    return(uuid)
