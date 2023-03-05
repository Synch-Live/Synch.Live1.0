import os

from flask import Flask, render_template, url_for
from . import download, download

from synch_live.camera.video.video import VideoProcessorProxy
from synch_live.camera.server.db import *

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        VIDEO_CONFIG=os.path.join(app.instance_path, 'video_config.yml'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    @app.template_global()
    def navigation():
        return [
            #dict(href=url_for('main'), caption='Home'),
            dict(href=url_for('setup.start_setup'), caption='Setup'),
            dict(href=url_for('tracking.control'), caption='Experiment'),
            dict(href=url_for('download.get_data'), caption='Data'),
            #dict(href=url_for('tracking.start_tracking'), caption='Start tracking'),
            #dict(href=url_for('tracking.stop_tracking'), caption='Stop tracking'),
            #dict(href=url_for('calibrate.calibrate'), caption='Calibrate'),
            #dict(href=url_for('experiment.observe'), caption='Observe')
        ]

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def main():
        return render_template('main.html')

    from . import calibration, setup, experiment, tracking, download
    app.register_blueprint(calibration.bp)
    app.register_blueprint(setup.bp)
    app.register_blueprint(experiment.bp)
    app.register_blueprint(tracking.bp)
    app.register_blueprint(download.bp)


    config_path = app.config.get_namespace('VIDEO_').get('config')
    VideoProcessorProxy(config_path)

    #cleanup database
    clean_query()

    #db.init_app(app)
    from .plotlydash.dashboard import init_dashboard
    app = init_dashboard(app)

    return app

