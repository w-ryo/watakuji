# きょうの運だめし

## 概要

「きょうの運だめし」は、毎日・毎週の運勢を「棚くじ風」に見せる Kivy 製のデスクトップアプリです。

- 0.1 秒ごとにカードが切り替わる
- 10秒 / 20秒でタイマーを選べる
- 気に入った瞬間を PNG 画像として保存できる
- 月曜日〜日曜日を選んで 1 週間分の運勢をまとめて撮影できる
- 保存した写真をアプリ内のギャラリーで見ることができる
- 日本語表示のために Noto Sans JP を使う

このアプリは GitHub 上で直接開くものではなく、ローカルの Mac / Windows / Linux PC で実行して使う前提です。

## 必要環境

- Python 3.10 以上
- Kivy 2.3.1
- 日本語フォント: `Noto Sans JP`
- GUI が使えるローカル環境

## このリポジトリの構成

- `main.py` : アプリ本体
- `requirements.txt` : Python の依存関係
- `run_tanakuji.command` : macOS 用の起動スクリプト
- `tanakuji_photos/` : 保存した画像の保存先
- `../Noto_Sans_JP/` : 日本語フォントの置き場所

## 日本語フォントの準備

このアプリは日本語を表示するために Noto Sans JP を使用します。

フォントファイルは次の場所に置いてください。

```text
/Users/ryou/Downloads/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf
```

または、あなたの環境に合わせたパスに置いて、`main.py` 内の `FONT_PATH` がそのパスを指すようにして下さい。

## セットアップ

```bash
cd /Users/ryou/Downloads/tanakuji_app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 実行

```bash
cd /Users/ryou/Downloads/tanakuji_app
source .venv/bin/activate
python main.py
```

macOS だと次のように実行できることもあります。

```bash
cd /Users/ryou/Downloads/tanakuji_app
./run_tanakuji.command
```

## 画像の保存先

保存された PNG は、このプロジェクト直下の `tanakuji_photos` フォルダに置かれます。

```text
/Users/ryou/Downloads/tanakuji_app/tanakuji_photos
```

アプリ内のギャラリーでも確認できます。

## 1週間分の使い方

1. 「1週間を撮る」を押す
2. 月曜日〜日曜日を順番に選んでいく
3. その日の 10 秒の中で気に入ったカードを保存する
4. 次の曜日へ進む
5. 1週間分の写真がまとめて保存される

## 文字化けしたとき

日本語が四角で表示される場合は、次を確認してください。

- Noto Sans JP がちゃんと存在している
- `FONT_PATH` が正しい場所を指している
- `python main.py` を Virtualenv で起動している
- `requirements.txt` で Kivy が入っている

## 補足

- このアプリは GUI アプリなので、GitHub のブラウザ画面から直接起動することはできません。
- 実際に使うにはローカルで実行する必要があります。
- 保存した画像は `tanakuji_photos` フォルダに残るので、後で一覧や確認がしやすいです。
