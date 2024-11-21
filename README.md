# REACT-SIoT

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
<!-- [![Build Status](https://img.shields.io/github/actions/workflow/status/MB-Presents/REACT-SIoT/build.yml)](https://github.com/MB-Presents/REACT-SIoT/actions)   -->
<!-- [![Docker](https://img.shields.io/docker/pulls/MB-Presents/react-siot)](https://hub.docker.com/r/MB-Presents/react-siot) -->
<!-- [![Contributors](https://img.shields.io/github/contributors/MB-Presents/REACT-SIoT)](https://github.com/MB-Presents/REACT-SIoT/graphs/contributors) -->

The **REACT-SIoT** project is a research initiative designed to evaluate and validate novel trust models in **Social Internet of Things (SIoT)** environments. The platform provides tools for researchers and industry professionals to simulate realistic SIoT settings, benchmark trust metrics, and enable trustworthy distributed collaborations.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Manuals for Tools and Setup](#manuals-for-tools-and-setup)
   - [X11 Setup](#x11-setup)
   - [ELK Stack Access and Logs](#elk-stack-access-and-logs)
4. [Usage](#usage)
5. [Architecture](#architecture)
6. [Contributing](#contributing)
7. [License](#license)

---

## Features
- **Realistic SIoT Environment**: Simulate and evaluate trust models in distributed IoT scenarios.
- **Modular Architecture**: Easily configurable and extendable with Dockerized components.
- **Comprehensive Logs**: Centralized logging with ELK stack (Elasticsearch, Logstash, Kibana).
- **Visualization Tools**: Built-in dashboards for trust evaluation metrics.

---

## Installation

### Prerequisites
- **Docker**: Install Docker Desktop from [Docker’s website](https://docs.docker.com/get-docker/).
- **Docker Compose**: Ensure Docker Compose is installed, often bundled with Docker Desktop.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/MB-Presents/REACT-SIoT.git
   cd REACT-SIoT
   ```
2. Build the Docker images:
   ```bash
   docker-compose build
   ```
3. Start the platform:
   ```bash
   docker-compose up
   ```

---

## Manuals for Tools and Setup

### X11 Setup

**X11** is required to allow graphical tools within Docker to display on your host machine. Follow these steps for setup:

#### On MacOS
1. **Install XQuartz**:
   ```bash
   brew install --cask xquartz
   ```
   Launch XQuartz and enable network client connections:
   - Go to **XQuartz > Preferences > Security**.
   - Check **"Allow connections from network clients"**.

2. **Install XAuth**:
   ```bash
   brew install xauth
   ```

3. **Setup Display**:
   - Determine your host machine’s IP address:
     ```bash
     ifconfig en0
     ```
     Note the `inet` address.
   - Export the display environment variable:
     ```bash
     export DISPLAY=<your-ip-address>:0
     ```

4. **Grant Permissions**:
   Allow your host to accept X11 connections:
   ```bash
   xhost + <your-ip-address>
   ```

5. **Configure Docker Compose**:
   Ensure your `docker-compose.yml` includes:
   ```yaml
   services:
     sumo:
       environment:
         - DISPLAY=${DISPLAY}
         - XAUTHORITY=/tmp/.docker.xauth
       volumes:
         - /tmp/.X11-unix:/tmp/.X11-unix
         - /tmp/.docker.xauth:/tmp/.docker.xauth
   ```

#### On Linux
1. Ensure `xhost` is installed.
2. Allow Docker containers to use your display:
   ```bash
   xhost +local:docker
   ```

#### On Windows
1. Install an X server like [VcXsrv](https://sourceforge.net/projects/vcxsrv/).
2. Configure your Docker container to connect to the X server:
   - Set the `DISPLAY` environment variable.

---

### ELK Stack Access and Logs

The **ELK Stack** (Elasticsearch, Logstash, Kibana) is used for centralized logging and analysis.

#### Step 1: Ensure ELK Stack Is Running
Start the ELK stack using:
```bash
docker-compose up
```

#### Step 2: Access Kibana
1. Open your browser and navigate to:
   ```
   http://localhost:5601
   ```
2. Log in using the credentials:
   - username: `elastic`
   - Password: Set in your `.env` file as `ELASTIC_PASSWORD`.

#### Step 3: View Logs in Kibana
1. Navigate to **Discover** in the left-hand menu.
2. Set up an index pattern:
   - Go to **Stack Management > Index Patterns**.
   - Create a new index pattern matching Logstash (e.g., `logstash-*`).
3. Use filters or search to analyze logs.

#### Access Logs from Docker
For direct logs:
```bash
docker logs <container-name>
```
For example:
```bash
docker logs elasticsearch
```

---

## Usage

### Running the Platform
Once the platform is up, you can access:
- **Kibana**: `http://localhost:5601`

### Evaluating Trust Models
1. Upload your custom trust model to the `models/` directory.
2. Configure the `config.json` file to reference your model.
3. Restart the Docker stack to apply changes.

---

## Architecture

The REACT-SIoT platform comprises the following key components:

1. **Frontend**: A web-based interface for configuration and visualization.
2. **Backend**: Core logic for simulations and trust model evaluation.
3. **Database**: Stores logs, configurations, and results.
4. **Logging System (ELK)**: Centralized logging with Elasticsearch, Logstash, and Kibana.



---

## Contributing

We welcome community contributions! To contribute:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with detailed descriptions of your changes.


---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

### Future Improvements
1. Add pre-configured scripts to automate X11 and ELK setups.
2. Provide example datasets and sample trust models.
3. Include detailed API documentation for programmatic usage.