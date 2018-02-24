#!/bin/bash
cd trajectory && FLASK_DEBUG=1 uwsgi --touch-reload=TrajectoryServer.py --callable app  --http :9090 --processes 4 --threads 1  --wsgi-file TrajectoryServer.py
