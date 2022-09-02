# pyDLGO

自從 AlphaGo 打敗世界冠軍後，電腦圍棋儼然變成深度學習的代名詞，讓不少同學對於電腦圍棋有不小的興趣，但實做一個完整的圍棋引擎並不是只有深度學習而已，還包含許許多多枯燥乏味且需花費大量時間的部份，這令多數同學望而卻步。dlgo 實做一個最低要求的圍棋引擎，它包含圍棋的基本演算法、GTP 界面和 SGF 格式解析器，讓同學可以先跳過這些部份，專注於深度學習，體驗電腦圍棋的魅力。最終目標是希望幫助同學製造屬於自己的圍棋引擎，並參加 TCGA 電腦對局競賽。

#### (黑) dlgo-0.1 vs (白) Leela-0.11 (黑中盤勝) 
![vs_leela](./img/dlgo_vs_leela.gif)

## 快速開始

The simple English tutorial is [Here](./docs/English.md)

開始前請先安裝以下的 python 依賴庫（請注意本程式使用 python3）
1. PyTorch（1.x 版本，如果要使用 GPU 請下載對應的 CUDA/cuDNN 版本）
2. NumPy
3. Tkinter

請輸入下列指令安裝，或自行使用下載可執行的版本

    pip3 install -r requirements.txt

完成依賴庫安裝後，首先請先下載本程式碼和預先訓練好的權重，預先訓練好的權重可到 Release 裡找到（為 pt 檔，不需要解壓縮），將權重放到 pyDLGO 的資料夾裡，假設權重的名稱為 nn_2x64.pt ，請輸入以下指令打開圖形界面

    $ python3 dlgo.py --weights nn_2x64.pt --gui

## 文件目錄
0. [圍棋規則的簡單介紹](https://www.smartgo.com/tw/go.html)
1. [完整的操作教學和 TCGA 比賽](./docs/Tutorial.md)
2. [演算法實做和原理（持續施工中）](./docs/Methods.md)
3. [GTP 界面原理](./docs/dlgoGTP.md)
4. [SGF 格式說明](./docs/SmartGameFormat.md)
5. [board.py 內的 functions](./docs/dlgoAPI.md)
6. [Python 圍棋引擎列表（歡迎添加）](./docs/PyGoEngine.md)

## License

MIT License

## Todo
* 修復 GUI 的 bug 並優化之
* 訓練十九路權重
* 支援 ```analyze``` 和 ```genmove_analyze``` 指令，利於分析
* 實做 AlphaGo Zero pipe？

### 聯絡資訊

如果有任何問題或是建議，可以通過 ```cglemon000@gmail.com``` 聯繫我。
