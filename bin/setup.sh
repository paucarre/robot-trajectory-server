#!/bin/bash
conda create --name pytorch python=3.6 --yes && \
source activate pytorch && \
conda install --yes -c conda-forge uwsgi && \
conda install --yes click && \
conda install --yes psycopg2 && \
conda install --yes flask && \
conda install --yes numpy && \
conda install --yes requests && \
conda clean --all -y
