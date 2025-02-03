from sys import stderr, stdout, stdin
from board import Board, PASS, RESIGN, BLACK, WHITE, INVLD
from network import Network
from mcts import Search
from config import BOARD_SIZE, KOMI
from time_control import TimeControl

class GTP_ENGINE:
    def __init__(self, args):
        self.args = args
        self.board = Board(BOARD_SIZE, KOMI)
        self.network = Network(BOARD_SIZE)
        self.time_control = TimeControl()
        self.network.trainable(False)
        self.board_history = [self.board.copy()]
        self.last_verbose = str()

        if self.args.weights != None:
            self.network.load_pt(self.args.weights)

    # For GTP command "clear_board". Reset the board to the initial state and
    # clear the move history.
    def clear_board(self):
        self.board.reset(self.board.board_size, self.board.komi)
        self.board_history = [self.board.copy()]
        self.network.clear_cache()

    # For GTP command "genmove". The engine returns the best move and play it. 
    def genmove(self, color):
        # Genrate next move and play it.
        c = self.board.to_move
        if color.lower()[:1] == "b":
            c = BLACK
        elif color.lower()[:1] == "w":
            c = WHITE

        self.board.to_move = c
        search = Search(self.board, self.network, self.time_control)

        # Collect the search verbose for the built-in GUI.
        move, self.last_verbose = search.think(
                                      self.args.playouts,
                                      self.args.resign_threshold,
                                      self.args.verbose)
        if self.board.play(move):
            self.board_history.append(self.board.copy())

        return self.board.vertex_to_text(move)
        
    # For GTP command "play". Play a move if it is legal. 
    def play(self, color, move):
        # play move if the move is legal.
        c = INVLD
        if color.lower()[:1] == "b":
            c = BLACK
        elif color.lower()[:1] == "w":
            c = WHITE

        vtx = None
        if move == "pass":
            vtx = PASS
        elif move == "resign":
            vtx = RESIGN
        else:
            x = ord(move[0]) - (ord('A') if ord(move[0]) < ord('a') else ord('a'))
            y = int(move[1:]) - 1
            if x >= 8:
                x -= 1
            vtx = self.board.get_vertex(x,y)

        if c != INVLD:
            self.board.to_move = c
            if self.board.play(vtx):
                self.board_history.append(self.board.copy())
                return True
        return False

    # For GTP command "undo". Play the undo move.
    def undo(self):
        if len(self.board_history) > 1:
            self.board_history.pop()
            self.board = self.board_history[-1].copy()

    # For GTP command "boardsize". Set a variant board size.
    def boardsize(self, bsize):
        self.board.reset(bsize, self.board.komi)
        self.board_history = [self.board.copy()]
        self.network.clear_cache()

    # For GTP command "boardsize". Set a variant komi.
    def komi(self, k):
        self.board.komi = k

    # For GTP command "time_settings". Set initial time settings and restart it.
    # 'main time' is basic thinking time.
    # 'byo time' is byo yomi time.
    # 'byo stones' is byo yomi stone.
    def time_settings(self, main_time, byo_time, byo_stones):
        if not main_time.isdigit() or \
               not byo_time.isdigit() or \
               not byo_stones.isdigit():
            return False

        self.time_control.time_settings(int(main_time), int(byo_time), int(byo_stones))
        return True

    # For GTP command "time_left". Set time left value for one side.
    def time_left(self, color, time, stones):
        c = INVLD
        if color.lower()[:1] == "b":
            c = BLACK
        elif color.lower()[:1] == "w":
            c = WHITE
        if c == INVLD:
            return False
        self.time_control.time_left(c, int(time), int(stones))
        return True

    # For GTP command "showboard". Dump the board(stand error output).
    def showboard(self):
        stderr.write(str(self.board))
        stderr.flush()

    def lz_genmove_analyze(self, color, interval):
        c = self.board.to_move
        if color.lower()[:1] == "b":
            c = BLACK
        elif color.lower()[:1] == "w":
            c = WHITE

        self.board.to_move = c
        search = Search(self.board, self.network, self.time_control)
        search.analysis_tag["interval"] = interval/100

        # Collect the search verbose for the built-in GUI.
        move, self.last_verbose = search.think(
                                      self.args.playouts,
                                      self.args.resign_threshold,
                                      self.args.verbose)
        if self.board.play(move):
            self.board_history.append(self.board.copy())

        return self.board.vertex_to_text(move)

    def lz_analyze(self, color, interval):
        c = self.board.to_move
        if color.lower()[:1] == "b":
            c = BLACK
        elif color.lower()[:1] == "w":
            c = WHITE

        self.board.to_move = c
        search = Search(self.board, self.network, self.time_control)
        search.analysis_tag["interval"] = interval/100

        # Collect the search verbose for the built-in GUI.
        self.last_verbose = search.ponder(
                                self.args.playouts * 100,
                                self.args.verbose)

class GTP_LOOP:
    COMMANDS_LIST = [
        "quit", "name", "version", "protocol_version", "list_commands",
        "play", "genmove", "undo", "clear_board", "boardsize", "komi",
        "time_settings", "time_left", "lz-genmove_analyze", "lz-analyze"
    ]
    def __init__(self, args):
        self.engine = GTP_ENGINE(args)
        self.args = args
        self.cmd_id = None

        # Start the main GTP loop.
        self.loop()
        
    def loop(self):
        while True:
            # Get the commands.
            cmd = stdin.readline().split()

            # Get the command id.
            self.set_id(cmd)

            if len(cmd) == 0:
                continue

            main = cmd[0]
            if main == "quit":
                self.success_print("")
                break

            # Parse the commands and execute it.
            self.process(cmd)

    def set_id(self, cmd):
        self.cmd_id = None
        if len(cmd) == 0:
            return

        if cmd[0].isdigit():
            self.cmd_id = cmd.pop(0)

    def process(self, cmd):
        # TODO: Support analyze and genmove_analyze commands.
        main = cmd[0]
        
        if main == "name":
            self.success_print("dlgo")
        elif main == "version":
            version = "0.1";
            if self.args.kgs:
                self.success_print(version + "\nI am a simple bot. I don't understand the life and death. Please help me to remove the dead strings when the game is end. Have a nice game.")
            else:
                self.success_print(version)
        elif main == "protocol_version":
            self.success_print("2")
        elif main == "list_commands":
            clist = str()
            for c in self.COMMANDS_LIST:
                clist += c
                if c is not self.COMMANDS_LIST[-1]:
                    clist += '\n'
            self.success_print(clist)
        elif main == "clear_board":
            # reset the board
            self.engine.clear_board();
            self.success_print("")
        elif main == "play" and len(cmd) >= 3:
            # play color move
            if self.engine.play(cmd[1], cmd[2]):
                self.success_print("")
            else:
                self.fail_print("")
        elif main == "undo":
            # undo move
            self.engine.undo();
            self.success_print("")
        elif main == "genmove" and len(cmd) >= 2:
            # genrate next move
            self.success_print(self.engine.genmove(cmd[1]))
        elif main == "boardsize" and len(cmd) >= 2:
            # set board size and reset the board
            self.engine.boardsize(int(cmd[1]))
            self.success_print("")
        elif main == "komi" and len(cmd) >= 2:
            # set komi
            self.engine.komi(float(cmd[1]))
            self.success_print("")
        elif main == "showboard":
            # display the board
            self.engine.showboard()
            self.success_print("")
        elif main == "time_settings":
            if self.engine.time_settings(cmd[1], cmd[2], cmd[3]):
                self.success_print("")
            else:
                self.fail_print("")
        elif main == "time_left":
            if self.cmd_id is not None:
                stdout.write("={}\n".format(self.cmd_id))
            else:
                stdout.write("=\n")
            stdout.flush()
        elif main == "lz-genmove_analyze":
            color = "tomove"
            interval = 0
            if len(cmd) >= 2:
                if cmd[1].isdigit():
                    interval = cmd[1]
                if cmd[2].isdigit():
                    color = cmd[1]
                    interval = cmd[2]
            self.success_half('')
            m = self.engine.lz_genmove_analyze(color, int(interval))
            stdout.write("play {}\n\n".format(m))
            stdout.flush()
        elif main == "lz-analyze":
            color = "tomove"
            interval = 0
            if len(cmd) >= 2:
                if cmd[1].isdigit():
                    interval = cmd[1]
                if cmd[2].isdigit():
                    color = cmd[1]
                    interval = cmd[2]
            self.success_half('')
            m = self.engine.lz_analyze(color, int(interval))
            stdout.write("\n")
            stdout.flush()
        else:
            self.fail_print("Unknown command")

    def success_half(self, res):
        if self.cmd_id is not None:
            stdout.write("={} {}\n".format(self.cmd_id, res))
        else:
            stdout.write("= {}\n".format(res))
        stdout.flush()

    def success_print(self, res):
        if self.cmd_id is not None:
            stdout.write("={} {}\n\n".format(self.cmd_id, res))
        else:
            stdout.write("= {}\n\n".format(res))
        stdout.flush()

    def fail_print(self, res):
        stdout.write("? {}\n\n".format(res))
        stdout.flush()
