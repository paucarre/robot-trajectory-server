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

worker_ids = None
worker_index = None
worker_index_update_time = None
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

def send_socket(message, current_socket):
    bytes_sent = 0
    is_connected = True
    while bytes_sent < len(message) and is_connected:
        current_bytes_sent = current_socket.send(message[bytes_sent:])
        is_connected = current_bytes_sent > 0
        if is_connected:
            bytes_sent = bytes_sent + current_bytes_sent
        else:
            print(f"Socket '{socket}' disconnected")
    return is_connected

def receive_socket(current_socket):
    received_bytes = []
    is_connected = True
    while is_connected:
        byte_received = current_socket.recv(1)
        received_bytes.insert(len(received_bytes), byte_received.decode("utf-8"))
        print(f"****{byte_received}****")
        is_connected = byte_received != b''
    return ''.join(received_bytes)

def create_connection(ip):
    try:
        current_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        current_socket.connect((ip, 23))
        return current_socket
    except e:
        print(f"Connection to IP {ip} was unsucccesful due to '{e}'")
        return None

def disconnect(socket):
    try:
        socket.disconnect()
        return True
    except BaseException as e:
        print(f"Error trying to disconnect due to '{e}'")
        return False

def get_current_position(ip):
    socket = create_connection(ip)
    position_as_float = None
    if(socket is not None):
        successful = send_socket(bytearray(b'?'), socket)
        if(successful):
            raw_position = receive_socket(socket)
            if(raw_position is not None):
                #print(f"*******{raw_position}*******")
                position_as_float = float(raw_position)
            else:
                print(f"Problem receiving positon from articulation in IP {ip}")
        else:
            print(f"Problem sending positon request to articulation in IP {ip}")
        disconnect(socket)
    else:
        print(f"Problem connecting to articulation with IP {ip}")
    return position_as_float

def get_articulation_positions():
    articulation_positions = []
    for articulation_ip in articulation_ips:
        articulation_position = get_current_position(articulation_ip)
        articulation_positions.insert(len(articulation_positions), articulation_position)
    return articulation_positions

@app.route('/positions', methods=['GET'])
def positions_endpoint():
    articulation_positions = get_articulation_positions()
    return Response(f"{articulation_positions}", mimetype='text/html', status=200)

@app.route('/move_to', methods=['POST'])
def move_to():
    pass
