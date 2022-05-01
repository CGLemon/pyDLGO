import time

class TimeControl:
    def __init__(self):
        self.main_time = 0
        self.byo_time = 7 * 24 * 60 * 60 # one week per move
        self.byo_stones = 1

        self.maintime_left = [0, 0]
        self.byotime_left = [0, 0]
        self.stones_left = [0, 0]
        self.in_byo = [False, False]
        
        self.clock_time = time.time()
        self.reset()

    def check_in_byo(self):
        self.in_byo[0] = True if self.maintime_left[0] <= 0 else False
        self.in_byo[1] = True if self.maintime_left[1] <= 0 else False

    def reset(self):
        self.maintime_left = [self.main_time] * 2
        self.byotime_left = [self.byo_time] * 2
        self.stones_left = [self.byo_stones] * 2
        self.check_in_byo()

    def time_settings(self, main_time, byo_time, byo_stones):
        self.main_time = main_time
        self.byo_time = byo_time
        self.byo_stones = byo_stones
        self.reset()

    def time_left(self, color, time, stones):
        if stones == 0:
            self.maintime_left[color] = time
        else:
            self.maintime_left[color] = 0
            self.byotime_left[color] = time
            self.stones_left[color] = stones
        self.check_in_byo()

    def clock(self):
        self.clock_time = time.time()

    def took_time(self, color):
        remaining_took_time = time.time() - self.clock_time
        if not self.in_byo[color]:
            if self.maintime_left[color] > remaining_took_time:
                self.maintime_left[color] -= remaining_took_time
                remaining_took_time = -1
            else:
                remaining_took_time -= self.maintime_left[color]
                self.maintime_left[color] = 0
                self.in_byo[color] = True

        if self.in_byo[color] and remaining_took_time > 0:
            self.byotime_left[color] -= remaining_took_time
            self.stones_left[color] -= 1
            if self.stones_left[color] == 0:
                self.stones_left[color] = self.byo_stones
                self.byotime_left[color] = self.byo_time

    def get_thinking_time(self, color, board_size, move_num):
        estimate_moves_left = max(4, int(board_size * board_size * 0.4) - move_num)
        lag_buffer = 1 # Remaining some time for network hiccups or GUI lag 
        remaining_time = self.maintime_left[color] + self.byotime_left[color] - lag_buffer
        if self.byo_stones == 0:
            return remaining_time / estimate_moves_left
        return remaining_time / self.stones_left[color]

    def should_stop(self, max_time):
        elapsed = time.time() - self.clock_time
        return elapsed > max_time

    def get_timeleft_string(self, color):
        out = str()
        if not self.in_byo[color]:
            out += "{s} sec".format(
                                 s=int(self.maintime_left[color]))
        else:
            out += "{s} sec, {c} stones".format(
                                             s=int(self.byotime_left[color]),
                                             c=self.stones_left[color])
        return out

    def __str__(self):
        return "".join(["Black: ",
                          self.get_timeleft_string(0),
                           " | White: ",
                           self.get_timeleft_string(1)])
