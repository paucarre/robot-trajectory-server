#!/bin/bash
cd trajectory && uwsgi --lazy-apps --callable app  --http :9090 --processes 4 --threads 1 --wsgi-file TrajectoryServer.py
