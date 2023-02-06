
import logging

from uwb.core.emergence import EmergenceCalculator, compute_macro
from uwb.core.tracking  import EuclideanMultiTracker

class UWBConnection():

    def __init__(self, args):

        # TODO: LAURIA:
        #  Change / set the arguments that you need to create the connection

        # Housekeeping
        self.name = ""
        self.MAC = ""

        # Make a buffer that we can use for averaging & outlier detection
        self.position_buffer = []

        # Other parameters
        self.smoothing_alpha = 0.01
        self.smoothing_beta = 0.001
        self.window_length = 30


    def connectToPlayer(self):

        # TODO: LAURIA:
        #  Player connection code

        # Not sure what this will be but should be a persistent object in self namespace
        self.myConnection = "???"


    def pollPlayer(self):

        # TODO: LAURIA:
        #  Get the position, we can figure out later what we actually return (instantaneous value, smoothed persisted
        #  value, etc) but for now simple return is probably best

        position = "..."

        return position

class UWBHandler():
    """
    Initialized with a dict of UWB connection objects.
    Handles the binning, and return of player x-y coordinates into downstream emergence stuff
    """
    def __init__(self, my_uwb_connections, config):

        self.my_uwb_connections = my_uwb_connections

        self.sampling_rate_hz = 60
        self.running = False
        self.config = config

        self.task = self.config.game.task

        self.tracking_thread = threading.Thread(target=self.tracking)
        self.lock = threading.Lock()

        self.calc = None
        self.psi = 0.0

    @property
    def Sync(self) -> float:

        if self.task == 'manual':
            return self.psi / 10.0
        elif self.task == 'emergence':
            a = 0
            b = 3
            return 1.0 / (1 + np.exp((self.psi - a) / b))
        else:
            return self.psi

    def set_manual_psi(self, psi: float) -> None:
        if self.task != 'manual':
            if self.task == 'psi':
                if self.calc:
                    self.calc.exit()

            self.task = 'manual'
            self.config.game.task = 'manual'

        self.psi = psi

        logging.info(f"Manually setting psi to {psi}")

    def update_tracking_conf(self, max_players: int) -> None:
        """
        Following a form submission in the front-end, reinitialise tracker with
        new parameters, as well as update config

        Params
        ------
            max_players
                maximum number of objects to be tracked

        Side-effects
        ------
            - reinitialise tracker
        """
        self.config.tracking.max_players = int(max_players)

        self.tracker = EuclideanMultiTracker(self.config.tracking)

        logging.info(f"Updated max_players from Web UI to {max_players} and reinitialised tracker")




