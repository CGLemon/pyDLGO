# dlgo API

## board.py

以下是棋盤裡可用的 functions 和參數，此檔案依賴於 config.py 和 NumPy，只需要少量修改，就可以遷移進入你的專案。

#### Functions
   * `void Board.__init__(size: int, komi: float)`
      * Board 的初始化建構。

   * `void Board.reset(size: int, komi: float)`
      * 清理盤面並重新開始。

   * `bool Board.legal(vertex: int)`
      * 測試是否為合法手，如果是合法手，返回 True。

   * `bool Board.play(vertex: int)`
      * 走一手棋到到盤面上。也會測試是否為合法手，如果是合法手，返回 True。

   * `int Board.final_score()`
      * 計算基於 Tromp-Taylor 規則的目數。

   * `int Board.get_vertex(x: int, y: int)`
      * 將 x, y 座標轉成 vertex。

   * `str Board.vertex_to_text(vtx: int)`
      * 將 vertex 轉成文字。

   * `Board Board.copy()`
      * 快速複製當前的棋盤，複製的棋盤共用歷史盤面。
    
   * `bool Board.superko()`
      * 當前盤面是否為 superko，如果是則返回 True。

   * `nparry Board.get_features()`
      * 得到神經網路的輸入資料。

   * `str Board.__str__()`
      * 將當前盤面轉成文字。

#### Parametes

   * `int BLACK = 0`
      * 黑棋的數值。

   * `int WHITE = 1`
      * 白棋的數值。

   * `int PASS = -1`
      * 虛手的 vertex 數值。

   * `int RESIGN = -2`
      * 投降的 vertex 數值。

   * `int Board.board_size`
      * 當前盤面大小。
      
   * `float Board.komi`
      * 當前貼目。

   * `float Board.to_move`
      * 當前下棋的顏色。

   * `int Board.move_num`
      * 當前手數。

   * `int Board.last_move`
      * 上一手棋下的位置。

   * `int Board.num_passes`
      * 虛手的次數。

   * `list[nparray] Board.history`
      * 歷史的盤面。
