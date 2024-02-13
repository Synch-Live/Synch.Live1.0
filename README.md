# Synch.Live
An art experience and collective behaviour experiment based on an information-theoretic criterion of emergent behaviour conceptualised by [Hillary Leone](https://cabengo.com).

This repository contains on the `main` branch the nighly development version of the Synch.Live 1.0 (Computer Vision) system software.

The system is composed of the `observer`, a Raspberri Pi 4 with a PiCamera, and the `player`, headsets equipped with Raspberry Pi Zero W and LEDs. The `observer` tracks the LEDs on the `player`s with computer vision (OpenCV) and computes information theory on trajectories using [JIDT](https://github.com/jlizier/jidt).

## Contents
The code contains four folders:
- `ansible` - scripts to control hat devices including clock synchronisation, code update, and light testing via SSH using Ansible
- `media` - contains example videos to test the Observer in dev mode
- `python` - contains the core Synch.Live Observer code including the web app, database, and calculation scripts
- `setup` - contains setup instructions, hosts files, and other system files to be added to the Raspberry Pi when setting up new `observer`s or `player`s


# Observer Development
This section includes the code and instructions for running the Observer code. This can be run in development mode on a laptop, or in live mode on the Observer pi. Note that throughout, specific Python and packaging versioning is **very important**, so please make sure you're using the correct versions.


## Installation for development

1. Clone the relevant branch

2. Go to the `python/` folder and create a virtual environment with Python 3.7. This specific version of Python is required to run the `openCV` package successfully on the Pi (so it is good practice to ensure you use the same version for development). Do not use a more recent version, or you are likely to have trouble getting your code to run on the Observer. To create and activate a virtual enfironment:
```
cd Synch.Live1.0/python
python3.7 -m venv venv
source venv/bin/activate
```

> [!IMPORTANT]
> Python3.7 is by now deprecated, so specific installation of the `python3.7-venv` is necessary to create the virtual environment.
> Make sure you always run Synch.Live development in virtual environments with all dependencies installed. 
> See official Python [docs](https://docs.python.org/3/library/venv.html#creating-virtual-environments) on `venv` and instructions for Ubuntu [here](https://stackoverflow.com/questions/70422866/how-to-create-a-venv-with-a-different-python-version).
 
3. Install the requirements by running the following code **from within your virtual environment** (notice the full stop after the e). This may fail at the `picamera` package as it fails some hardware checks on non-Raspberry Pi devices.
```
pip install -e.
```
4. Install npm on your machine. Use `brew install npm` for Mac and see [here](https://phoenixnap.com/kb/install-node-js-npm-on-windows) for Windows. Once npm is successfully installed (check by running `npm -v` in the command line), navigate to the folder `/python/synch_live/camera/server` and run the following:
```
cd Synch.Live1.0/python/synch_live/camera/server
npm install
```
5. Run the flask app from the `/python` folder with the `--debug` option:
```
cd Synch.Live1.0/python
flask --app synch_live.camera.server run --debug
```
6. Go to `localhost:5000` in your browser. If this doesn't connect, try `127.0.0.1:5000`.

7. Navigate around the app. You should be able to run a test video.

## Installation on the Observer pi

There are several ways to get the latest code onto the Observer. If you connect it to the internet, then you can `scp` any updated files to the Observer to replace previous versions. There are also Ansible scripts in the `ansible` folder to update code, but these are very slow to run. So we recommend `scp` instead.

To get in to the observer, connect to the Synch.Live router and `ssh` to `pi@observer.local`.

TODO:
- Setup of system daemons and MDNS

# Troubleshooting
This section contains a log of the main issues encountered during the development of the udpated Observer app in Q1 2023 and outstanding TODOs.

TODO:
- The Observer is set up for automatic hat detection. The resulting link to the hat has a trailing fullstop `.` (i.e. `player4.local.:5000` rather than `player4.local:5000`). This link works OK on Macs but not on Windows. The fix should be straighforward and should be somewhere in `python/synch_live/camera/server/players_listener.py`, which is where the automatic hat detection is impelemented.
- include system setup files for Observer

- **OpenCV version issues** The current Observer uses Python 3.7 and has a compatible OpenCV package installed (4.4.0.46). But later Python versions are not compatible with this package, so if you want to upgrade the Observer's Python version then you will also need to figure out a way to get a later version of OpenCV installed. There are several issues you may run into:
  - Some OpenCV versions do not have pre-compiled binary executables available for Debian. This means that installing new versions can take a very long time (in the order of hours).
  - Some OpenCV versions are not compatible with either / both the Observer's camera and the code. You won't find out if this is the case until after installation, which can be frustrating if that has taken hours!
  - As a final bonus issue, the OpenCV version used in development cannot be installed on Macs with M1 chips. An alternative version (4.4.0.46) works OK, but note that there may be some subtle differences that we did not uncover during testing. So make sure to test camera-related code on the Observer itself.
- **Ansible version issues** There is a warning that Ansible is being deprecated for Python 3.7, which the Observer Pi currently uses. Upgrading Python to resolve this issue suffers from the other issues mentioned in the previous bullet. Ansible should be used with version 2.10 next to Python3.7
