# Synch.Live database connection

A database is created to store trajectories and experiment parameters using 'sqlite3'.
The database holdstwo tables `trajectories` and `experiment_parameters`.
The code for database is located in `python/camera/server/database.py`.

### Running an experiment and getting a database
Once you launch `server.py` app, you can input `Experimet id` and `Experiment location` and press `Start tracking`.
A `database.db` is created automatically once you start tracking (if it doesn't already exist) in `python` directory.
All the findings are being written to the database once the experiment is running. 
When `Stop Tracking` is pressed, the database can be downloaded. On the main app page, you can input `Experiment id`
and press `Get trajectories`. A database will be downloaded in `csv` format for the particular experiment id.

### `trajectories` TABLE
This table contains `experiment_id` inputted by the user on the app, 
`player_id` which starts from '1' and depends on the number of hats used in the experiment, 
`frame_id` which starts from '0' every time a new experiment is run to indicate initial position, 
`position_x` which is computed as "x-w/2", 
`position_y` which is computed as "y-h/2", 
`unfiltered_psi` which is 'NULL' when `frame_id` is '0', 
`filtered_psi` which is 'NULL' when `frame_id` is '0'.

This table is being filled in `video.py` by calling functions `write_in_trajectories_player_coordinates` and
`write_in_trajectories_psis` in `database.py`.

### `experiment_parameters` TABLE
This table contains `experiment_id` inputted by the user on the app,
`date` which is a current date at the experiment run time, 
`location` inputted by the user on the app, 
`start_time` which is a current time at the experiment run time, 
`end_time` which is a time when `Stop Tracking` is pressed, 
`use_correction`, 
`psi_buffer_size`, 
`observation_window_size`, 
`use_local`, 
`sigmoid_a`, 
`sigmoid_b`.

`experiment_id`, `location`,`date` and `start_time` parameters of the table are being filled in `server.py` 
when we `start_tracking` by calling `write_in_experiment_parameters` function in `database.py`.
The other parameters of this table are being filled in `video.py` 
by calling `write_in_experiment_parameters_emergenceCalculator`, `write_in_experiment_parameters_sigmoids` and `write_in_experiment_parameters_end_time` functions in `database.py`.

Note: to write `sigmoid_a` and `sigmoid_b` to database, a function `write_in_experiment_parameters_sigmoids`
was added to the function `Sync(self)` in `video.py` to retrieve them and `Sync(self)` is being called in `server.py`.