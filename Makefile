MAKEFLAGS = -s

DOCKER_IMAGE := robot-trajectory-server

.PHONY: help build
.DEFAULT_GOAL := help

help:
	@echo "make build  -- builds a docker container"
	@echo "make run    -- runs a docker container"
	@echo "make test   -- runs tests"
	@echo

build:
	docker build -t $(DOCKER_IMAGE) .

run: build
	docker run -it -p 9090:9090 --add-host="localhost:192.168.65.1" -e ROBOT_TRAJECTORY_SERVER_SETTINGS='../conf/settings-dev.conf'  --user daemon robot-trajectory-server:latest

test:
	cd src && \
	 python  -m unittest discover -s .  -p 'Test*.py'
