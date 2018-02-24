#!/bin/bash
cd trajectory && FLASK_DEBUG=1 uwsgi --lazy-apps --callable app  --http :9090 --processes 4 --threads 1 --wsgi-file TrajectoryServer.py
