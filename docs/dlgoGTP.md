# dlgo GTP

## ㄧ、GTP 簡介
GTP(Go Text Protocol) 最早為 GNU Go 團隊為了簡化當時的圍棋協定 Go Modem Protocol，在 GNU Go 3.0 時引入，到了現代 GTP 以成為圍棋軟體普遍的溝通方式。GTP 運作的原理相當簡單，就是界面（或是使用者）向引擎送出一條指令，引擎根據指令做出相應的動作，並且回覆訊息給界面。回覆的格式分成兩種，一種是執行成功，此時回覆的第一個字元是 ```=```，另一種是執行失敗，此時回覆的第一個字元是 ```?```，回覆完結時要換兩行表示結束。以下是 dlgo 的範例，此範例要注意的是 showboard 的部份輸出是 stderr ，stdout 部份依舊是標準的 GTP 指令。

    name
    = dlgo
    
    version 
    = 0.1
    
    protocol_version
    = 2
    
    play b e5
    = 
    
    play w e3
    = 
    
    play b g5
    = 
    
    showboard
       A  B  C  D  E  F  G  H  J 
     9 .  .  .  .  .  .  .  .  .  9
     8 .  .  .  .  .  .  .  .  .  8
     7 .  .  .  .  .  .  .  .  .  7
     6 .  .  .  .  .  .  .  .  .  6
     5 .  .  .  .  X  . [X] .  .  5
     4 .  .  .  .  .  .  .  .  .  4
     3 .  .  .  .  O  .  .  .  .  3
     2 .  .  .  .  .  .  .  .  .  2
     1 .  .  .  .  .  .  .  .  .  1
       A  B  C  D  E  F  G  H  J 
    
    = 
    
    play w c4
    = 
    
    showboard
       A  B  C  D  E  F  G  H  J 
     9 .  .  .  .  .  .  .  .  .  9
     8 .  .  .  .  .  .  .  .  .  8
     7 .  .  .  .  .  .  .  .  .  7
     6 .  .  .  .  .  .  .  .  .  6
     5 .  .  .  .  X  .  X  .  .  5
     4 .  . [O] .  .  .  .  .  .  4
     3 .  .  .  .  O  .  .  .  .  3
     2 .  .  .  .  .  .  .  .  .  2
     1 .  .  .  .  .  .  .  .  .  1
       A  B  C  D  E  F  G  H  J 
    
    = 
    
    aabbbcccc
    ? Unknown command
    
    quit
    = 

## 二、支援的指令

dlgo 僅支援基本的 GTP 指令集，主要是為了滿足 TCGA 比賽的基本需求（KGS），當然還有很多標準指令尚未實作，如果有興趣可到 [GTP 英文文檔](https://www.gnu.org/software/gnugo/gnugo_19.html)找到更多資訊。以下是 dlgo 支援的指令。

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

   * `play [black|white] <vertex: string>`
      * 走一手棋到盤面上，必須是合法手。參數中的 vertex 為 [GTP vertex](https://www.lysator.liu.se/~gunnar/gtp/gtp2-spec-draft2/gtp2-spec.html#SECTION00042000000000000000) ，例如 ```a1```、```a2```、```e5``` 等座標位置或是 pass 代表虛手，resign 代表投降。

   * `genmove [black|white]`
      * 讓引擎思考並產生下一手棋到盤面上。

   * `undo`
      * 悔棋。

   * `clear_board`
      * 清空盤面，重新新的一局。

   * `boardsize <size: integer>`
      * 設定不同的盤面大小。注意，dlgo 的神經網路接受的盤面大小是固定的，隨意調整可能使程式崩貴退出。

   * `komi <komi: float>`
      * 設定不同的貼目。注意，dlgo 的網路輸出勝率不會因貼目改變而動態調整。

   * `time_settings <main time: integer> <byo time: integer> <byo stones: integer>`
      * 設定初始的時限並重新計時， ```main time``` 為基本思考時間，```byo time``` 為讀秒思考時間，```byo stones``` 為讀秒內要下的棋手數，僅支援加拿大讀秒（Canadian byo-yomi）規則。

   * `time_left [black|white] <main time: integer> <byo time: integer> <byo stones: integer>`
      * 設定某方剩餘的時限。

   * `analyze [black|white] <interval: integer>`
      * 背景分析結果，詳細指令的參數可到[這裡](https://github.com/SabakiHQ/Sabaki/blob/master/docs/guides/engine-analysis-integration.md)查看。
      
   * `genmove_analyze [black|white] <interval: integer>`
      * 讓引擎思考並產生下一手棋到盤面上並在背景送出分析結果，詳細指令的參數可到[這裡](https://github.com/SabakiHQ/Sabaki/blob/master/docs/guides/engine-analysis-integration.md)查看。

## 三、其它 KGS 可用指令

有些指令在 KGS 上有特殊效果，或是可以提供更多功能，如果有興趣的話，可以優先實作下列指令，指令的參數和效果可到 [GTP 英文文檔](https://www.gnu.org/software/gnugo/gnugo_19.html)查看

   * `final_status_list [alive|dead]`
      * 顯示當前盤面的死棋和活棋棋串。GNU Go 還有實做其它種類的判斷，如 ```seki```、 ```white_territory```、 ```black_territory``` 和 ```dame```。

   * `place_free_handicap <number of handicap: integer>`
      * 讓引擎自己生成讓子的位置。
      
   * `set_free_handicap <list of vertex: string>`
      * 使用者告訴電腦讓子的位置。
      
   * `kgs-genmove_cleanup [black|white]`
      * KGS 專用的生成合法手的指令，禁止虛手直到盤面沒有死棋為止，用以清除盤面死棋。
      
   * `kgs-time_settings ...`
      * KGS 專用的時間控制指令，相比原版的多支援 Byo-Yomi 讀秒規則，詳情請看[這裡](https://www.gokgs.com/help/timesystems.html)。
      
   * `kgs-game_over`
      * 當每盤對戰結束，會發出此指令。
