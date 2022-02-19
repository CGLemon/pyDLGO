# Methods

## 一、棋盤資料結構

如果同學們以前有自己嘗試實做圍棋棋盤，應該可以發現圍棋棋盤和圖論有莫大的關係，首先棋盤大部份點和點之間是等價的，二來棋盤是一個平面圖，這些圖論性質暗示者在棋盤上找某些特定元素可能會非常困難，像是找出棋盤上活棋棋串，有些甚至無法保證可以找出來，像是雙活。慶幸的是，基本常用的資料結構是有定論的，接下來我們要討論如何快速計算棋盤上每一塊棋串的狀態

### MailBox

我們知道如果程式中分支條件越多，性能就會越低，假設我要找棋盤上某一點四周的氣，那就必須用四個分支條確保不會搜尋到到棋盤外，而且搜尋四周邊是使用次數非常多的功能，這將會有巨大的性能消耗，為了解決這個問題，我們要使用一個棋盤遊戲中常用的資料結構，MailBox 。假設我有一個大小為五棋盤如下

       a b c d e
    1  . . . . .
    2  . . . . .
    3  . . . . .
    4  . . . . .
    5  . . . . .


改進前的資料結構虛擬碼如下（注意這邊是使用一維陣列）

    BLACK = 0
    WHITE = 1
    EMPTY = 2
    INVLD = 3 # out of board value

    find_adjacent(index):
        type_count[4] = {0,0,0,0}

        for adjacent in index
            if adjacent is out of board
                type_count[INVLD] += 1
            else
                type = board[adjacent]
                type_count[type] += 1


MailBox 的核心概念就是在棋盤外圍加一圈無效區域（標示為 '-' 的位置），這樣就不用特別判斷是否超出邊界

        a b c d e
      - - - - - - -
    1 - . . . . . -
    2 - . . . . . -
    3 - . . . . . -
    4 - . . . . . -
    5 - . . . . . -
      - - - - - - -

改進後的資料結構虛擬碼如下，可以看見不僅性能提，整個程式碼也簡潔不少

    BLACK = 0
    WHITE = 1
    EMPTY = 2
    INVLD = 3 # out of board value

    find_adjacent(vertex):
        type_count[4] = {0,0,0,0}

        for adjacent in vertex
            type_count[type] += 1


在本程式的實做當中，如果是使用改進前版本的座標表示法，則稱為 index ，一般用於輸出盤面資料給外部使用。如果是使用改進後版本的座標表示法，則稱為 vertex，，一般用於內部棋盤搜尋。

### 棋串（string）

棋串可以看成是整個棋盤中的子圖（sub-graph），而且它是一個節點循環的圖，我們來看看下列結構，board position 是當前盤面，可以看到有兩個黑棋棋串，vertex position 是當前 vertex 的座標數值（一維陣列），string identity 是棋串的 identity，這邊注意的是 identity 指到的位置是整個棋串的 root vertex 位置，像是 identity 為 16 的棋串，其 16 的 vertex 座標必在此棋串內，此位置也為此棋串的根節點，至於為甚麼要這樣做，稍後再來討論，最後 next position 指向下一個節點位置，而且它們是循環的，像是 identity 為 16 的棋串，他的 next position 串接起來為 (17->18->16) -> (17->18->16) -> ... 無限循環

    board position
       a b c d e
    1| . . . . .
    2| . x x x .
    3| . . . . .
    4| . x x . .
    5| . . . . .
        
    vertex position
       a  b  c  d  e
    1| 8  9  10 11 12
    2| 15 16 17 18 19
    3| 22 23 24 25 26
    4| 29 30 31 32 33
    5| 36 37 38 39 40

    string identity
       a  b  c  d  e
    1| .  .  .  .  .
    2| .  16 16 16 .
    3| .  .  .  .  .
    4| .  30 30 .  .
    5| .  .  .  .  .

    next position
       a  b  c  d  e
    1| .  .  .  .  .
    2| .  17 18 16 .
    3| .  .  .  .  .
    4| .  31 30 .  .
    5| .  .  .  .  .


假設今天我們要找一個棋串的氣，只要從一個節點開始走下去，依序計算直到走到原位置，虛擬碼如下

    conut_liberty(vertex):
        start_pos = identity[vertex] # get the start vertex postion

        next_pos = start_pos
        liberty_set = set()
        {
            for adjacent in next_pos
                if board[adjacent] == EMPTY
                    liberty_set.add(adjacent) # add the adjacent vertex to set

            next_pos = next[next_pos] # go to next vertex postion
        } while(next_pos != start_pos)

        liberties = length(liberty_set)


### 儲存棋串（string）資訊

剛剛講了 identity 指向棋串的 root vertex，這 root vertex 可以儲存棋串的狀態資訊，當需要用到這些資訊時，不必每次都重算，像是棋串棋子數目，或是棋串氣數等等。本程式實做的資料結構如下


    string identity
       a  b  c  d  e
    1| .  .  .  .  .
    2| .  16 16 16 .
    3| .  .  .  .  .
    4| .  30 30 .  .
    5| .  .  .  .  .


    string stones
       a  b  c  d  e
    1| .  .  .  .  .
    2| .  3  .  .  .
    3| .  .  .  .  .
    4| .  2  .  .  .
    5| .  .  .  .  .

    string liberty set
       a  b  c  d  e
    1| .  .  .  .  .
    2| .  A  .  .  .
    3| .  .  .  .  .      # A = liberty set of string 16
    4| .  B  .  .  .      # B = liberty set of string 30
    5| .  .  .  .  .


### 合併棋串（string）

兩個棋串合併時，只要簡單的交換雙方接觸點的 next position，並把 string identity 、string stones 和 string liberty set 更新即可，如下所示。如果是多個棋串合併，只要簡單的把兩兩棋串一個個合併就好。

    board position
       a  b  c  d  e
    1| .  .  .  .  .
    2| .  x  x  x  .
    3| . [x] .  .  .
    4| .  x  .  .  .
    5| .  .  .  .  .

    Merge two strings...

    string identity
       a  b  c  d  e             a  b  c  d  e
    1| .  .  .  .  .          1| .  .  .  .  .
    2| .  16 16 16 .          2| .  16 16 16 . 
    3| .  30 .  .  .    >>    3| .  16 .  .  .
    4| .  30 .  .  .          4| .  16 .  .  .
    5| .  .  .  .  .          5| .  .  .  .  .

    next position
       a  b  c  d  e             a  b  c  d  e
    1| .  .  .  .  .          1| .  .  .  .  .
    2| .  17 18 16 .          2| .  30 18 16 .
    3| .  30 .  .  .    >>    3| .  17 .  .  .
    4| .  23 .  .  .          4| .  23 .  .  .
    5| .  .  .  .  .          5| .  .  .  .  .

    string stones
       a  b  c  d  e             a  b  c  d  e
    1| .  .  .  .  .          1| .  .  .  .  .
    2| .  3  .  .  .          2| .  5  .  .  .
    3| .  .  .  .  .    >>    3| .  .  .  .  .
    4| .  2  .  .  .          4| .  .  .  .  .
    5| .  .  .  .  .          5| .  .  .  .  .


    string liberty set
       a  b  c  d  e             a  b  c  d  e
    1| .  .  .  .  .          1| .  .  .  .  .
    2| .  A  .  .  .          2| .  C  .  .  .
    3| .  .  .  .  .    >>    3| .  .  .  .  .    # set C = set A + set B
    4| .  B  .  .  .          4| .  .  .  .  .
    5| .  .  .  .  .          5| .  .  .  .  .


### 偵測合法手

依據不同的圍棋規則，合法手會有不同定義，為了方便討論問題，這裡依據本程式的實做給予合法手兩個基本條件

1. 此手棋下下去後，最終結果不為零氣，簡單來講就是不能自殺
2. 禁止同一盤棋出現相同盤面（super ko）

先討論第一點不能自殺，避免自殺有三種方式

1. 四周至少有一點為空點
2. 四周與自身相同的顏色的棋串，至少一塊棋超過一氣
3. 四周與自身相異的顏色的棋串，至少一塊棋為一氣（提吃）

    
       is_suicide(vertex):
           for adjacent in vertex
               if board[adjacent] == EMPTY
                   return false
       
               if board[adjacent] == MY_COLOR &&
                      string_liberties[adjacent] > 1:
                   return false
       
               if board[adjacent] == OPP_COLOR &&
                      string_liberties[adjacent] == 1:
                   return false
           return true

以上其中一個條件滿足，則必不是自殺手。接著討論禁止相同盤面，由於偵測相同盤面會比較消耗計算力，而且相同盤面的情況其實相對罕見，一般我們以偵測熱子為主，如果出現吃掉熱子棋況，則為非法手。熱子的定義為

1. 吃到一顆對方的棋子
2. 下的棋子最終結果只有一氣
3. 下的棋子最終結果只有一顆子

       is_ko(vertex):
           if captured_count == 1 &&
                  string_stones[vertex] == 1 &&
                  string_liberties[vertex] == 1
               return true
           return false

此三項都滿足，則必為熱子。如果必須偵測相同盤面，就沒有特別的算法，只能實際將棋子擺到棋盤上後，再看是否當前盤面和歷史盤面有重複。

## 二、審局函數

最早期的圍棋程式是沒有審局函數的，這是由於圍棋局勢多變缺乏明顯特徵，致使一直以來製作審局函數都是一個大難題，但自從深度學習開始興起，審局函數的問題便迎刃而解。這裡主要是對審局函數的一些基本描述，並不會涉及大多深度學習的部份，有興趣者可自行上網查詢。

### 基本狀態

假設今天有一個狀態 <img src="https://render.githubusercontent.com/render/math?math=\Large S"> （當前盤面），它擁有數個動作 <img src="https://render.githubusercontent.com/render/math?math=\Large A_i"> （合法手），執行動作者為代理人 <img src="https://render.githubusercontent.com/render/math?math=\Large Agent"> （程式本體），我們會希望從當前狀態得到兩類資訊，第一類是策略（policy）資訊，告訴代理人哪些動作值得被執行或是搜尋，在 AlphaGo 的實做中，此為合法手的機率分佈，第二類為價值（value）資訊，告訴代理人當前狀態的分數或是每個動作的分數在 AlphaGo 的實做中，此為當前盤面的分數（也能視為勝率），如下所示

![policy_value](https://github.com/CGLemon/pyDLGO/blob/master/img/policy_value.gif)

### 訓練審局函數

我們收集當前狀態、下一步棋和本局的勝負當作訓練的資料，收集的結果為下

| 當前狀態       | 落子座標           | 勝負結果          |
| :------------: | :---------------: | :---------------: |
| S1（換黑棋落子）| 'e5'              | 黑棋獲勝          |
| S2（換白棋落子）| 'd3'              | 黑棋獲勝          |
| S3（換黑棋落子）| 'e5'              | 白棋獲勝          |
| S4（換白棋落子）| 'd3'              | 白棋獲勝          |


接下來將資料轉換成網路看得懂的資料，在本實做中，當前狀態過去的八手棋（每手棋包含黑白兩個 planes）和當前盤面做編碼（兩個 planes），編碼成 18 個 planes（可到 board.py 裡的 get_features() 查看如何實做），落子座標轉成一維陣列，勝負結果如果是當前玩家獲勝則是 1，如果落敗則為 -1。轉換的結果如下

| 當前狀態       | 落子座標           | 勝負結果          |
| :------------: | :---------------: | :---------------: |
| Inputs 1       | 40                | 1                 |
| Inputs 2       | 21                | -1                |
| Inputs 3       | 40                | -1                |
| Inputs 4       | 21                | 1                 |

網路希望的優化結果為下

![loss](https://github.com/CGLemon/pyDLGO/blob/master/img/loss.gif)

其中 

<img src="https://render.githubusercontent.com/render/math?math=\Large R_t"> 為資料的勝負結果

<img src="https://render.githubusercontent.com/render/math?math=\Large R_o"> 為網路數出的 value

<img src="https://render.githubusercontent.com/render/math?math=\Large P_t"> 為資料的落子座標陣列

<img src="https://render.githubusercontent.com/render/math?math=\Large P_o"> 為網路數出的 policy

<img src="https://render.githubusercontent.com/render/math?math=\Large WeightDecay"> 為對網路參數的懲罰項

當然這不是唯一的編碼方式，像是 ELF Open Go 的勝負結果只看黑棋的一方，如下方

| 當前狀態       | 落子座標           | 勝負結果          |
| :------------: | :---------------: | :---------------: |
| Inputs 1       | 40                | 1                 |
| Inputs 2       | 21                | 1                 |
| Inputs 3       | 40                | -1                |
| Inputs 4       | 21                | -1                |

## 三、蒙地卡羅樹搜索（Monte Carlo Tree Search）

蒙地卡羅樹搜索是一種啟發式算法，最早由 Crazy Stone 的作者 Rémi Coulom 在 2006 年在他的論文 [Efficient Selectivity and Backup Operators in Monte-Carlo Tree Search](https://hal.inria.fr/inria-00116992/document) 中提出，他成功結合 [negamax](http://rportal.lib.ntnu.edu.tw/bitstream/20.500.12235/106643/4/n069347008204.pdf) 和蒙地卡羅方法，此方法最大的突破點在於，不同以往的圍棋程式，它僅須少量的圍棋知識就可以實做。時至今日，蒙地卡羅樹搜索經歷多次的公式修正和加入更多的啟發式搜索，如傳統的 UCT（Upper Confidence bounds applied to Trees）和 RAVE，和本次程式實做的 [PUCT](https://www.chessprogramming.org/Christopher_D._Rosin#PUCT) （'Predictor' + UCT ）。

### 蒙地卡羅方法（Monte Carlo Method）

蒙地卡羅方法的核心概念非常簡單，要知道某件事情發生的機率，我們只要模擬數次就可以得到近似發生的機率，但為何需要如此費力且不完全準確的方法呢？我以擲筊為例，大家應該都對筊杯不陌生，當生活遇到瓶頸時，或多或少都會有人擲筊請示神明，但不知道是否有人想過，擲出聖杯的機率到底是多少，依照古典算法，假設擲出正反兩面的機率是二分之一，那麼聖杯的機率是二分之一（笑杯也加入計算），但很顯然的，由於筊杯兩面不是對稱的，所以機率絕對不是二分之一。在一般情況下，擲出聖杯的機率是沒有辦法僅依靠計算得出的，此時蒙地卡羅方法就展現他的威力的，我只需要重複投擲一萬次，再計算共幾次聖杯即可。同樣的在圍棋上，由於圍棋的複雜性，早期圍棋是很難得出較為準確的勝率，但通過蒙地卡羅方法，讓同一個盤隨機模擬數次，即可算出一個相對來說較為可靠的勝率。

### 基本的 UCT

<div align=center>
<img src="https://github.com/CGLemon/pyDLGO/blob/master/img/mcts.png" align=center/>
</div>

傳統的 MCTS 的每輪迭代更新會經歷基本的四個步驟

1. 選擇：
由根節點開始，根據一定的選擇算法，找到一個葉節點（終端節點），傳統的 MCTS 會使用 UCT 作為選擇的依序，它的公式如下

![ucb](https://github.com/CGLemon/pyDLGO/blob/master/img/ucb.gif)

其中 

<img src="https://render.githubusercontent.com/render/math?math=\Large w_i"> 表示節點累積的分數（或勝利次數）

<img src="https://render.githubusercontent.com/render/math?math=\Large n_i"> 表示節點訪問次數

<img src="https://render.githubusercontent.com/render/math?math=\Large C"> 表示探勘的參數

<img src="https://render.githubusercontent.com/render/math?math=\Large N"> 表示父節點的訪問次數

2. 擴張：
將被選到的葉節點，生長新的子節點。新的子節點代表新的走步

3. 模擬：
使用蒙地卡羅（Monte Carlo Method）方法，計算第一步驟中被選到的葉節點的分數（或勝率）

4. 迭代：
延著被選擇的路徑，依序迭代路徑更新分數（或勝率），迭代的節點訪問次數加一

如果有仔細看的話，會發現我對於四個步驟的描述和圖片稍有不一樣，但其實只是敘述方式不太一樣，計算結果會是一樣的。

### PUCT 的改進

<div align=center>
<img src="https://github.com/CGLemon/pyDLGO/blob/master/img/alphago_zero_mcts.jpg" align=center/>
</div>

2017 年的 AlphaGo Zero 提出改進過的 MCTS 演算法，主要兩點不同，第一點是用 PUCT 取代 UCT 找尋節點，第二就是移除模擬的過程，所以只會重複三個步驟。

1. 選擇：
由根節點開始，根據 PUCT 選擇算法，找到一個葉節點（終端節點，此節點尚無價值數值）

![puct](https://github.com/CGLemon/pyDLGO/blob/master/img/puct.gif)

其中 

<img src="https://render.githubusercontent.com/render/math?math=\Large w_i"> 表示節點累積的價值數值（即累積的勝率）

<img src="https://render.githubusercontent.com/render/math?math=\Large n_i"> 表示節點訪問次數

<img src="https://render.githubusercontent.com/render/math?math=\Large C_{puct}"> 表示探勘的參數

<img src="https://render.githubusercontent.com/render/math?math=\Large N"> 表示父節點的訪問次數

<img src="https://render.githubusercontent.com/render/math?math=\Large P"> 表示節點的策略數值（即父節點走此節點的機率）

2. 擴張：
將被選到的葉節點，生長新的子節點。新的子節點代表新的走步，並將神經網路策略數值加入新的子節點，價值數值加到第一步驟中被選到的葉節點上

3. 迭代：
延著被選擇的路徑，依序迭代路徑更新價值數值（即勝率），迭代的節點訪問次數加一

AlphaGo Zero 版本的 MCTS 相當精簡，並且去除了模擬步驟，整體來講可以說是和跟蒙地卡羅方法毫無關係，理論上，此演算法不包含隨機性，由於本程式也是實做此版本的 MCTS 演算法，所以本程式在同個盤面上給相同的計算量時，每次的計算結果都會一致。

### 落子

最後 n 輪的 MCTS 結束後，找根節點上訪問次數最多的子節點當做最佳手輸出。


## 四、 NN Cache

2018 年 Leela Zero 團隊提出 nn cache 並實作，它將每次的網路運算結果存入 cache ，下次要再使用時，就不需要重新運算，直接從 cache 中拿出即可。由於每次蒙地卡羅會有部分的節點會重複計算，因此它可以加速蒙蒂卡羅迭代的速度。

## 五、影片

可以到[這裡](https://www.youtube.com/watch?v=zHojAp5vkRE)觀看 AlphaGo 原理的講解，雖然有一些錯誤和不清楚的部份，但整體上講的很好，看完大概就可以知道本程式主要的運作原理，但因為此影片講解的是 AlphaGo 版本（2016年）的實做，和本實做有些不一樣的地方

1. 沒有 Fast Rollot
2. 沒有強化學習的部份，僅有監督學習
3. 策略（policy）網路和價值（value）網路前面的捲積層是共享的
4. AlphaGo Zero 原本 17 層的輸入層，本實做修正為 18 層（顏色輸入多一層），這樣訓練上會比較平均（請參考 Leela Zero）
