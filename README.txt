# きょうの運だめし（たなくじ風アプリ）

## 概要
「きょうの運だめし」は、10秒または20秒の時間で運勢カードを切り替えながら、
その瞬間のカードをPNGとして保存できる Kivy 製アプリです。

- 10秒 / 20秒の時間を選べる
- 0.5秒 / 0.3秒 / 0.1秒でカードが切り替わる
- 直前の運勢と同じ名前は連続しない
- 「この瞬間を撮影」で表示中のカードを保存
- 時間切れ時も最後のカードを自動保存
- 日本語表示のために Noto Sans JP を使う

## 必要環境
- Python 3.10 以上
- macOS / Linux / Windows のローカル環境
- フォント: `../Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf`

## セットアップ
このリポジトリでは `.venv` を使って依存を固定します。

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

## 保存先
保存先はアプリのユーザーデータディレクトリ配下の `tanakuji_photos` フォルダです。
通常は次のような場所に作成されます。

- macOS: `~/Library/Application Support/.../tanakuji_photos`
- Windows: `%APPDATA%/.../tanakuji_photos`
- Linux: `~/.local/share/.../tanakuji_photos`

## フォントについて
日本語文字が四角で表示される場合は、`Noto_Sans_JP` フォルダがこのプロジェクトの親ディレクトリにあることを確認してください。

想定パス:

```text
/Users/ryou/Downloads/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf
```

## 補足
- APK 化などの Android 向け配布は別途 Buildozer と設定が必要です。
- このアプリは画面上のカードを画像として保存するサンプルです。
- `main.py` の `Spinner` で切替速度を調整できます。
