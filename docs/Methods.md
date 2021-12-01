# Methods

持續施工中...

## 棋盤資料結構

如果同學們以前有自己嘗試實做圍棋棋盤，可以發現圍棋棋盤和圖論有莫大的關係，首先棋盤大部份點和點之間都是等價的，二來棋盤是一個平面圖，這些圖論性質暗示者在棋盤上找特定元素可能會非常困難，像是找出棋盤上活棋棋串，有些甚至無法保證可以找出來，像是雙活。但慶幸的是，基本常用的資料結構是有定論的，接下來我們要討論如何快速計算棋盤上每一塊棋串的狀態

### MailBox

我們知道如果程式中分支條件越多，性能就會越低，假設我要找棋盤上某一點四周的氣，那就必須用四個中分支條確保不會搜尋到到棋盤外，而且搜尋四周邊是使用次數非常多的功能，為了解決這個問題，我們要使用一個常用的資料結構，MailBox 。我假設有一個大小為五棋盤如下

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




MailBox 的核心概念就是在棋盤外圍加一圈無效區域，這樣就不用判斷是否超出邊界

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


在本程式的實做當中，如果是使用改進前版本的座標表示，則稱為 index ，一般用於輸出盤面資料給他人使用。如果是使用改進後版本的座標表示，則稱為 vertex，，一般用於內部棋盤搜尋。

### 棋串（string）

棋串可以看成是整個棋盤中的子圖（sub-graph）而且它是一個節點循環的圖，我們看看下列結構，board position 是當前盤面，可以看到有兩個黑棋棋串，vertex position 是當前 vertex 的座標數值（一維陣列），string identity 是棋串的 identity，這邊注意的是 identity 指到的位置是整個棋串的 root vertex 位置，像是 identity 為 16 的棋串，其 16 的 vertex 座標必在此棋串內，此位置也為此棋串的根節點，為甚麼要這樣做，稍後再來討論，最後 next position 指向下一個節點位置，而且它們是循環的，像是 identity 為 16 的棋串，他的 next position 串接起來為 (17->18->16) -> (17->18->16) -> ... 無限循環

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
        liberty = 0
        start_pos = identity[vertex] # get start vertex postion

        next_pos = start_pos
        {
            for adjacent in next_pos
                if board[adjacent] == EMPTY
                    liberty += 1

            next_pos = next[next_pos] # go to next vertex postion
        } while(next_pos != start_pos)


### 儲存棋串（string）資訊

剛剛講了 identity 指向棋串的 root vertex，這 root vertex 可以儲存棋串的狀態資訊，當需要用到這些資訊時，不必每次都重算，像是棋串棋子數目，或是棋串氣數等等。資料結構如下


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


### 合併棋串（string）

兩個棋串合併時，只要簡單的交換雙方接觸點的 next position，並把 string identity 和 string stones 更新即可

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


## 影片

可以到[這裡](https://www.youtube.com/watch?v=zHojAp5vkRE)觀看 AlphaGo 原理的講解，雖然有一些錯誤和不清楚的部份，但整體上講的很好，看完大概就可以知道本程式主要的運作原理，但因為此影片講解的是 AlphaGo 版本（2016年）的實做，和本實做有些不一樣的地方

1. 沒有 Fast Rollot
2. 沒有強化學習的部份，僅有監督學習
3. 策略（policy）網路和價值（value）網路前面的捲積層是共享的
4. AlphaGo Zero 原本 17 層的輸入層，本實做修正為 18 層（顏色輸入多一層），這樣訓練上會比較平均（請參考 leela zero）
