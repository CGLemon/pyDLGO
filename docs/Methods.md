# Methods

持續施工中...

## 影片

可以到[這裡](https://www.youtube.com/watch?v=zHojAp5vkRE)觀看 AlphaGo 原理的講解，雖然有一些錯誤和不清楚的部份，但整體上講的很好，看完大概就可以知道本程式主要的運作原理，但因為此影片講解的是 AlphaGo 版本（2016年）的實做，和本實做有些不一樣的地方

1. 沒有 Fast Rollot
2. 沒有強化學習的部份，僅有監督學習
3. 策略（policy）網路和價值（value）網路前面的捲積層是共享的
4. AlphaGo Zero 原本 17 層的輸入層，本實做修正為 18 層（顏色輸入多一層），這樣訓練上會比較平均（請參考 leela zero）
