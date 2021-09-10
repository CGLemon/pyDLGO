# dlgo GTP

## ㄧ、支援的指令

以下是 dlgo 所支援的 GTP 指令

   * `quit`
      * 退出並結束執行。
   * `name`
      * 顯示程式名字。
   * `version`
      * 顯示程式版本。
   * `protocol_version`
      * 顯示 GTP 的版本。
   * `list_commands`
      * 顯示所有支援的 GTP 指令。
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

## 二、其它

更多完整的指令和詳細的參數設置可到 [GTP 英文文檔](https://www.gnu.org/software/gnugo/gnugo_19.html)查看。
