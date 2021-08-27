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

啟動引擎有兩個參數是比較重要的

| 參數             |參數類別          | 說明                |
| :------------: | :---------------: | :---------------: |
| --weights     | string              | 要使用的網路權重名稱 |
| --playouts    | int                   | MCTS 的 playouts，數目越多越強 |

注意再啟動以前，必須確定你有權限打開 dlgo.py ，以下是啟動的範例

    $ chmod 777 dlgo.py
    $ ./dlgo.py --weights weights-name --playouts 1600

## 三、使用 GTP 介面

dlgo支援基本的 GTP 介面，你可以使用任何支援 GTP 軟體（ [Sabaki](https://github.com/SabakiHQ/Sabaki )），掛載 dlgo 上去，使用的參數參考上面。以下是如何在 Sabaki 上使用的教學。

第一步、打開引擎選項
![step_one](https://github.com/CGLemon/pyDLGO/blob/master/img/截圖%202021-08-27%20下午7.44.57.png?raw=true)

第二步、新增引擎
![step_two](https://github.com/CGLemon/pyDLGO/blob/master/img/截圖%202021-08-27%20下午7.45.58.png?raw=true)

第三步、加載引擎
![step_two](https://github.com/CGLemon/pyDLGO/blob/master/img/截圖%202021-08-27%20下午7.56.38.png?raw=true)

## 四、Windows

這裏需要更改的部分是 dlgo.py 內的第一行，需要改成當前環境所執行 python 路徑位置，此行就是

    #!/usr/bin/env python3


由於此路徑是基於 Linux/MacOS ，所以無法直接在 Windows 上使用，這裏有討論如何在 Windows 上可以 work ([討論串](https://superuser.com/questions/378477/making-usr-bin-env-python-work-on-windows))，請根據你的使用環境更改此行，以下是範例

    #!c:/Python/python.exe


## TODO
* 加上如何將引擎掛載在 KGS 上
