import sys, os
from flask import Flask, jsonify, render_template, redirect, request, url_for
from flask.wrappers import Response
import signal
import logging
import yaml
from copy import deepcopy

from tools import parse
from uwb import UWBConnection, UWBHandler


def create_app(server_type, conf, conf_path, uwb_modules):
    app = Flask(__name__)
    app.debug = True
    conf.conf_path = conf_path

    logging.info(f"Creating {server_type} server with config:\n{conf}")

    proc = UWBHandler(conf, uwb_modules)

    def handler(signum, frame):
        res = input("Do you want to exit? Press y.")
        if res == 'y':
            proc.stop()
            exit(1)

    signal.signal(signal.SIGINT, handler)

    def is_running():
        if proc.running:
            return "Tracking is running."
        else:
            return "Tracking is off. Please press Start Tracking to begin the experiment."

    @app.route("/")
    def index():
        return render_template("index.html", running_text=is_running())

    @app.route("/sync")
    def return_sync():
        return jsonify(proc.Sync)

    @app.route("/start_tracking")
    def start_tracking():
        if not proc.running:
            proc.start()
        return redirect(url_for("observe"))

    @app.route("/stop_tracking")
    def stop_tracking():
        if proc.running:
            proc.stop()
        return redirect(url_for("index"))

    @app.route("/calibrate", methods = [ 'GET', 'POST' ])
    def calibrate():
        use_picamera = proc.config.server.CAMERA == 'pi'

        if request.method == 'GET':
            opts = unparse(proc.config)
            # color picker expects hex colours
            opts['detection']['min_colour'] = hsv_to_hex(vars(proc.config.detection.min_colour))
            opts['detection']['max_colour'] = hsv_to_hex(vars(proc.config.detection.max_colour))

            return render_template("calibrate.html", use_picamera = use_picamera,
                conf_path = proc.config.conf_path, save_file = False, opts = opts, awb_modes = awb_modes)
        else:
            proc.update_tracking_conf(request.form['max_players'])
            proc.update_detection_conf(
                request.form['min_contour'], request.form['max_contour'],
                request.form['min_colour'], request.form['max_colour'])

            if use_picamera:
                proc.update_picamera(request.form['iso'], request.form['shutter_speed'],
                    request.form['saturation'], request.form['awb_mode'])

            if 'save_file' in request.form:
                conf_path = request.form['conf_path']
                file = open(conf_path, 'w')
                conf_to_save = deepcopy(proc.config)
                conf_to_save.detection.min_colour = parse(unwrap_hsv(conf_to_save.detection.min_colour))
                conf_to_save.detection.max_colour = parse(unwrap_hsv(conf_to_save.detection.max_colour))
                delattr(conf_to_save, 'conf_path')
                yaml.dump(unparse(conf_to_save), file)

            return redirect(url_for("calibrate"))

    @app.route("/observe", methods = ['GET', 'POST'])
    def observe():
        if request.method == "POST":
            psi = int(request.form.get("manPsi"))
            use_psi = request.form.get("psi")

            if use_psi:
                proc.task = 'emergence'
            else:
                proc.set_manual_psi(psi)
            return render_template("observe.html", running_text=is_running(), psi=proc.psi, task=proc.task)
        return render_template("observe.html", running_text=is_running(), psi=proc.psi, task=proc.task)

    return app


if __name__ == '__main__':

    server_type = 'uwb_observer'

    if len(sys.argv) > 1:
        server_type = sys.argv[1]

    host = os.environ.get('HOST', default='0.0.0.0')
    port = int(os.environ.get('PORT', default='8888'))
    conf_path = os.environ.get('CONFIG_PATH', default='./uwb/config/default.yml')
    print(os.path.abspath("."))

    logging.info(f"Starting server, listening on {host} at port {port}, using config at {conf_path}")

    with open(conf_path, 'r') as fh:
        yaml_dict = yaml.safe_load(fh)
        config = parse(yaml_dict)

        logging.info(f"Establishing connections with UWB beacons...")

        # TODO: LAURIA: Don't pay attention to anything above if __name__...
        #  I have copied this from the camera equivalent and have not done much there yet

        # TODO: LAURIA:
        #  Here the server should create N instances of UWBConnection(), if you need to send
        #  MAC addresses or the like, I would recommend putting it in config/default.yml
        #  EX:
        #  my_uwb_connections = [UWBConnection(args, kwargs)]

        # TODO: LAURIA:
        #  Pass list of connected UWB objects to app creation.
        #  I have not yet verified what arguments we need here

        create_app(server_type, config, conf_path).run(host=host, port=port, debug=True, threaded=True, use_reloader=False)
