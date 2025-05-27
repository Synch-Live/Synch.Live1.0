# Synch.Live musician

The code in this folder is a super-simple music player which responds to the values of synchrony emitted by the observerby changing the music from five pre-recorded layers.

## Testing

To run for testing, edit  `musician.py`, set `TEST_URL` to your local hostname with port `:8888` and replace `fetch_sync()` with `fetch_sync_mock()` on line 146. Then you can test this in 2 terminal windows as follows:


Terminal 1:

- install `netcat`

- run

    chmod +x observer_mock.sh
    ./observer_mock.sh

Terminal 2:

Run the `nix-shell` or preferred Python package environment to install dependencies (a `requirements.txt` is provided):

    nix-shell shell.nix 
    python3 musician.py


## Files

### Code files

- `hl_audio.py`: an example provided by HL with the original code for a hardware device playing music. For logic of audio volume.
- `musician.py`: 
- `observer_mock.sh`: a super-simple server that runs at port `:8888` in the `localhost` and whenever receives a HTTP request returns a random number. Can be used to test the Python code.


### Music files

The music files are in `../../media/music`, in the root of the repository.

### Synchrony values

Synchrony values are exposed by observer at http://observer.synch.live:8888/sync, and are currently computed as:

    sync = 1.0 / (1 + exp((psi - a) / b))

where `a = 0` and `b = 3`, and which **decreases** as Psi increases.

