# dlgo API

## board.py 的可用 API

注意，此檔案依賴於 config.py 和 numpy

#### Functions

   * `void Board.reset(size: int, komi: float)`
      * 清理盤面。

   * `bool Board.legal(vertex: int)`
      * 測試是否為合法手，如果是合法手，返回 True。

   * `bool Board.play(vertex: int)`
      * 走一手棋到到盤面上，如果是合法手，返回 True。

   * `int Board.final_score()`
      * 計算基於 Tromp-Taylor 規則的目數。

   * `int Board.get_vertex(x: int, y: int)`
      * 將 x, y 座標轉成 vertex。

   * `str Board.vertex_to_text(vtx: int)`
      * 將 vertex 轉成文字。

   * `Board Board.copy()`
      * 快速複製當前盤面，共用歷史盤面。
    
   * `nparry Board.get_features()`
      * 得到神經網路的輸入資料。

   * `str Board.__str__()`
      * 將當前盤面轉成文字。

#### Parametes

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


