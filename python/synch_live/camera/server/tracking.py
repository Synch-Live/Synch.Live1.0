from flask import Blueprint, redirect, url_for, Response, jsonify, render_template, request
from wtforms import Form, IntegerField, validators, StringField, widgets, SelectField, BooleanField, FormField
from wtforms.widgets import html_params

from synch_live.camera.video.video import VideoProcessorProxy
from synch_live.camera.server.db import *

bp = Blueprint('tracking', __name__, url_prefix='/tracking')

@bp.route('/control', methods=['GET','POST'])
def control():

    form = ExperimentInfoForm(request.form)
    
    if request.method == 'POST' and form.validate():
        experiment_id = form.experiment_id.data
        experiment_location = form.experiment_location.data
        
        if form.experiment_test.data:
            experiment_is_test = 'YES'
        else:
            experiment_is_test = 'NO'

        # writing date, start time, experiment id, location to database
        write_in_experiment_parameters(experiment_id, experiment_location, experiment_is_test) 

        proc = VideoProcessorProxy()
        proc.set_experiment_id(experiment_id)
        proc.start()
        
        #VideoProcessorProxy().start()
        
        return redirect(url_for('experiment.observe'))
    
    return render_template('control.html', form=form)



@bp.route('/start', methods=['GET', 'POST'])
def start_tracking():
    experiment_id = "test"
    experiment_location = "home"

    # writing date, start time, experiment id, location to database
    write_in_experiment_parameters(experiment_id, experiment_location) 

    VideoProcessorProxy().start()
    return redirect(url_for('experiment.observe'))


@bp.route('/stop')
def stop_tracking():
    VideoProcessorProxy().stop()
    return redirect(url_for('main'))


@bp.route('/sync')
def sync():
    return jsonify(VideoProcessorProxy().sync)


@bp.route('/feed')
def feed():
    return Response(VideoProcessorProxy().generate_frame(), mimetype="multipart/x-mixed-replace; boundary=frame")

class ExperimentInfoForm(Form):
    experiment_id = StringField('Experiment ID')
    experiment_location = StringField('Experiment location')
    experiment_test = BooleanField('Test?')

