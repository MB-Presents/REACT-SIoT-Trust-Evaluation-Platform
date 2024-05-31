# Host Machine


- Install docker
  - brew install docker
<!-- - Install conda envrionment
  -  brew install --cask anaconda -->
- Install XQUARTZ
  - brew install --cask xquartz
  - Setup X11 Server
  - .ssh/config -> Write HOST....
- brew install xauth
- echo $DISPLAY
- xauth list
- touch /tmp/.docker.xauth               
- Copy results from xauth list into  /tmp/.docker.xauth       



Add to docker compose file

- environment:
  - DISPLAY
  - XAUTHORITY=/tmp/.docker.xauth
- volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix
  - /tmp/.docker.xauth:/tmp/.docker.xauth





SOurces: https://gist.github.com/sorny/969fe55d85c9b0035b0109a31cbcb088


-  ifconfig en0
-  Copy inet address
-  export DISPLAY=<ipadress>:0
   - On mac: xhost + <ipadress>