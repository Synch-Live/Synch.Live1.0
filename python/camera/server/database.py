import sqlite3
import datetime
import csv
from io import StringIO

today = datetime.date.today().strftime('%Y-%m-%d')
datapath = './database.db'

#CREATING TABLE TRAJECTORIES
def create_table_trajectories():
    cursor = sqlite3.connect(datapath)
    #cursor.execute('DROP TABLE IF EXISTS trajectories')
    cursor.execute('''CREATE TABLE IF NOT EXISTS trajectories
                (experiment_id text, 
                player_id integer, 
                frame_id integer, 
                position_x real, 
                position_y real, 
                position_w real, 
                position_h real, 
                unfiltered_psi real, 
                filtered_psi real)''')
    cursor.close()

def write_in_trajectories_player_coordinates(experiment_id, frame_id, boxes):
    cursor = sqlite3.connect(datapath)
    for i, box in enumerate(boxes):
        cursor.execute('''INSERT INTO trajectories 
        (experiment_id, 
        player_id, 
        frame_id, 
        position_x, 
        position_y, 
        position_w, 
        position_h) values (?, ?, ?, ?, ?, ?, ?)''', 
        (experiment_id, (i + 1), frame_id, box[0], box[1], box[2], box[3]))
    cursor.commit()
    cursor.close()

def write_in_trajectories_psis(psi_u, psi_f, experiment_id, frame_id):
    cursor = sqlite3.connect(datapath)
    cursor.execute('''UPDATE trajectories SET 
        unfiltered_psi = ?, filtered_psi = ? 
        WHERE experiment_id = ? and frame_id = ?''', 
        (psi_u, psi_f, experiment_id, frame_id))
    cursor.commit()
    cursor.close()


#CREATING TABLE EXPERIMENT_PARAMETERS
def create_table_experiment_parameters():
    cursor = sqlite3.connect(datapath)
    #cursor.execute('DROP TABLE IF EXISTS experiment_parameters')
    cursor.execute('''CREATE TABLE IF NOT EXISTS experiment_parameters
                (experiment_id text, 
                date date, 
                location text, 
                start_time time, 
                end_time time, 
                use_correction integer, 
                psi_buffer_size integer, 
                observation_window_size integer, 
                use_local integer, 
                sigmoid_a real, 
                sigmoid_b real)''')
    cursor.close()

def write_in_experiment_parameters(experiment_id, experiment_location):
    cursor = sqlite3.connect(datapath)
    cursor.execute('''INSERT INTO experiment_parameters 
        (experiment_id, 
        location,
        date, 
        start_time) values (?, ?, ?, ?)''', 
        (experiment_id, experiment_location, today, datetime.datetime.now().strftime('%H:%M:%S')))
    cursor.commit()
    cursor.close()

def write_in_experiment_parameters_emergenceCalculator(use_correction, psi_buffer_size, 
                                                       observation_window_size, use_local, experiment_id):
    cursor = sqlite3.connect(datapath)
    cursor.execute('''UPDATE experiment_parameters SET 
        use_correction = ?, 
        psi_buffer_size = ?, 
        observation_window_size = ?, 
        use_local = ? WHERE experiment_id = ? and date = ?''', 
        (use_correction, psi_buffer_size, observation_window_size, use_local, experiment_id, today))
    cursor.commit()
    cursor.close()

def write_in_experiment_parameters_end_time(experiment_id):
    cursor = sqlite3.connect(datapath)
    cursor.execute('''UPDATE experiment_parameters SET end_time = ? 
        WHERE experiment_id = ? and date = ?''', 
        (datetime.datetime.now().strftime('%H:%M:%S'), experiment_id, today))
    cursor.commit()
    cursor.close()

### QUERY DATABASE ###
def process_query(experiment_id):

    connection = sqlite3.connect(datapath)
    cursor = connection.cursor()

    si = StringIO()
    cw = csv.writer(si)
    cursor.execute('''SELECT * FROM experiment_parameters WHERE experiment_id = ?''', [experiment_id])
    rows = cursor.fetchall()
    cw.writerow([i[0] for i in cursor.description])
    cw.writerows(rows)

    '''
    cursor.execute(''''''SELECT * from experiment_parameters'''''')
    search_results = cursor.fetchall()
    '''
    cursor.close()

    return si

### Creating tables    
create_table_trajectories()
create_table_experiment_parameters()
