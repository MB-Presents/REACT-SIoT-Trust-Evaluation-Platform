echo "Starting dev env with GUI"
echo "Copy x cookies into temop file"

rmdir /tmp/.docker.xauth
xauth list > /tmp/.docker.xauth

echo "Completed copying x cookies into temop file"


echo "Set ip address for xhost and env variable DISPLAY"
echo $(ifconfig en0 | grep 'inet ' | awk '{print $2}')


export DISPLAY_EXT=$(ifconfig en0 | grep 'inet ' | awk '{print $2}'):0
echo "DISPLAY_EXT: $DISPLAY_EXT"


xhost +$(ifconfig en0 | grep 'inet ' | awk '{print $2}')

devcontainer open