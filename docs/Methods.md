# Methods

持續施工中...

## 一、棋盤資料結構

如果同學們以前有自己嘗試實做圍棋棋盤，可以發現圍棋棋盤和圖論有莫大的關係，首先棋盤大部份點和點之間都是等價的，二來棋盤是一個平面圖，這些圖論性質暗示者在棋盤上找特定元素可能會非常困難，像是找出棋盤上活棋棋串，有些甚至無法保證可以找出來，像是雙活。但慶幸的是，基本常用的資料結構是有定論的，接下來我們要討論如何快速計算棋盤上每一塊棋串的狀態

### MailBox

我們知道如果程式中分支條件越多，性能就會越低，假設我要找棋盤上某一點四周的氣，那就必須用四個中分支條確保不會搜尋到到棋盤外，而且搜尋四周邊是使用次數非常多的功能，為了解決這個問題，我們要使用一個棋盤遊戲中常用的資料結構，MailBox 。我假設有一個大小為五棋盤如下

       a b c d e
    1  . . . . .
    2  . . . . .
    3  . . . . .
    4  . . . . .
    5  . . . . .


改進前的資料結構虛擬碼如下（這邊注意是使用一維陣列）

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

棋串可以看成是整個棋盤中的子圖（sub-graph），而且它是一個節點循環的圖，我們看看下列結構，board position 是當前盤面，可以看到有兩個黑棋棋串，vertex position 是當前 vertex 的座標數值（一維陣列），string identity 是棋串的 identity，這邊注意的是 identity 指到的位置是整個棋串的 root vertex 位置，像是 identity 為 16 的棋串，其 16 的 vertex 座標必在此棋串內，此位置也為此棋串的根節點，至於為甚麼要這樣做，稍後再來討論，最後 next position 指向下一個節點位置，而且它們是循環的，像是 identity 為 16 的棋串，他的 next position 串接起來為 (17->18->16) -> (17->18->16) -> ... 無限循環

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

依據不同的圍棋規則，合法手會有不同定義，為了方便討論問題，這裡本程式的實做給予合法手兩個基本條件

1. 此手棋下下去後，最終結果不為零氣，簡單來講就是不能自殺
2. 禁止同一盤棋出現相同盤面（super ko）

先討論第一點不能自殺，避免自殺有三種方式

1. 四周有至少一點為空
2. 四周與自身相同的顏色的棋串，至少一塊棋不為一氣
3. 四周與自身相異的顏色的棋串，至少一塊棋為一氣

    
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

以上其中一個條件滿足，則必不是自殺手。接著討論禁止相同盤面，由於偵測相同盤面會比較消耗計算力，而且相同盤面的情況其實相對罕見，一般我們會用偵測熱子來代替，如果出現吃掉熱子棋況，則為非法手。熱子的定義為

1. 吃到一顆對方的棋子
2. 下的棋子最終結果只有一氣
2. 下的棋子最終結果只有一顆子

       is_ko(vertex):
           if captured_count == 1 &&
                  string_stones[vertex] == 1 &&
                  string_liberties[vertex] == 1
               return true
           return false

此三項都滿足，則必為熱子。

## 二、蒙地卡羅樹搜索（Monte Carlo Tree Search）

### 簡介

蒙地卡羅樹搜索是一種基於啟發式算法，最早由 Crazy Stone 的作者 Rémi Coulom 在 2006 年在他的論文 [<Efficient Selectivity and Backup Operators in Monte-Carlo Tree Search>](https://hal.inria.fr/inria-00116992/document) 中提出，他成功結合 [negamax](http://rportal.lib.ntnu.edu.tw/bitstream/20.500.12235/106643/4/n069347008204.pdf) 和合蒙地卡羅方法，此方法最大的突破點在於，不同以往的圍棋程式，它僅須少量的圍棋知識就可以實做。時至今日，蒙地卡羅樹搜索經歷多次的公式修正和加入更多的啟發式搜索，如傳統的 UCT（Upper Confidence bounds applied to Trees）和 RAVE，和本次程式實做的 [PUCT](https://www.chessprogramming.org/Christopher_D._Rosin#PUCT) （'Predictor' + UCT ）。

### 基本方法

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

AlphaGo Zero 版本的 MCTS 相當簡解，而且去除了模擬步驟，可以說是和跟蒙地卡羅方法毫無關係，所以理論上，此演算法不包含隨機性，由於本程式也是實做此版本的 MCTS 演算法，所以本程式在同個盤面上給相同的計算量時，每次的計算結果都會一致。

### 落子

最後 n 輪的 MCTS 結束後，找根節點上訪問次數最多的子節點當做最佳手輸出。

## 影片

可以到[這裡](https://www.youtube.com/watch?v=zHojAp5vkRE)觀看 AlphaGo 原理的講解，雖然有一些錯誤和不清楚的部份，但整體上講的很好，看完大概就可以知道本程式主要的運作原理，但因為此影片講解的是 AlphaGo 版本（2016年）的實做，和本實做有些不一樣的地方

1. 沒有 Fast Rollot
2. 沒有強化學習的部份，僅有監督學習
3. 策略（policy）網路和價值（value）網路前面的捲積層是共享的
4. AlphaGo Zero 原本 17 層的輸入層，本實做修正為 18 層（顏色輸入多一層），這樣訓練上會比較平均（請參考 leela zero）
