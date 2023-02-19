import sqlite3
import datetime

experiment_id = "A1"    ####### Change 
sample_counter = -1 
today = datetime.date.today().strftime('%Y-%m-%d')

#CREATING TABLE TRAJECTORIES
def create_table_trajectories():
    cursor = sqlite3.connect('database.db')
    cursor.execute('DROP TABLE IF EXISTS trajectories')
    cursor.execute('''CREATE TABLE trajectories
                (experiment_id text, player_id integer, frame_id integer, position_x real, position_y real, position_w real, position_h real, unfiltered_psi real, filtered_psi real)''')
    cursor.close()
def write_in_trajectories_player_coordinates(boxes):
    global sample_counter
    sample_counter += 1
    cursor = sqlite3.connect('../database.db')
    for i, box in enumerate(boxes):
        cursor.execute('''INSERT INTO trajectories (experiment_id, player_id, frame_id, position_x, position_y, position_w, position_h) values (?, ?, ?, ?, ?, ?, ?)''', (experiment_id, i+1, sample_counter, box[0], box[1], box[2], box[3]))
    cursor.commit()
    cursor.close()

def write_in_trajectories_psis(psi_u, psi_f, counter):
    cursor = sqlite3.connect('../database.db')
    cursor.execute('''UPDATE trajectories SET unfiltered_psi = ?, filtered_psi = ? WHERE experiment_id = ? and frame_id = ?''', (psi_u, psi_f, experiment_id, counter))
    cursor.commit()
    cursor.close()


#CREATING TABLE EXPERIMENT_PARAMETERS
def create_table_experiment_parameters():
    cursor = sqlite3.connect('database.db')
    cursor.execute('DROP TABLE IF EXISTS experiment_parameters')
    cursor.execute('''CREATE TABLE experiment_parameters
                (experiment_id text, date date, location text, start_time time, end_time time, use_correction integer, psi_buffer_size integer, observation_window_size integer, use_local integer, sigmoid_a real, sigmoid_b real)''')
    cursor.close()

def write_in_experiment_parameters_start_time():
    cursor = sqlite3.connect('../database.db')
    cursor.execute('''INSERT INTO experiment_parameters (experiment_id, date, start_time) values (?, ?, ?)''', (experiment_id, today, datetime.datetime.now().strftime('%H:%M:%S')))
    cursor.commit()
    cursor.close()

def write_in_experiment_parameters_emergenceCalculator(use_correction, psi_buffer_size, observation_window_size, use_local):
    cursor = sqlite3.connect('../database.db')
    cursor.execute('''UPDATE experiment_parameters SET use_correction = ?, psi_buffer_size = ?, observation_window_size = ?, use_local = ? WHERE experiment_id = ? and date = ?''', (use_correction, psi_buffer_size, observation_window_size, use_local, experiment_id, today))
    cursor.commit()
    cursor.close()

def write_in_experiment_parameters_end_time():
    cursor = sqlite3.connect('../database.db')
    cursor.execute('''UPDATE experiment_parameters SET end_time = ? WHERE experiment_id = ? and date = ?''', (datetime.datetime.now().strftime('%H:%M:%S'), experiment_id, today))
    cursor.commit()
    cursor.close()

### Creating tables    
create_table_trajectories()
create_table_experiment_parameters()
