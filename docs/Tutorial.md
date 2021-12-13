# 教學

## 零、依賴與來源

以下是部份程式碼和資源的來源
1. sgf.py 修改自 [jtauber/sgf](https://github.com/jtauber/sgf)
2. board.py 修改自 [ymgaq/Pyaq](https://github.com/ymgaq/Pyaq)
3. sgf.zip 來源自 [ymgaq/Pyaq](https://github.com/ymgaq/Pyaq)

以下的 python 依賴庫需要安裝（請注意本程式使用 python3）
1. PyTorch（1.x 版本，如果要使用 GPU 請下載對應的 CUDA/cuDNN 版本）
2. NumPy
3. Tkinter（僅使用內建的圖形界面需要，默認是不需要的）
3. Matplotlib（僅訓練時需要，或是訓練時使用 --noplot 禁用此庫）

以下程式需要 Java
1. KGS GTP

## ㄧ、訓練網路

dlgo 可以解析 SGF 格式的棋譜，並將棋譜作為訓練資料訓練一個網路，通過以下步驟可以訓練出一個基本網路。

#### 第一步、收集棋譜

需要收集訓練的棋譜，如果你沒有可使用的棋譜，可以使用附的 sgf.zip，裡面包含三萬五千盤左右的九路棋譜。也可以到 [Aya](http://www.yss-aya.com/ayaself/ayaself.html) 上找到更多可訓練的棋譜。

#### 第二步、設定網路大小

網路的參數包含在 config.py 裡，所需要用到的參數如下

| 參數              | 說明              |
| :---------------: | :---------------: |
| BLOCK_SIZE        | 殘差網路的 block 的數目，數目越大網路越大 |
| FILTER_SIZE       | 卷積網路 filter 的數目，數目越大網路越大  |
| BOARD_SIZE        | 棋盤大小，必須和棋譜的大小一致            |
| USE_GPU           | 是否使用 GPU 訓練。如果為 True ，會自動檢查是否有可用的 GPU ，如果沒有檢測到 GPU ，則會使用 CPU 訓練，如果為 False ，則強制使用 CPU 訓練。此參數建議使用 True |


#### 第三步、開始訓練

接下來便是開始訓練一個網路，所需要用到的參數如下
    
| 參數                 |參數類別            | 說明              |
| :---------------:    | :---------------: | :---------------: |
| -d, --dir            | string            | 要訓練的 SGF 檔案夾|
| -s, --step           | integer           | 要訓練的步數，越多訓練時間越久 |
| -b, --batch-size     | integer           | 訓練的 batch size，建議至少大於 128 ，太低會無法訓練 |
| -l, --learning-rate  | float             | 學習率大小 ，建議從 0.001 開始|
| -w, --weights-name   | string            | 要輸出的網路權重名稱 |
| --load-weights       | string            | 載入其它權重，可以從此權重繼續開始訓練 |
| --noplot             | NA                | 訓練完後不要使用 Matplotlib 繪圖 |

以下是訓練範例命令

    $ python3 train.py --dir sgf-directory-name --step 128000 --batch-size 512 --learning-rate 0.001 --weights-name weights

在一台有配備獨立顯示卡的電腦，大概數個小時內可以完成訓練，如果使用 CPU 訓練大概需要幾天時間。當網路權重出現後，就完成第一步的訓練了。如果你對當前的訓練結果不滿意，可到[這裏](https://github.com/CGLemon/pyDLGO/blob/master/docs/Trainig.md)查看一些訓練時的小技巧。

## 二、啟動引擎

### Linux/MacOS

啟動引擎有三個參數是比較重要的

| 參數             |參數類別          | 說明                |
| :------------: | :---------------: | :---------------: |
| -w, --weights  | string            | 要使用的網路權重名稱，如果沒給則使用 random 的權重|
| -p, --playouts | integer           | MCTS 的 playouts，數目越多越強。預設值是 400 |
| -r, --resign-threshold | float     | 投降的門檻，0.1 代表勝率低於 10% 就會投降。預設值是 0.1 |
| -g, --gui      | NA                | 使用內建的圖形界面。|

注意再啟動以前，必須確定你有權限打開 dlgo.py ，如果沒有，請先使用 chmod 指令更改權限，以下是啟動的範例

    $ chmod 777 dlgo.py
    $ ./dlgo.py --weights weights-name --playouts 1600 -r 0.25

啟動之後，可以試試輸入 GTP 指令 'showboard' ，看看是否有正常運作，順利的話可以看到以下輸出

    showboard
       A  B  C  D  E  F  G  H  J 
     9 .  .  .  .  .  .  .  .  .  9
     8 .  .  .  .  .  .  .  .  .  8
     7 .  .  .  .  .  .  .  .  .  7
     6 .  .  .  .  .  .  .  .  .  6
     5 .  .  .  .  .  .  .  .  .  5
     4 .  .  .  .  .  .  .  .  .  4
     3 .  .  .  .  .  .  .  .  .  3
     2 .  .  .  .  .  .  .  .  .  2
     1 .  .  .  .  .  .  .  .  .  1
       A  B  C  D  E  F  G  H  J 

    = 
    

### Windows

Windows 系統是無法直接使用此程式，這裏需要更改的部分是 dlgo.py 內的第一行，需要改成當前環境所執行 python 路徑位置，此行就是

    #!/usr/bin/env python3

由於此路徑是基於 Linux/MacOS ，所以無法直接在 Windows 上使用，這裏有[討論串](https://superuser.com/questions/378477/making-usr-bin-env-python-work-on-windows)教導如何在 Windows 上可以 work，請跟據你的電腦的 python 執行檔路徑更改此行，以下是範例

    #!c:/Python/python.exe
    
接下來參考上方 Linux/MacOS 的部分啟動引擎。

## 三、使用 GTP 介面

dlgo 支援基本的 GTP 介面，你可以使用任何支援 GTP 軟體，比如用 [Sabaki](https://sabaki.yichuanshen.de) 將 dlgo 掛載上去，使用的參數參考第二部份。以下是如何在 Sabaki 上使用的教學。

#### 第一步、打開引擎選項

![step_one](https://github.com/CGLemon/pyDLGO/blob/master/img/screenshot_sabaki_01.png)

#### 第二步、新增引擎

![step_two](https://github.com/CGLemon/pyDLGO/blob/master/img/screenshot_sabaki_02.png)

#### 第三步、加載引擎

![step_two](https://github.com/CGLemon/pyDLGO/blob/master/img/screenshot_sabaki_03.png)

設置完成後就可以和 dlgo 對戰了。如果想知道 dlgo 支援哪些 GTP 指令，可到[這裏](https://github.com/CGLemon/pyDLGO/blob/master/docs/dlgoGTP.md)查看。

## 四、在 KGS 上使用

KGS 是一個網路圍棋伺服器，它曾經世界最大、最多人使用的網路圍棋。KGS 除了可以上網下棋以外，還能掛載 GTP 引擎上去，以下將會教學如何將 dlgo 掛載上去。

#### 第一步、下載 KGS 客戶端並註冊

請到 [KGS 官網](https://www.gokgs.com/index.jsp?locale=zh_CN)上下載對應系統的客戶端，如果是 Linux 系統，請選擇 Raw JAR File。接下來到 [KGS 註冊網站](https://www.gokgs.com/register/index.html)創立一個帳號。


#### 第二步、下載 KGS GTP 客戶端

到 [KGS GTP 網站](https://www.gokgs.com/download.jsp)下載專為 GTP 引擎設計的客戶端。

#### 第三步、掛載 GTP 引擎

首先我們需要創建並設定 config.txt 的參數，你可以參考以下直接設定

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

設定完成後就可以輸入以下命令即可掛載引擎

    $ java -jar kgsGtp.jar config.txt
    
詳細的參數說明可以看 [KGS GTP 文件]( http://www.weddslist.com/kgs/how/kgsGtp.html)。注意這是舊版的文件，如果要新版的文件，可以點擊在同個資料夾的 kgsGtp.xhtml，或是輸入以下命令在終端機觀看。

    $ java -jar kgsGtp.jar -h

#### 第四步、和 dlgo 在 KGS 上下棋

登錄 KGS 客戶端（注意，你第一個申請的帳號正在被引擎使用，請申請第二個帳號或使用參觀模式），可以從“新開對局”中找到你的帳號，點擊你的帳號即可發出對局申請。


## 五、參加 TCGA 競賽

TCGA 全名為台灣電腦對局協會，基本上每年會舉辦兩場各類型的電腦對局比賽，當然也包括圍棋。TCGA 的圍棋比賽是使用 KGS 伺服器比賽的，如果你已經能順利掛載引擎到 KGS 上，恭喜你完成第一步比賽的準備。當然 dlgo 還有不少可以改進的空間，接下來可以設法強化 dlgo，希望你能在比賽中獲得好成績。


### 比賽列表

* TCGA 管理的網站這幾年好像有點疏於維護，容易出現錯誤訊息，如果出現錯誤訊息請等幾天或幾個禮拜後再嘗試進去看看。

| 比賽                                             |時間                | 狀態               |
| :------------:                                   | :---------------: | :---------------: |
| [TAAI 2021](https://www.tcga.tw/taai2021/zh_TW/) | 11 月 20 號比賽 | 結束   |


## 六、其他
* dlgo 實做的規則是 [Tromp-Taylor](https://senseis.xmp.net/?TrompTaylorRules)（不同的是禁止自殺）。
