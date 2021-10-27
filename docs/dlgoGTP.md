# dlgo GTP

## ㄧ、支援的指令

dlgo 僅支援少量的 GTP 指令，主要是為了滿足 TCGA 比賽的基本需求（KGS），當然還有很多指令尚未實作，如果有興趣可到 [GTP 英文文檔](https://www.gnu.org/software/gnugo/gnugo_19.html)找到更多資訊。

   * `quit`
      * 退出並結束執行。

   * `name`
      * 顯示程式名字。

   * `version`
      * 顯示程式版本。

   * `protocol_version`
      * 顯示使用的 GTP 版本。

   * `list_commands`
      * 顯示所有此程式支援的 GTP 指令。

   * `play <color: string, 'black' or 'white'> <vertex: string, eg. 'a1', 'a2', 'pass', 'resign'>`
      * 走一手棋到盤面上，必須是合法手。

   * `genmove <color: string, 'black' or 'white'>`
      * 讓引擎思考並產生下一手棋到盤面上。

   * `undo`
      * 悔棋。

   * `clear_board`
      * 清空盤面，重新新的一局。

   * `boardsize <size: integer>`
      * 設定不同的盤面大小。注意，dlgo 的神經網路接受的盤面大小是固定的，隨意調整可能使程式崩貴退出。

   * `komi <komi: float>`
      * 設定不同的貼目。注意，dlgo 的勝率不會因貼目改變而動態調整。

   * `time_settings <main time: integer> <byo time: integer> <byo stones: integer>`
      * 設定初始的限時時間。

   * `time_left <color: string, 'black' or 'white'> <main time: integer> <byo time: integer> <byo stones: integer>`
      * 設定某方剩餘的限時時間。

## 二、其它 KGS 可用指令

有些指令在 kgs 上有特殊效果，或是可以提供更多功能，如果有興趣的話，可以優先實作下列指令，指令的參數和效果可到[GTP 英文文檔](https://www.gnu.org/software/gnugo/gnugo_19.html)

   * `final_status_list`
      * 顯示當言盤面的死棋和活棋。

   * `place_free_handicap`
      * 讓 Bot 自己決定讓子的位置。
      
   * `set_free_handicap`
      * 使用者告所電腦讓子的位置。
      
   * `kgs-genmove_cleanup`
      * KGS 專用的生成合法手。
      
   * `kgs-time_settings`
      * KGS 專用的時間控制指令。
      
   * `kgs-game_over`
      * 當每盤對戰結束，會發出此指令。
