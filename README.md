# pyDLGO

基於深度學習的 GTP 圍棋引擎

## ㄧ、訓練網路

dlgo 可以解析 sgf 格式的棋譜，並直接訓練一個網路。

第一步、需要收集訓練的棋譜，如果你沒有可使用的棋譜，可以使用附的 sgf.zip，裡面包含三萬盤以上九路棋譜。

第二步、設定網路大小，參數包含在 config.py 裡，BLOCK_SIZE 為殘差網路的 block 數目，數目越大網路越大，FILTER_SIZE 卷積網路 filter 的數目，數目越大網路越大，BOARD_SIZE 為要訓練的棋盤大小，USE_GPU 為是否用使用 GPU 訓練。

第三部、開始訓練

    $ python3 --dir sgf-directory-name --step 128000 --batch-size 512 --learning-rate 0.001 --weights-name weights

當網路出現後，就完成訓練了。

## 二、啟動引擎

    $ ./dlgo.py --weights weights-name --playouts 1600

--weights：要使用的網路權重名稱。

--playouts：MCTS 的 playouts，數目越多越強。

## 三、使用 GTP 介面

dlgo支援基本的 GTP 介面，你可以使用任何支援 GTP 軟體（ [Sabaki](https://github.com/SabakiHQ/Sabaki )），掛載 dlgo 上去，使用的參數參考上面。

## TODO
* 加入圖片說明
* 加上如何在 KGS 使用
* 支援 windows
