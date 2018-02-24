FROM ubuntu:16.04

RUN \
  apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

RUN \
  sudo apt-get update && \
  sudo apt-get install -y software-properties-common python-software-properties && \
  sudo apt-get install -y vim git bzip2 make tree telnet bsdtar curl wget && \
  apt-get clean

RUN mkdir /home/daemon && \
  chown -R daemon: /home/daemon && \
  chmod -R u+w /home/daemon && \
  echo "daemon:daemon" | chpasswd && adduser daemon sudo && \
  printf '%s\n%s\n' '%sudo   ALL=(ALL:ALL) ALL' '%sudo   ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
  usermod -d /home/daemon  daemon

USER daemon

RUN sudo -Hu daemon bash && \
  touch /home/daemon/.profile && \
  export PATH=/home/daemon/miniconda3/bin:$PATH

RUN cd /home/daemon && \
  curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
  chmod +x Miniconda3-latest-Linux-x86_64.sh  && \
  ./Miniconda3-latest-Linux-x86_64.sh -b && \
  rm Miniconda3-latest-Linux-x86_64.sh

ENV PATH="/home/daemon/miniconda3/bin:${PATH}"

RUN ["bash", "-c", "cd /home/daemon && \
  conda create --name pytorch python=3.6 --yes && \
  source activate pytorch && \
  conda install --yes -c conda-forge uwsgi && \
  conda install --yes click && \
  conda install --yes psycopg2 && \
  conda install --yes flask && \
  conda install --yes numpy && \
  conda install --yes requests && \
  conda clean --all -y"]

RUN cd /home/daemon && \
  git clone https://github.com/paucarre/robot-fabrik-cga.git && \
  cd robot-fabrik-cga && \
  ./setup.py install

RUN cd /home/daemon && \
  git clone https://github.com/pygae/clifford.git && \
  cd clifford && \
  python setup.py install

RUN cd /home/daemon && \
  mkdir robot-trajectory-server

COPY . /home/daemon/robot-trajectory-server

RUN sudo chown -R daemon: /home/daemon/robot-trajectory-server && \
  sudo chmod -R u+w /home/daemon/robot-trajectory-server

ENV ROBOT_TRAJECTORY_SERVER_SETTINGS='../conf/settings.conf'

RUN conda install --yes -c conda-forge uwsgi

ENTRYPOINT ["bash", "-c", "cd /home/daemon/robot-trajectory-server && \
  source activate pytorch && \
  export LC_ALL=C.UTF-8 && \
  export LANG=C.UTF-8 && \
  ./bin/start.sh"]
