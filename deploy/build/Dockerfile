# Use an official Python runtime as a parent image
FROM ubuntu:22.04

# Update the system
RUN apt-get update -y && apt-get upgrade -y

# Set environment variable to avoid time zone prompt
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get install -y \
    software-properties-common \
    apt-utils \
    g++ \
    git \ 
    wget \
    cmake \
    libxerces-c-dev \
    libfox-1.6-0 libfox-1.6-dev \
    libgdal-dev \ 
    libproj-dev \ 
    libgl2ps-dev \
    swig \
    xauth \
    xvfb \
    libgl1-mesa-glx \
    curl \
    mesa-utils \
    x11-apps

RUN add-apt-repository ppa:deadsnakes/ppa -y 
RUN add-apt-repository ppa:sumo/stable
RUN apt-get update -y

RUN apt install -y python3.12
#  python3.12-venv
# RUN apt install -y python3-pip
# RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

RUN apt-get update -y 
RUN apt-get install gcc
RUN apt-get install -y python3.12-dev

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
# RUN update-alternatives --config python3

RUN echo "Building with Python version:" && python3 --version

# Install Python 3.11 (check if it's available in standard repositories of Ubuntu 22.04)
# RUN apt-get install -y python3.11 python3.11-dev python3.11-distutils

# Install pip for Python 3.11

RUN apt-get update -y

RUN apt update
RUN apt install -y sumo sumo-tools sumo-doc

RUN apt-get update -y 

RUN python3 --version

# Set environment variables
ENV SUMO_HOME=/usr/share/sumo
ENV DISPLAY=:0
ENV XAUTHORITY=/tmp/.docker.xauth

# Set locale
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US:en

ENV LIBGL_ALWAYS_INDIRECT=1
ENV RUNNING_ENV=local
# Create an alias for pip3 as pip
RUN command -v pip > /dev/null 2>&1 || ln -s $(which pip3) /usr/bin/pip

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY app /app




# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -r additional.txt

RUN pip install -r pip-packages/requirements_core.txt
RUN pip install -r pip-packages/requirements_ml.txt
RUN pip install -r pip-packages/requirements_jupyter.txt
RUN pip install -r pip-packages/requirements_logging.txt
RUN pip install -r pip-packages/requirements_others.txt

RUN pip install torch torch_geometric numpy python-logstash-async traci

# RUN pip install -r pip-packages/requirements_additional.txts


# Expose any necessary ports
EXPOSE 5000
# EXPOSE 8888

# ENV LIBGL_ALWAYS_INDIRECT=0



# Run the application
# CMD ["python", "app.py"]
ENTRYPOINT ["tail", "-f", "/dev/null"]




# RUN apt-get install --reinstall xserver-xorg-video-intel libgl1-mesa-glx libgl1-mesa-dri xserver-xorg-core