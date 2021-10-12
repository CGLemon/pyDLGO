# pyDLGO

自從 AlphaGo 打敗世界冠軍後，電腦圍棋儼然變成深度學習的代名詞，讓不少同學對於電腦圍棋有不小的興趣，但實做一個完整的圍棋引擎並不是只有深度學習而已，還包含許許多多枯燥乏味且需花費大量時間的部份，這令多數同學望而卻步。dlgo 實做一個最低要求的圍棋引擎，它包含圍棋的基本演算法，GTP 界面和 SGF 格式解析器，讓同學可以簡單跳過這些部份，專注於深度學習，輕鬆訓練出明顯強於 GNU Go 的網路，最終目標是幫助同學參加 TCGA 電腦對局競賽。

#### (黑) GNU Go 3.8 vs (白) dlgo 0.1
![vs_gnugo](https://github.com/CGLemon/pyDLGO/blob/master/img/b_gungo_vs_w_dlgo.gif)

## 零、依賴與來源

sgf.py 修改自 [jtauber/sgf](https://github.com/jtauber/sgf)

board.py 修改自 [ymgaq/Pyaq](https://github.com/ymgaq/Pyaq)

sgf.zip 來源自 [ymgaq/Pyaq](https://github.com/ymgaq/Pyaq)

以下的 python 依賴庫是必須的（請注意本程式使用 python3）
1. PyTorch (1.x 版本，如果要使用 GPU 請下載對應的 CUDA/cuDNN 版本)
2. NumPy

KGS GTP 需要 Java

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
| USE_GPU           | 是否用使用 GPU 訓練。如果為 True ，會自動檢查是否有可用的 GPU ，如果沒有檢測到 GPU ，則會使用 CPU 訓練，如果為 False ，則強至使用 CPU 訓練。此參數建議使用 True |


#### 第三步、開始訓練

接下來便是開始訓練一個網路，所需要用到的參數如下
    
| 參數                 |參數類別            | 說明              |
| :---------------:    | :---------------: | :---------------: |
| -d, --dir            | string            | 要訓練的 SGF 檔案夾|
| -s, --step           | int               | 要訓練的步數，越多訓練時間越久 |
| -b, --batch-size     | int               | 訓練的 batch size |
| -l, --learning-rate  | float             | 學習率大小 |
| -w, --weights-name   | string            | 要輸出的網路權重名稱 |
| --load-weights       | string            | 載入其它權重，可以從此權重繼續開始訓練 |

以下是訓練範例命令

    $ python3 train.py --dir sgf-directory-name --step 128000 --batch-size 512 --learning-rate 0.001 --weights-name weights

當網路權重出現後，就完成訓練了。

## 二、啟動引擎

### Linux/MacOS

啟動引擎有三個參數是比較重要的

| 參數             |參數類別          | 說明                |
| :------------: | :---------------: | :---------------: |
| -w, --weights  | string            | 要使用的網路權重名稱 |
| -p, --playouts | int               | MCTS 的 playouts，數目越多越強。預設值是 400 |
| -r, --resign-threshold | float     | 投降的門檻，0.1 代表勝率低於 10% 就會投降。預設值是 0.1 |

注意再啟動以前，必須確定你有權限打開 dlgo.py ，如果沒有，請先使用 chmod 指令更改權限，以下是啟動的範例

    $ chmod 777 dlgo.py
    $ ./dlgo.py --weights weights-name --playouts 1600 -r 0.25


### Windows

Windows 系統是無法直接使用此程式，這裏需要更改的部分是 dlgo.py 內的第一行，需要改成當前環境所執行 python 路徑位置，此行就是

    #!/usr/bin/env python3

由於此路徑是基於 Linux/MacOS ，所以無法直接在 Windows 上使用，這裏有[討論串](https://superuser.com/questions/378477/making-usr-bin-env-python-work-on-windows)教導如何在 Windows 上可以 work，請跟據你的電腦的 python 執行檔路徑更改此行，以下是範例

    #!c:/Python/python.exe
    
接下來參考上方 Linux/MacOS 的部分啟動引擎。

## 三、使用 GTP 介面

dlgo 支援基本的 GTP 介面，你可以使用任何支援 GTP 軟體，比如用 [Sabaki](https://sabaki.yichuanshen.de) 將 dlgo 掛載上去，使用的參數參考上面。以下是如何在 Sabaki 上使用的教學。

#### 第一步、打開引擎選項

![step_one](https://github.com/CGLemon/pyDLGO/blob/master/img/screenshot_sabaki_01.png)

#### 第二步、新增引擎

![step_two](https://github.com/CGLemon/pyDLGO/blob/master/img/screenshot_sabaki_02.png)

#### 第三步、加載引擎

![step_two](https://github.com/CGLemon/pyDLGO/blob/master/img/screenshot_sabaki_03.png)

如果想知道 dlgo 支援哪些 GTP 指令，可到[這裏](docs/dlgoGTP.md)查看。

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


#### 比賽列表

| 比賽                                             |時間                | 狀態               |
| :------------:                                   | :---------------: | :---------------: |
| [TAAI 2021](https://www.tcga.tw/taai2021/zh_TW/) | 11 月 18 號報名截止 | 開始報名   |

## 六、其它
* 如果想利用 dlgo 檔案重新製作其它圍棋引擎，可到[這裏](docs/dlgoAPI.md)查看。
* dlgo 實做的規則是 Tromp-Taylor（但禁止自殺）。

## License

board.py 和  sgf.py 依原作者為 MIT License 條款，剩餘程式皆為 MIT License 條款。


## TODO
* 確認正確性
* 增加程式碼可讀性
* 增加 Tromp-Taylor 規則的解釋
* 增加 SGF 格式的教學
* 增加深度學和蒙蒂卡羅在圍棋上的應用、原理
