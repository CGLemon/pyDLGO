# Smart Game Format

## ㄧ、歷史
智慧遊戲格式 (Smart Game Format) 最早來源於 Smart Go ，由其原作者 Anders Kierulf 和後繼者 Martin Mueller ， Arno Hollosi 接力開發，因此早期版本稱為智慧圍棋格式 (Smart Go Format)。到了現在 SGF 已經是圍棋軟體預設紀錄儲存棋譜的格式，而且不只是圍棋，其它棋類如，黑白棋，也多採用 SGF 格式。

## 二、基本概念
SGF 是以樹狀結構紀錄，每一個節點以 ```;``` 分隔，每一個樹枝以 ```(``` 和 ```)``` 分隔，例如某一樹狀結構為

          |a
          |b
        f/ \c
       g/   \d
             \e
             
則其 SGF 結構為

    (;a;b(;f;g)(;c;d;e))

## 三、屬性

每個節點都有屬性(property)資料，他的表示法為下

    B[aa]

此屬性為 ```B``` ，括號內的 ```aa``` 為此屬性的值。如果用 SGF 表示則看起來像

    (;B[aa];W[ab](;B[ac];W[ad])(;B[bc];W[bd];B[bd]))

每個節點也可以包含多個屬性資料

    (;B[aa]C[Hello])

一些常用的屬性列在下方，如果想要了解更多屬性種類可到 [SGF Wiki](https://en.wikipedia.org/wiki/Smart_Game_Format)

| 屬性            | 說明                |
| :------------: | :---------------: |
| GM               | 遊戲種類，圍棋為 1，必須在 root node |
| FF               | 版本，現行版本為 4 ，必須在 root node |
| RU               | 使用的規則，必須在 root node |
| RE               | 勝負的結果，必須在 root node |
| KM               | 貼目，必須在 root node |
| SZ               | 盤面大小，必須在 root node |
| AP               | 使用的軟體，必須在 root node |
| HA               | 讓子數目，必須在 root node |
| AB               | 初始盤面的黑棋落子位置，必須在 root node |
| AW               | 初始盤面的白棋落子位置，必須在 root node |
| PB               | 黑棋玩家名稱，必須在 root node |
| PW               | 白落玩家名稱，必須在 root node |
| DT               | 日期，必須在 root node |
| B                | 黑棋落子座標 |
| W                | 白棋落子座標 |
| C                | 評論 |

<br>

## 四、範例
以下是一個 SGF 檔案範例，可用 Sabaki 或是其它支援 SGF 的軟體打開

    (
      ;GM[1]FF[4]CA[UTF-8]AP[Sabaki:0.43.3]KM[7.5]SZ[19]DT[2021-10-31]HA[2]AB[dp][pd]PB[Black Player]PW[White Player]
      ;W[qp];B[dd];W[fq];B[cn];W[kq]
      (
        ;B[qf];W[fc];B[df];W[jd];B[lc];W[pk];B[op];W[pn];B[qq];W[rq];B[pq];W[rr];B[mq];W[ko]
      )
      (
        ;B[df];W[qf];B[nc];W[pj];B[op]
      )
    )

其中座標的表示法為 ```a~z```，如 ```B[ab]``` 代表黑棋下在 (1,2) 的位置。而虛手，在十九路或小於十九路的棋盤裡，可用 ```[tt]``` 或是 ```[]``` 代表，但如果棋盤超過十九路，則 ```[tt]``` 代表 (20,20) 的位置，只有 ```[]``` 代表虛手。至於投降手沒有統一的表示方式，通常是不會紀錄在棋譜裡。

## 五、使用 sgf.py

sgf.py 提供三個 functions 解析 SGF 檔案

   * `parse_from_string(string)`
      * 直接解析 SGF 字串

   * `parse_from_file(string)`
      * 解析包含 SGF 字串的檔案

   * `parse_from_dir(string)`
      * 解析裝有 SGF 檔案的檔案夾，必須注意檔案的後綴必須是 ```.sgf``` 或是 ```.sgfs```

解析出來的結果，是包含每個棋譜的 sgf tree 的資料，使用方式如下

    sgf_games = parse_from_string(sgf_strig)
    for game in sgf_games:
        # 每個 game 都是單獨的 sgf tree
        for node in game:
            # 從 root 遍歷 sgf tree 的主要 node
            if "W" in node.properties:
                data = node.properties["W"][0] # 取出屬性值
    
