# pyDLGO

基於深度學習的 GTP 圍棋引擎

## 零、依賴與來源

sgf.py 修改自 ([sgf](https://github.com/jtauber/sgf))
board.py 修改自 ([pyaq](https://github.com/ymgaq/Pyaq))
sgf.zip 來源自 ([pyaq](https://github.com/ymgaq/Pyaq))

以下的 python 是必須的（均是 python3）
1. pytorch
2. numpy

KGS GTP 需要 Java

## ㄧ、訓練網路

dlgo 可以解析 sgf 格式的棋譜，並直接訓練一個網路。

第一步、需要收集訓練的棋譜，如果你沒有可使用的棋譜，可以使用附的 sgf.zip，裡面包含三萬盤以上九路棋譜。

第二步、設定網路大小，參數包含在 config.py 裡，BLOCK_SIZE 為殘差網路的 block 數目，數目越大網路越大，FILTER_SIZE 卷積網路 filter 的數目，數目越大網路越大，BOARD_SIZE 為要訓練的棋盤大小，USE_GPU 為是否用使用 GPU 訓練。

第三步、開始訓練，參數如下
    
| 參數                    |參數類別          | 說明                |
| :---------------:    | :---------------: | :---------------: |
| --dir                    | string               | 要訓練的 sgf 檔案夾|
| --step                 | int                    | 要訓練的步數，越多訓練時間越久 |
| --batch-size       | int                    | 訓練的 batch size |
| --learning-rate    |float                  | 學習率大小 |
| --weights-name | string               | 要輸出的網路權重名稱 |

以下是訓練範例

    $ python3 --dir sgf-directory-name --step 128000 --batch-size 512 --learning-rate 0.001 --weights-name weights

當網路出現後，就完成訓練了。

## 二、啟動引擎

### Linux/MacOS

啟動引擎有兩個參數是比較重要的

| 參數             |參數類別          | 說明                |
| :------------: | :---------------: | :---------------: |
| --weights     | string              | 要使用的網路權重名稱 |
| --playouts    | int                   | MCTS 的 playouts，數目越多越強 |

注意再啟動以前，必須確定你有權限打開 dlgo.py ，以下是啟動的範例

    $ chmod 777 dlgo.py
    $ ./dlgo.py --weights weights-name --playouts 1600


### Windows

這裏需要更改的部分是 dlgo.py 內的第一行，需要改成當前環境所執行 python 路徑位置，此行就是

    #!/usr/bin/env python3


由於此路徑是基於 Linux/MacOS ，所以無法直接在 Windows 上使用，這裏有討論如何在 Windows 上可以 work ([討論串](https://superuser.com/questions/378477/making-usr-bin-env-python-work-on-windows))，請根據你的使用環境更改此行，以下是範例

    #!c:/Python/python.exe

## 三、使用 GTP 介面

dlgo支援基本的 GTP 介面，你可以使用任何支援 GTP 軟體（ [Sabaki](https://github.com/SabakiHQ/Sabaki )），掛載 dlgo 上去，使用的參數參考上面。以下是如何在 Sabaki 上使用的教學。

#### 第一步、打開引擎選項
![step_one](https://github.com/CGLemon/pyDLGO/blob/master/img/截圖%202021-08-27%20下午7.44.57.png?raw=true)

#### 第二步、新增引擎
![step_two](https://github.com/CGLemon/pyDLGO/blob/master/img/截圖%202021-08-27%20下午7.45.58.png?raw=true)

#### 第三步、加載引擎
![step_two](https://github.com/CGLemon/pyDLGO/blob/master/img/截圖%202021-08-27%20下午7.56.38.png?raw=true)


## 四、在 KGS 上使用 

KGS 是一個網路圍棋伺服器，它曾經世界最大、最多人使用的網路圍棋。KGS 除了可以上網下棋以外，還能掛載 GTP 引擎上去，以下將會教學如何將 dlgo 掛載上去。

#### 第一步、下載 KGS 客戶端並註冊
請到 ([KGS 官網](https://www.gokgs.com/index.jsp?locale=zh_CN))上下載對應系統的客戶端，如果是 Linux 系統，請選擇 Raw JAR File。接下來到 ([KGS  註冊網站](https://www.gokgs.com/register/index.html)創立一個帳號。


#### 第二步、下載 KGS GTP 客戶端
到 ([KGS GTP 網站](https://www.gokgs.com/download.jsp))下載專為 GTP 引擎設計的客戶端。

#### 第三步、掛載 GTP 引擎

首先我們需要創建並設定 config.txt，你可以參考以下直接設定

    name=帳號
    password=密碼
    room=Computer Go
    mode=custom

    rules=chinese
    rules.boardSize=9
    rules.time=10:00

    undo=f
    reconnect=t
    verbose=t

    engine=dlgo 的路徑和參數


設定完成後就可以輸入以下命令掛載引擎

    $ java -jar kgsGtp.jar config.txt
    
詳細的參數說明可以看 ([KGS GTP 文件]( http://www.weddslist.com/kgs/how/kgsGtp.html))。

#### 第四部、和 dlgo 在 KGS 上下棋
登錄 KGS 客戶端（注意，你第一個申請的帳號正在被引擎使用，請申請第二個帳號或使用參觀模式），從上方列表找到，對局室 -> 對局室列表 -> Social -> Computer Go，你的帳號正在此房間裡，點擊你的帳號即可發出對局申請。


## TODO
* 確認正確性
* 增加 TCGA 訊息
* 增加深度學和蒙蒂卡羅在圍棋上的應用、原理
