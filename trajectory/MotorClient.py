import random
import os
import re
import threading
import time
import datetime
import json
import sys
import socket

class MotorClient():

    def __init__(self, articulation_ips):
        self.articulation_ips = articulation_ips

    def send_socket(self, message, current_socket):
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

    def receive_socket(self, current_socket):
        received_bytes = []
        is_connected = True
        while is_connected:
            byte_received = current_socket.recv(1)
            received_bytes.insert(len(received_bytes), byte_received.decode("utf-8"))
            is_connected = byte_received != b''
        return ''.join(received_bytes)

    def create_connection(self, ip):
        try:
            current_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            current_socket.connect((ip, 23))
            return current_socket
        except e:
            print(f"Connection to IP {ip} was unsucccesful due to '{e}'")
            return None

    def disconnect(self, socket):
        try:
            socket.disconnect()
            return True
        except BaseException as e:
            print(f"Error trying to disconnect due to '{e}'")
            return False

    def get_position(self, ip):
        socket = self.create_connection(ip)
        position_as_float = None
        if(socket is not None):
            successful = send_socket(bytearray(b'?'), socket)
            if(successful):
                raw_position = receive_socket(socket)
                if(raw_position is not None):
                    position_as_float = float(raw_position)
                else:
                    print(f"Problem receiving positon from articulation in IP {ip}")
            else:
                print(f"Problem sending positon request to articulation in IP {ip}")
            disconnect(socket)
        else:
            print(f"Problem connecting to articulation with IP {ip}")
        return position_as_float

    def set_position_(self, position, index):
        ip = self.articulation_ips[index]
        socket = self.create_connection(ip)
        position_as_float = None
        if(socket is not None):
            possition_message = f">{position}"
            position_message_byte = bytearray()
            position_message_byte.extend(map(ord, possition_message))
            successful = self.send_socket(position_message_byte, socket)
            if(successful):
                return True
            else:
                return False

    def get_articulation_positions(self):
        articulation_positions = []
        for articulation_ip in self.articulation_ips:
            articulation_position = self.get_position(articulation_ip)
            articulation_positions.insert(len(articulation_positions), articulation_position)
        return articulation_positions
