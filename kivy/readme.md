# Building on Linux machine
1. 
```
sudo apt-get update
sudo apt-get upgrade
```
1. make sure to have jdk, python3 and pip3 installed
1. install kivy for python3
1. reboot
1. if you have created a virtual environement for kivy during installation,
 enable it, e. g. `source ~/kivy_venv/bin/activate` 
1. `sudo apt install libffi-dev`
1. `pip3 install cython`
1. `pip3 install jnius`
1. `buildozer -v android debug` (this may take a while)
