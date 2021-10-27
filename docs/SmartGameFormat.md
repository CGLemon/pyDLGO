# Smart Game Format

## ㄧ、歷史
智慧遊戲格式最早來源於 Smart Go ，由其原作者 Anders Kierulf 和後繼者 Martin Mueller ， Arno Hollosi 接力開發，因此早期版本又稱為 Smart Go Format。到了現在 SGF 已經是圍棋軟體預設紀錄儲存棋譜的格式，而且不只是圍棋，其它棋類如，黑白棋，也採用 SGF 格式。

## 二、基本概念
SGF 是以樹狀結構紀錄，每一個節點以 ';' 分隔，每一個樹枝以 '(' 和 ')' 分隔，例如某一樹狀結構為

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

此屬性為 'B' ，括號內的 'aa' 為此屬性的值。如果用 SGF 表示則看起來像

    (;B[aa];W[ab](;B[ac];W[ad])(;B[bc];W[bd];B[bd]))

一些常用的屬性為下

| 屬性            | 說明                |
| :------------: | :---------------: |
| GM               | 遊戲種類，圍棋為 1，必須在 root node |
| FF               | 版本，現行版本為 4 ，必須在 root node |
| KM               | 貼目，必須在 root node |
| SZ               | 盤面大小，必須在 root node |
| DT              | 日期 |
| B                 | 黑棋落子 |
| W                 | 白棋落子 |

## 四、範例
以下是一個 sgf 檔案範例，可用 Sabaki 或是其它支援 SGF 的軟體打開


    (
      ;GM[1]FF[4]CA[UTF-8]AP[Sabaki:0.35.1]KM[7]SZ[9]DT[2021-10-27]
      ;B[dd];W[ff];B[fe];W[ee];B[ed];W[ge];B[fd];W[ef];B[gd]
      (
        ;W[cf];B[ce];W[be];B[bd];W[de];B[cd];W[bf];B[gf];W[gg];B[he];W[hg]
      )
      (
        ;W[ce];B[de];W[df];B[cd];W[bf];B[be];W[cf];B[gf];W[gg];B[he];W[hg];B[bd]
      )
    )

## 五、使用 sgf.py

sgf.py 提供三個 functions 解析 SGF 檔案

   * `parse_from_string(string)`
      * 直接解析 SGF 字串

   * `parse_from_file(string)`
      * 解析包含 SGF 字串的檔案

   * `parse_from_dir(string)`
      * 解析裝有 SGF 檔案的檔案夾，必須注意檔案的後綴必須是 '.sgf' 或是 '.sgfs'

解析出來的結果，是所有的 sgf tree  使用方式如下

    sgf_games = parse_from_string(sgf_strig)
    for game in sgf_games:
        # 每個 game 都是單獨的 sgf tree
        for node in game:
            # 從 root 遍歷 sgf tree 的主要 node
            if "W" in node.properties:
                data = node.properties["W"][0] # 取出屬性值
    
