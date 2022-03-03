# Training

## 訓練的資訊

依照訓練範例輸入一下指令，終端機會出現一系列訊息，幫助掌握目前學習的進度和情況，第一部份是程式在載入解析 sgf 當案並產生訓練資料，當出現 'parsed 100.00% games' 時，代表棋譜已經全處理完成。第二部份就開始訓練網路，大部份資訊我想理解不是問題，其中 'rate' 代表每秒訓練幾個 steps ，'estimate' 代表完成訓練估計的剩餘秒數

    $ python3 train.py --dir sgf-directory-name --step 128000 --batch-size 512 --learning-rate 0.001 --weights-name weights
    total 34572 games
    parsed 2.89% games
    parsed 5.79% games
    parsed 8.68% games
    parsed 11.57% games
    parsed 14.46% games
    parsed 17.36% games
    parsed 20.25% games
    parsed 23.14% games
    parsed 26.03% games
    parsed 28.93% games
    parsed 31.82% games
    parsed 34.71% games
    parsed 37.60% games
    parsed 40.50% games
    parsed 43.39% games
    parsed 46.28% games
    parsed 49.17% games
    parsed 52.07% games
    parsed 54.96% games
    parsed 57.85% games
    parsed 60.74% games
    parsed 63.64% games
    parsed 66.53% games
    parsed 69.42% games
    parsed 72.31% games
    parsed 75.21% games
    parsed 78.10% games
    parsed 80.99% games
    parsed 83.88% games
    parsed 86.78% games
    parsed 89.67% games
    parsed 92.56% games
    parsed 95.45% games
    parsed 98.35% games
    parsed 100.00% games
    [2021-12-4 21:00:57] steps: 1000/128000, 0.78% -> policy loss: 2.4710, value loss: 0.8499 | rate: 8.83(step/sec), estimate: 14379(sec)
    [2021-12-4 21:02:51] steps: 2000/128000, 1.56% -> policy loss: 1.9450, value loss: 0.7782 | rate: 8.74(step/sec), estimate: 14419(sec)
    [2021-12-4 21:04:44] steps: 3000/128000, 2.34% -> policy loss: 1.8621, value loss: 0.7504 | rate: 8.86(step/sec), estimate: 14106(sec)
    [2021-12-4 21:06:37] steps: 4000/128000, 3.12% -> policy loss: 1.8111, value loss: 0.7355 | rate: 8.84(step/sec), estimate: 14026(sec)
    [2021-12-4 21:08:29] steps: 5000/128000, 3.91% -> policy loss: 1.7738, value loss: 0.7247 | rate: 8.93(step/sec), estimate: 13775(sec)
    [2021-12-4 21:10:21] steps: 6000/128000, 4.69% -> policy loss: 1.7503, value loss: 0.7135 | rate: 8.90(step/sec), estimate: 13707(sec)
    [2021-12-4 21:12:14] steps: 7000/128000, 5.47% -> policy loss: 1.7259, value loss: 0.7063 | rate: 8.87(step/sec), estimate: 13649(sec)
    [2021-12-4 21:14:07] steps: 8000/128000, 6.25% -> policy loss: 1.7106, value loss: 0.7036 | rate: 8.86(step/sec), estimate: 13537(sec)
    [2021-12-4 21:16:00] steps: 9000/128000, 7.03% -> policy loss: 1.6983, value loss: 0.6958 | rate: 8.87(step/sec), estimate: 13418(sec)
    [2021-12-4 21:17:53] steps: 10000/128000, 7.81% -> policy loss: 1.6819, value loss: 0.6926 | rate: 8.84(step/sec), estimate: 13341(sec)
    [2021-12-4 21:19:45] steps: 11000/128000, 8.59% -> policy loss: 1.6736, value loss: 0.6900 | rate: 8.92(step/sec), estimate: 13119(sec)
    [2021-12-4 21:21:37] steps: 12000/128000, 9.38% -> policy loss: 1.6612, value loss: 0.6867 | rate: 8.96(step/sec), estimate: 12940(sec)
    [2021-12-4 21:23:29] steps: 13000/128000, 10.16% -> policy loss: 1.6567, value loss: 0.6839 | rate: 8.89(step/sec), estimate: 12943(sec)
    [2021-12-4 21:25:23] steps: 14000/128000, 10.94% -> policy loss: 1.6507, value loss: 0.6778 | rate: 8.80(step/sec), estimate: 12947(sec)
    [2021-12-4 21:27:16] steps: 15000/128000, 11.72% -> policy loss: 1.6413, value loss: 0.6780 | rate: 8.79(step/sec), estimate: 12853(sec)
    [2021-12-4 21:29:09] steps: 16000/128000, 12.50% -> policy loss: 1.6342, value loss: 0.6737 | rate: 8.89(step/sec), estimate: 12598(sec)
    [2021-12-4 21:31:00] steps: 17000/128000, 13.28% -> policy loss: 1.6281, value loss: 0.6745 | rate: 8.97(step/sec), estimate: 12372(sec)
    [2021-12-4 21:32:53] steps: 18000/128000, 14.06% -> policy loss: 1.6189, value loss: 0.6710 | rate: 8.88(step/sec), estimate: 12380(sec)
    [2021-12-4 21:34:45] steps: 19000/128000, 14.84% -> policy loss: 1.6198, value loss: 0.6707 | rate: 8.93(step/sec), estimate: 12210(sec)
    [2021-12-4 21:36:37] steps: 20000/128000, 15.62% -> policy loss: 1.6120, value loss: 0.6695 | rate: 8.90(step/sec), estimate: 12135(sec)
    [2021-12-4 21:38:29] steps: 21000/128000, 16.41% -> policy loss: 1.6105, value loss: 0.6655 | rate: 8.98(step/sec), estimate: 11918(sec)
    [2021-12-4 21:40:21] steps: 22000/128000, 17.19% -> policy loss: 1.6069, value loss: 0.6644 | rate: 8.93(step/sec), estimate: 11863(sec)
    [2021-12-4 21:42:12] steps: 23000/128000, 17.97% -> policy loss: 1.6023, value loss: 0.6639 | rate: 8.94(step/sec), estimate: 11748(sec)
    [2021-12-4 21:44:05] steps: 24000/128000, 18.75% -> policy loss: 1.6009, value loss: 0.6628 | rate: 8.93(step/sec), estimate: 11649(sec)
    [2021-12-4 21:45:57] steps: 25000/128000, 19.53% -> policy loss: 1.5965, value loss: 0.6604 | rate: 8.88(step/sec), estimate: 11601(sec)
    [2021-12-4 21:47:49] steps: 26000/128000, 20.31% -> policy loss: 1.5939, value loss: 0.6599 | rate: 8.91(step/sec), estimate: 11452(sec)
    [2021-12-4 21:49:42] steps: 27000/128000, 21.09% -> policy loss: 1.5888, value loss: 0.6602 | rate: 8.90(step/sec), estimate: 11352(sec)
    [2021-12-4 21:51:34] steps: 28000/128000, 21.88% -> policy loss: 1.5879, value loss: 0.6580 | rate: 8.90(step/sec), estimate: 11235(sec)
    [2021-12-4 21:53:27] steps: 29000/128000, 22.66% -> policy loss: 1.5824, value loss: 0.6575 | rate: 8.90(step/sec), estimate: 11125(sec)
    [2021-12-4 21:55:19] steps: 30000/128000, 23.44% -> policy loss: 1.5817, value loss: 0.6570 | rate: 8.88(step/sec), estimate: 11030(sec)
    [2021-12-4 21:57:12] steps: 31000/128000, 24.22% -> policy loss: 1.5770, value loss: 0.6570 | rate: 8.87(step/sec), estimate: 10929(sec)
    [2021-12-4 21:59:05] steps: 32000/128000, 25.00% -> policy loss: 1.5771, value loss: 0.6551 | rate: 8.84(step/sec), estimate: 10858(sec)
    [2021-12-4 22:00:58] steps: 33000/128000, 25.78% -> policy loss: 1.5752, value loss: 0.6559 | rate: 8.85(step/sec), estimate: 10732(sec)
    [2021-12-4 22:02:50] steps: 34000/128000, 26.56% -> policy loss: 1.5740, value loss: 0.6538 | rate: 8.91(step/sec), estimate: 10545(sec)
    [2021-12-4 22:04:42] steps: 35000/128000, 27.34% -> policy loss: 1.5714, value loss: 0.6533 | rate: 8.90(step/sec), estimate: 10454(sec)
    [2021-12-4 22:06:36] steps: 36000/128000, 28.12% -> policy loss: 1.5696, value loss: 0.6516 | rate: 8.81(step/sec), estimate: 10438(sec)
    [2021-12-4 22:08:28] steps: 37000/128000, 28.91% -> policy loss: 1.5659, value loss: 0.6513 | rate: 8.95(step/sec), estimate: 10169(sec)
    [2021-12-4 22:10:21] steps: 38000/128000, 29.69% -> policy loss: 1.5639, value loss: 0.6506 | rate: 8.84(step/sec), estimate: 10182(sec)
    [2021-12-4 22:12:12] steps: 39000/128000, 30.47% -> policy loss: 1.5615, value loss: 0.6501 | rate: 8.95(step/sec), estimate: 9941(sec)
    [2021-12-4 22:14:05] steps: 40000/128000, 31.25% -> policy loss: 1.5625, value loss: 0.6500 | rate: 8.90(step/sec), estimate: 9891(sec)
    [2021-12-4 22:15:57] steps: 41000/128000, 32.03% -> policy loss: 1.5624, value loss: 0.6478 | rate: 8.90(step/sec), estimate: 9772(sec)
    [2021-12-4 22:17:50] steps: 42000/128000, 32.81% -> policy loss: 1.5597, value loss: 0.6473 | rate: 8.85(step/sec), estimate: 9717(sec)
    [2021-12-4 22:19:44] steps: 43000/128000, 33.59% -> policy loss: 1.5555, value loss: 0.6503 | rate: 8.80(step/sec), estimate: 9661(sec)
    [2021-12-4 22:21:37] steps: 44000/128000, 34.38% -> policy loss: 1.5596, value loss: 0.6464 | rate: 8.88(step/sec), estimate: 9461(sec)
    [2021-12-4 22:23:29] steps: 45000/128000, 35.16% -> policy loss: 1.5548, value loss: 0.6470 | rate: 8.91(step/sec), estimate: 9315(sec)
    [2021-12-4 22:25:22] steps: 46000/128000, 35.94% -> policy loss: 1.5505, value loss: 0.6481 | rate: 8.84(step/sec), estimate: 9280(sec)
    [2021-12-4 22:27:15] steps: 47000/128000, 36.72% -> policy loss: 1.5506, value loss: 0.6457 | rate: 8.83(step/sec), estimate: 9177(sec)
    [2021-12-4 22:29:09] steps: 48000/128000, 37.50% -> policy loss: 1.5468, value loss: 0.6456 | rate: 8.77(step/sec), estimate: 9122(sec)
    [2021-12-4 22:31:01] steps: 49000/128000, 38.28% -> policy loss: 1.5540, value loss: 0.6456 | rate: 8.93(step/sec), estimate: 8851(sec)
    [2021-12-4 22:32:53] steps: 50000/128000, 39.06% -> policy loss: 1.5486, value loss: 0.6454 | rate: 8.92(step/sec), estimate: 8744(sec)
    [2021-12-4 22:34:46] steps: 51000/128000, 39.84% -> policy loss: 1.5465, value loss: 0.6429 | rate: 8.88(step/sec), estimate: 8672(sec)
    [2021-12-4 22:36:39] steps: 52000/128000, 40.62% -> policy loss: 1.5458, value loss: 0.6463 | rate: 8.88(step/sec), estimate: 8558(sec)
    [2021-12-4 22:38:30] steps: 53000/128000, 41.41% -> policy loss: 1.5459, value loss: 0.6428 | rate: 8.96(step/sec), estimate: 8371(sec)
    [2021-12-4 22:40:23] steps: 54000/128000, 42.19% -> policy loss: 1.5463, value loss: 0.6421 | rate: 8.88(step/sec), estimate: 8329(sec)
    [2021-12-4 22:42:15] steps: 55000/128000, 42.97% -> policy loss: 1.5463, value loss: 0.6427 | rate: 8.88(step/sec), estimate: 8222(sec)
    [2021-12-4 22:44:08] steps: 56000/128000, 43.75% -> policy loss: 1.5419, value loss: 0.6423 | rate: 8.85(step/sec), estimate: 8131(sec)
    [2021-12-4 22:46:00] steps: 57000/128000, 44.53% -> policy loss: 1.5408, value loss: 0.6422 | rate: 8.93(step/sec), estimate: 7947(sec)
    [2021-12-4 22:47:53] steps: 58000/128000, 45.31% -> policy loss: 1.5429, value loss: 0.6395 | rate: 8.92(step/sec), estimate: 7851(sec)
    [2021-12-4 22:49:45] steps: 59000/128000, 46.09% -> policy loss: 1.5379, value loss: 0.6423 | rate: 8.89(step/sec), estimate: 7758(sec)
    [2021-12-4 22:51:37] steps: 60000/128000, 46.88% -> policy loss: 1.5396, value loss: 0.6403 | rate: 8.89(step/sec), estimate: 7647(sec)
    [2021-12-4 22:53:30] steps: 61000/128000, 47.66% -> policy loss: 1.5391, value loss: 0.6409 | rate: 8.91(step/sec), estimate: 7520(sec)
    [2021-12-4 22:55:22] steps: 62000/128000, 48.44% -> policy loss: 1.5360, value loss: 0.6389 | rate: 8.90(step/sec), estimate: 7417(sec)
    [2021-12-4 22:57:15] steps: 63000/128000, 49.22% -> policy loss: 1.5330, value loss: 0.6399 | rate: 8.85(step/sec), estimate: 7347(sec)
    [2021-12-4 22:59:08] steps: 64000/128000, 50.00% -> policy loss: 1.5367, value loss: 0.6415 | rate: 8.82(step/sec), estimate: 7255(sec)
    [2021-12-4 23:01:00] steps: 65000/128000, 50.78% -> policy loss: 1.5319, value loss: 0.6388 | rate: 8.95(step/sec), estimate: 7035(sec)
    [2021-12-4 23:02:52] steps: 66000/128000, 51.56% -> policy loss: 1.5323, value loss: 0.6403 | rate: 8.90(step/sec), estimate: 6962(sec)
    [2021-12-4 23:04:46] steps: 67000/128000, 52.34% -> policy loss: 1.5361, value loss: 0.6405 | rate: 8.78(step/sec), estimate: 6947(sec)
    [2021-12-4 23:06:42] steps: 68000/128000, 53.12% -> policy loss: 1.5335, value loss: 0.6385 | rate: 8.66(step/sec), estimate: 6928(sec)
    [2021-12-4 23:08:37] steps: 69000/128000, 53.91% -> policy loss: 1.5301, value loss: 0.6385 | rate: 8.71(step/sec), estimate: 6773(sec)
    [2021-12-4 23:10:30] steps: 70000/128000, 54.69% -> policy loss: 1.5323, value loss: 0.6402 | rate: 8.79(step/sec), estimate: 6595(sec)
    [2021-12-4 23:12:24] steps: 71000/128000, 55.47% -> policy loss: 1.5342, value loss: 0.6357 | rate: 8.83(step/sec), estimate: 6455(sec)
    [2021-12-4 23:14:17] steps: 72000/128000, 56.25% -> policy loss: 1.5281, value loss: 0.6397 | rate: 8.80(step/sec), estimate: 6361(sec)
    [2021-12-4 23:16:11] steps: 73000/128000, 57.03% -> policy loss: 1.5311, value loss: 0.6390 | rate: 8.80(step/sec), estimate: 6251(sec)
    [2021-12-4 23:18:03] steps: 74000/128000, 57.81% -> policy loss: 1.5276, value loss: 0.6366 | rate: 8.89(step/sec), estimate: 6076(sec)
    [2021-12-4 23:19:56] steps: 75000/128000, 58.59% -> policy loss: 1.5259, value loss: 0.6374 | rate: 8.86(step/sec), estimate: 5980(sec)
    [2021-12-4 23:21:48] steps: 76000/128000, 59.38% -> policy loss: 1.5280, value loss: 0.6368 | rate: 8.94(step/sec), estimate: 5816(sec)
    [2021-12-4 23:23:40] steps: 77000/128000, 60.16% -> policy loss: 1.5254, value loss: 0.6341 | rate: 8.90(step/sec), estimate: 5731(sec)
    [2021-12-4 23:25:33] steps: 78000/128000, 60.94% -> policy loss: 1.5252, value loss: 0.6362 | rate: 8.91(step/sec), estimate: 5612(sec)
    [2021-12-4 23:27:24] steps: 79000/128000, 61.72% -> policy loss: 1.5238, value loss: 0.6369 | rate: 8.97(step/sec), estimate: 5460(sec)
    [2021-12-4 23:29:16] steps: 80000/128000, 62.50% -> policy loss: 1.5291, value loss: 0.6355 | rate: 8.90(step/sec), estimate: 5396(sec)
    [2021-12-4 23:31:09] steps: 81000/128000, 63.28% -> policy loss: 1.5215, value loss: 0.6349 | rate: 8.92(step/sec), estimate: 5271(sec)
    [2021-12-4 23:33:01] steps: 82000/128000, 64.06% -> policy loss: 1.5202, value loss: 0.6360 | rate: 8.88(step/sec), estimate: 5178(sec)
    [2021-12-4 23:34:54] steps: 83000/128000, 64.84% -> policy loss: 1.5203, value loss: 0.6343 | rate: 8.85(step/sec), estimate: 5085(sec)
    [2021-12-4 23:36:48] steps: 84000/128000, 65.62% -> policy loss: 1.5200, value loss: 0.6349 | rate: 8.81(step/sec), estimate: 4996(sec)
    [2021-12-4 23:38:40] steps: 85000/128000, 66.41% -> policy loss: 1.5211, value loss: 0.6356 | rate: 8.92(step/sec), estimate: 4820(sec)
    [2021-12-4 23:40:34] steps: 86000/128000, 67.19% -> policy loss: 1.5221, value loss: 0.6337 | rate: 8.77(step/sec), estimate: 4787(sec)
    [2021-12-4 23:42:27] steps: 87000/128000, 67.97% -> policy loss: 1.5172, value loss: 0.6346 | rate: 8.82(step/sec), estimate: 4648(sec)
    [2021-12-4 23:44:20] steps: 88000/128000, 68.75% -> policy loss: 1.5199, value loss: 0.6339 | rate: 8.89(step/sec), estimate: 4499(sec)
    [2021-12-4 23:46:13] steps: 89000/128000, 69.53% -> policy loss: 1.5176, value loss: 0.6326 | rate: 8.85(step/sec), estimate: 4405(sec)
    [2021-12-4 23:48:06] steps: 90000/128000, 70.31% -> policy loss: 1.5176, value loss: 0.6332 | rate: 8.84(step/sec), estimate: 4300(sec)
    [2021-12-4 23:49:59] steps: 91000/128000, 71.09% -> policy loss: 1.5176, value loss: 0.6335 | rate: 8.87(step/sec), estimate: 4173(sec)
    [2021-12-4 23:51:50] steps: 92000/128000, 71.88% -> policy loss: 1.5150, value loss: 0.6342 | rate: 8.99(step/sec), estimate: 4005(sec)
    [2021-12-4 23:53:42] steps: 93000/128000, 72.66% -> policy loss: 1.5140, value loss: 0.6332 | rate: 8.95(step/sec), estimate: 3911(sec)
    [2021-12-4 23:55:34] steps: 94000/128000, 73.44% -> policy loss: 1.5148, value loss: 0.6343 | rate: 8.87(step/sec), estimate: 3832(sec)
    [2021-12-4 23:57:29] steps: 95000/128000, 74.22% -> policy loss: 1.5122, value loss: 0.6343 | rate: 8.76(step/sec), estimate: 3769(sec)
    [2021-12-4 23:59:22] steps: 96000/128000, 75.00% -> policy loss: 1.5134, value loss: 0.6314 | rate: 8.82(step/sec), estimate: 3628(sec)
    [2021-12-5 00:01:15] steps: 97000/128000, 75.78% -> policy loss: 1.5145, value loss: 0.6314 | rate: 8.81(step/sec), estimate: 3518(sec)
    [2021-12-5 00:03:09] steps: 98000/128000, 76.56% -> policy loss: 1.5139, value loss: 0.6329 | rate: 8.82(step/sec), estimate: 3401(sec)
    [2021-12-5 00:05:02] steps: 99000/128000, 77.34% -> policy loss: 1.5131, value loss: 0.6305 | rate: 8.81(step/sec), estimate: 3292(sec)
    [2021-12-5 00:06:56] steps: 100000/128000, 78.12% -> policy loss: 1.5131, value loss: 0.6321 | rate: 8.79(step/sec), estimate: 3184(sec)
    [2021-12-5 00:08:51] steps: 101000/128000, 78.91% -> policy loss: 1.5135, value loss: 0.6314 | rate: 8.74(step/sec), estimate: 3090(sec)
    [2021-12-5 00:10:44] steps: 102000/128000, 79.69% -> policy loss: 1.5150, value loss: 0.6331 | rate: 8.83(step/sec), estimate: 2943(sec)
    [2021-12-5 00:12:37] steps: 103000/128000, 80.47% -> policy loss: 1.5091, value loss: 0.6310 | rate: 8.83(step/sec), estimate: 2831(sec)
    [2021-12-5 00:14:30] steps: 104000/128000, 81.25% -> policy loss: 1.5082, value loss: 0.6313 | rate: 8.88(step/sec), estimate: 2703(sec)
    [2021-12-5 00:16:23] steps: 105000/128000, 82.03% -> policy loss: 1.5115, value loss: 0.6320 | rate: 8.82(step/sec), estimate: 2607(sec)
    [2021-12-5 00:18:18] steps: 106000/128000, 82.81% -> policy loss: 1.5088, value loss: 0.6319 | rate: 8.70(step/sec), estimate: 2530(sec)
    [2021-12-5 00:20:12] steps: 107000/128000, 83.59% -> policy loss: 1.5107, value loss: 0.6324 | rate: 8.79(step/sec), estimate: 2390(sec)
    [2021-12-5 00:22:12] steps: 108000/128000, 84.38% -> policy loss: 1.5080, value loss: 0.6303 | rate: 8.36(step/sec), estimate: 2393(sec)
    [2021-12-5 00:24:11] steps: 109000/128000, 85.16% -> policy loss: 1.5108, value loss: 0.6315 | rate: 8.35(step/sec), estimate: 2276(sec)
    [2021-12-5 00:26:10] steps: 110000/128000, 85.94% -> policy loss: 1.5073, value loss: 0.6310 | rate: 8.39(step/sec), estimate: 2144(sec)
    [2021-12-5 00:28:12] steps: 111000/128000, 86.72% -> policy loss: 1.5076, value loss: 0.6297 | rate: 8.25(step/sec), estimate: 2061(sec)
    [2021-12-5 00:30:10] steps: 112000/128000, 87.50% -> policy loss: 1.5036, value loss: 0.6292 | rate: 8.44(step/sec), estimate: 1896(sec)
    [2021-12-5 00:32:12] steps: 113000/128000, 88.28% -> policy loss: 1.5094, value loss: 0.6290 | rate: 8.22(step/sec), estimate: 1824(sec)
    [2021-12-5 00:34:12] steps: 114000/128000, 89.06% -> policy loss: 1.5076, value loss: 0.6271 | rate: 8.35(step/sec), estimate: 1677(sec)
    [2021-12-5 00:36:12] steps: 115000/128000, 89.84% -> policy loss: 1.5065, value loss: 0.6280 | rate: 8.28(step/sec), estimate: 1569(sec)
    [2021-12-5 00:38:12] steps: 116000/128000, 90.62% -> policy loss: 1.5082, value loss: 0.6286 | rate: 8.36(step/sec), estimate: 1435(sec)
    [2021-12-5 00:40:12] steps: 117000/128000, 91.41% -> policy loss: 1.5074, value loss: 0.6286 | rate: 8.32(step/sec), estimate: 1322(sec)
    [2021-12-5 00:42:14] steps: 118000/128000, 92.19% -> policy loss: 1.5022, value loss: 0.6290 | rate: 8.22(step/sec), estimate: 1216(sec)
    [2021-12-5 00:44:12] steps: 119000/128000, 92.97% -> policy loss: 1.5041, value loss: 0.6284 | rate: 8.46(step/sec), estimate: 1064(sec)
    [2021-12-5 00:46:09] steps: 120000/128000, 93.75% -> policy loss: 1.5085, value loss: 0.6267 | rate: 8.53(step/sec), estimate: 938(sec)
    [2021-12-5 00:48:06] steps: 121000/128000, 94.53% -> policy loss: 1.5030, value loss: 0.6275 | rate: 8.58(step/sec), estimate: 815(sec)
    [2021-12-5 00:50:04] steps: 122000/128000, 95.31% -> policy loss: 1.4998, value loss: 0.6284 | rate: 8.45(step/sec), estimate: 709(sec)
    [2021-12-5 00:52:04] steps: 123000/128000, 96.09% -> policy loss: 1.5033, value loss: 0.6288 | rate: 8.36(step/sec), estimate: 598(sec)
    [2021-12-5 00:54:02] steps: 124000/128000, 96.88% -> policy loss: 1.5049, value loss: 0.6304 | rate: 8.43(step/sec), estimate: 474(sec)
    [2021-12-5 00:56:00] steps: 125000/128000, 97.66% -> policy loss: 1.5011, value loss: 0.6267 | rate: 8.50(step/sec), estimate: 353(sec)
    [2021-12-5 00:58:00] steps: 126000/128000, 98.44% -> policy loss: 1.5055, value loss: 0.6272 | rate: 8.33(step/sec), estimate: 240(sec)
    [2021-12-5 01:00:00] steps: 127000/128000, 99.22% -> policy loss: 1.5007, value loss: 0.6274 | rate: 8.36(step/sec), estimate: 119(sec)
    [2021-12-5 01:01:57] steps: 128000/128000, 100.00% -> policy loss: 1.5010, value loss: 0.6273 | rate: 8.56(step/sec), estimate: 0(sec)
    Trainig is over.

最後完成訓練後，會出現以下圖片以視覺化的方式顯示訓練過程

![loss_plot](https://github.com/CGLemon/pyDLGO/blob/master/img/loss_plot.png)

## 訓練技巧

事實上，訓練圍棋的網路，持續的降低學習率是很重要的，相同訓練資料，有降低學習率和沒有學習率的網路，其強度可以差距三段以上，這個差距在讓子棋中尤其明顯，未降低學習率的網路在前期通常無法有效辨識當前盤面的好壞。dlgo 提供重新載入網路的的功能，輸入下列指令即可調整學習率重新訓練

    $ python3 train.py --dir sgf-directory-name --step 128000 --batch-size 512 --learning-rate 0.0001 --load-weights preweights --weights-name outweights

你可能會好奇，每次降低學習大概需要多少個 steps ，以經驗來看，範例給的 128000 steps 配合 512 batch 的訓練量就非常足夠，依照上面的訓練資訊，loss 已經很難再降低了。當然如果你不放心，可以選用更大 step 數來訓練，以確到達到完全訓練，只要訓練集夠大，過度訓練並不會影響網路強度。最後學習率大概要降低到多少，這沒有一定值，但一般來講 loss 不再降低時就可以停止了。
