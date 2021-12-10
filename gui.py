from board import Board, PASS, RESIGN, BLACK, WHITE, INVLD, EMPTY
from gtp import GTP_ENGINE
from config import BOARD_SIZE, KOMI

import time
import argparse
import tkinter as tk
from threading import Thread
from tkinter import scrolledtext

class GUI_LOOP(GTP_ENGINE):
    def __init__(self, args):
        super(GUI_LOOP, self).__init__(args)

        self.window = tk.Tk()
        self.window.resizable(0,0)
        self.window.title('Deep Learning Go')
        self.window.geometry('810x500')

        self.rect = None
        self.oval_buffer = [None] * self.board.num_intersections
        self.text_buffer = [None] * self.board.num_intersections
        self.game_thread = None
        self.acquire_vtx = None

        self.init_layerout()
        self.window.mainloop()

    def init_layerout(self):
        self.canvas = tk.Canvas(self.window, bg='#CD853F', height=435, width=435)
        self.scroll_rext = scrolledtext.ScrolledText(self.window, width=38, height=24)

        self.bt_black_start = tk.Button(self.window, text="執黑開始", command=lambda :self.start_new_game(BLACK))
        self.bt_black_start.place(x=480, y=10)

        self.bt_white_start = tk.Button(self.window, text="執白開始", command=lambda :self.start_new_game(WHITE))
        self.bt_white_start.place(x=580, y=10)

        self.bt_pass_start = tk.Button(self.window, text="虛手", command=lambda :self.acquire_move(PASS))
        self.bt_pass_start.place(x=480, y=50)

        self.draw_canvas((30, 30))
        self.draw_text((480, 100))
        self.draw_rows_cols((42, 470), (10, 35))


    def draw_canvas(self, canvas_pos):
        x, y = canvas_pos
        for i in range(self.board.board_size+1):
            pos = i*(400-2)/(self.board.board_size-1)
            SIDE = (435 - 400)/2
            self.canvas.create_line(SIDE, SIDE+pos, SIDE+400, SIDE+pos)
            self.canvas.create_line(SIDE+pos, SIDE, SIDE+pos, SIDE+400)
        self.canvas.place(x=x, y=y)

    def draw_rows_cols(self, rspos, cspos):
        rx, ry = rspos
        cx, cy = cspos
        for i in range(self.board.board_size):
            clabel = tk.Label(self.window, text=str(i+1))
            clabel.place(x=cx, y=cy+i*(400-2)/(self.board.board_size-1))

            rlabel = tk.Label(self.window, text=str(i+1))
            rlabel.place(x=rx+i*(400-2)/(self.board.board_size-1), y=ry)

    def draw_text(self, xy_pos):
        x, y = xy_pos
        self.scroll_rext.place(x=x, y=y)
    
    def draw_scroll_text(self, string):
        self.scroll_rext.insert(tk.END, string+'\n')
        self.scroll_rext.see(tk.END)
        self.scroll_rext.update()
    
    def reset_canvas(self):
        self.clear_board()
        self.canvas.delete("all")
        self.scroll_rext.delete(1.0, tk.END)
        self.draw_canvas((30, 30))
        self.canvas.bind("<Button-1>", self.scan_move)

    def draw_stone(self, player, rc_pos, Index, RADIUS=15):
        r, c = rc_pos
        x, y = self.convert_rc_to_xy(rc_pos)
        colorText  = 'black' if player == 1 else 'white'
        colorPiece = 'white' if player == 1 else 'black'
        self.oval_buffer[self.board.get_index(r,c)] = self.canvas.create_oval(x-RADIUS, y-RADIUS, x + RADIUS, y+RADIUS, fill=colorPiece, outline=colorPiece)

        if self.rect == None:
            OFFSET = 20
            self.rect = self.canvas.create_rectangle(x-OFFSET, y-OFFSET, x+OFFSET, y+OFFSET, outline="#c1005d")
            self.rect_xy_pos = (x, y)
        else:
            rc_pos = self.convert_xy_to_rc((x, y))
            old_x, old_y = self.rect_xy_pos
            new_x, new_y = self.convert_rc_to_xy(rc_pos)
            dx, dy = new_x-old_x, new_y-old_y
            self.canvas.move(self.rect, dx, dy)
            self.rect_xy_pos = (new_x, new_y)

        self.text_buffer[self.board.get_index(r,c)] = self.canvas.create_text(x,y, text=str(Index), fill=colorText,)
        self.canvas.update()

    def convert_rc_to_xy(self, rc_pos):
        SIDE = (435 - 400)/2
        DELTA = (400-2)/(self.board.board_size-1)
        r, c = rc_pos
        x = c*DELTA+SIDE
        y = r*DELTA+SIDE
        return x, y

    def convert_xy_to_rc(self, xy_pos):
        SIDE = (435 - 400)/2
        DELTA = (400-2)/(self.board.board_size-1)
        x, y = xy_pos
        r = round((y-SIDE)/DELTA)
        c = round((x-SIDE)/DELTA)
        return r, c

    def start_new_game(self, color):
        if self.game_thread != None:
            self.game_thread = None

        self.turns = ["compute", "compute"]
        self.turns[color] = "player"

        self.game_thread = Thread(target=self.process_game,)
        self.game_thread.setDaemon(True) 
        self.game_thread.start()

    def process_game(self):
        self.reset_canvas()

        resignd = None
        self.flag_player_click = False

        while True:
            time.sleep(0.1)

            to_move = self.board.to_move
            move_num = self.board.move_num

            if self.turns[to_move] == "compute":
                move = self.genmove(to_move)
                
                vtx = self.board.last_move
                if move == "resign":
                    vtx = RESIGN
                    resignd = to_move

                if vtx != PASS or vtx != RESIGN:
                    x = self.board.get_x(vtx)
                    y = self.board.get_y(vtx)
                self.update_canvas(vtx, (x,y), to_move,  move_num+1)
            else:
                if self.acquire_vtx != None:
                    if self.acquire_vtx == PASS:
                        self.board.play(PASS)
                        self.canvas.delete(self.rect)
                        self.flag_player_click = False
                    self.acquire_vtx = None
                elif self.flag_player_click and self.is_validmove(self.rc_pos):
                    r, c = self.rc_pos
                    self.board.play(self.board.get_vertex(r,c))
                    self.update_canvas(self.board.get_vertex(r,c), self.rc_pos, to_move,  move_num+1)
                    self.flag_player_click = False

            if resignd != None:
                if resignd == BLACK:
                    self.draw_scroll_text("黑棋投降")
                else:
                    self.draw_scroll_text("白棋投降")
                break
            elif self.board.num_passes >= 2:
                score = self.board.final_score()
                if abs(score) <= 0.01:
                    self.draw_scroll_text("平手")
                elif score > 0:
                    self.draw_scroll_text("黑勝{}目".format(score))
                elif score < 0:
                    self.draw_scroll_text("白勝{}目".format(-score))
                break

    def update_canvas(self, vtx, rc_pos, to_move, move_num):
        r, c = rc_pos
        self.draw_stone(to_move, rc_pos, move_num)
        if self.board.removed_cnt != 0:
            curr = len(self.board.history) - 1
            post_state = self.board.history[curr-1]
            for v in range(len(post_state)):
                if self.board.state[v] == EMPTY and post_state[v] != EMPTY:
                    self.canvas.delete(self.oval_buffer[self.board.vertex_to_index(v)])
                    self.canvas.delete(self.text_buffer[self.board.vertex_to_index(v)])

    def is_validmove(self, rc_pos):
        r, c = rc_pos

        if r < 0 or r >= self.board.board_size:
            self.flag_player_click = False
            return False

        if c < 0 or c >= self.board.board_size:
            self.flag_player_click = False
            return False

        return self.board.legal(self.board.get_vertex(r,c))

    def scan_move(self, event):
        self.flag_player_click = True

        x, y = event.x, event.y
        r, c = self.convert_xy_to_rc((x, y))
        self.rc_pos = (r, c)

    def acquire_move(self, vtx):
        self.acquire_vtx = vtx
