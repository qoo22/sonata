# -*- coding: utf-8 -*-
# HP半分で切り替わる“第2BGM（intense/サビ）”を合成。完全オリジナル。
import _synth as S

NH=S.NHARM
# 泣きのサビ（レシピ7）— ドラマチックな climax 進行
SABI=['F','G','Am','Am','F','G','C','E','F','G','Am','G','F','E','Am','Am']

# 1 あおい：潮騒の激情サビ
S.make('assets/bgm1b.wav',170, SABI, NH, style='boss', lead_density='high', lead_gain=0.6)
# 2 すゞな：疾風の最高速
S.make('assets/bgm2b.wav',192, ['Am','G','F','G','Am','G','F','E','Am','Dm','G','C','F','G','Am','E'],
       NH, style='boss', lead_density='high', bell_arp=True, lead_gain=0.6)
# 3 まつり：大輪の宴サビ
S.make('assets/bgm3b.wav',182, ['Am','Dm','G','C','F','G','Am','E','Am','Dm','G','C','F','G','Am','Am'],
       NH, style='boss', lead_density='high', lead_gain=0.6)
# 4 ねむ：回る時計の加速
S.make('assets/bgm4b.wav',176, ['Am','F','Dm','E','Am','F','C','E','F','G','Am','G','F','E','Am','Am'],
       NH, style='boss', lead_density='high', lead_gain=0.58)
# 5 しじま：静寂を破る狂気
S.make('assets/bgm5b.wav',188, ['Am','Bb','Am','E','Am','G#dim','F','E','Am','Bb','Am','E','F','G','Am','Am'],
       NH, style='boss', lead_density='high', lead_gain=0.62)
# 6 うた：終幕のサビ
S.make('assets/bgm6b.wav',184, SABI, NH, style='boss', lead_density='high', lead_gain=0.65)
print('intense done')
