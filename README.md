# 燐音郷 ～ Phosphorescent Sonata（ブラウザ版）

東方Projectの「面白さの本質（美しい弾幕・避ける快感・世界観）」を継承した、完全オリジナルの弾幕シューティング。
このリポジトリは**ブラウザだけで遊べる全6面版**です（`index.html` + `assets/`、外部通信なし）。
6人のボス（雫見あおい／鈴懸すゞな／燈籠まつり／箱宮ねむ／静水しじま／始響うた）を立ち絵・背景・カットイン・実BGM付きで通しプレイできます。

## 遊ぶ
- 公開URL（GitHub Pages を有効にすると下記が使えます）:
  `https://<あなたのユーザー名>.github.io/<リポジトリ名>/`
- ローカルで試す場合は `index.html` をブラウザで開くだけ。

## 操作
- PC: 矢印/WASD=移動、Z=ショット、Shift=集中（低速＋当たり判定表示）、X=ボム、C=共鳴解放、R=リトライ
- スマホ: 画面ドラッグで移動（自動ショット）、右下 BOMB ボタン、タップで開始/リトライ

## 遊び方のコツ
- 当たり判定は自機中央の極小の点だけ。弾の近くを通すと「グレイズ」でゲージが溜まり、満タンで **C＝共鳴解放**（敵弾スロー）。
- 各ボスは固有の弾幕（波・風・花火・歯車・静寂・虹）と実BGMを持ちます。ボスを倒すと次の面へ、全6面クリアで ALL CLEAR。

---

## GitHub Pages で公開する手順（ブラウザだけ・約3分）
1. GitHub にログインし、**New repository** で新しいリポジトリを作成（名前は何でもOK、例: `rinnekyo`）。Public を選択。
2. 作成後の画面で **Add file → Upload files**。**`index.html`・`README.md`・`assets` フォルダごと**ドラッグ＆ドロップ（`assets/` の中の画像も一緒に）→ **Commit changes**。
   - 画像は `index.html` から `assets/xxx.png` の相対パスで読み込みます。フォルダ構成（`index.html` と同じ階層に `assets/`）を崩さないでください。
3. リポジトリの **Settings → Pages** を開く。
4. **Build and deployment → Source** を **Deploy from a branch** にし、Branch を **main / (root)** にして **Save**。
5. 1〜2分待つと、同じ Pages 画面の上部に公開URLが表示されます → それが遊べるリンクです。

> Git に慣れていれば `git init → add → commit → push` でもOK。GitHub Desktop なら「Add Local Repository」でこのフォルダを選び、Publish repository でも公開できます。

## ライセンス/権利メモ
- コードはオリジナル。キャラ・世界観・弾幕・音はすべて新規制作で、既存作品の流用はありません。
- 画像アセットを別途同梱・公開する場合は、生成物の取り扱い・配布条件にご注意ください。

フル版（全6面・道中・会話・ランキング/リプレイ・設定・練習モード）は Unity プロジェクト側にあります。
