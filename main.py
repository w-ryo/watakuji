# -*- coding: utf-8 -*-
"""
スマホ向け「たなくじ風」おみくじアプリ
必要: Python 3.10+ / Kivy 2.3+
起動: python main.py

機能:
- 10秒 / 20秒を選んで開始
- 0.5秒ごとに運勢カードが切り替わる
- 「この瞬間を撮影」でそのカードを保存
- 制限時間終了時は最後に表示されていたカードを自動保存
- 保存先: アプリの user_data_dir 内の tanakuji_photos フォルダ
"""

import os
import random
import subprocess
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption


APP_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.abspath(os.path.join(APP_DIR, "..", "Noto_Sans_JP", "NotoSansJP-VariableFont_wght.ttf"))

if not os.path.exists(FONT_PATH):
    FONT_PATH = ""  # フォントが見つからない場合はデフォルトにフォールバック

WEEKDAYS = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]


class FontSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_PATH or ""
        self.color = (1, 1, 1, 1)


# 20 × 10 = 200種類の、オリジナル運勢名を作ります。
# 「たなくじ」そのものの文言・画像は使用せず、独自の名前です。
# 「ダークホース大吉」のように、名前だけで情景や物語が浮かぶ運勢名。
# 40個の個性的な前半 × 5段階の運勢 = 200種類。
PREFIXES = [
    "ダークホース", "伏兵あらわる", "寝坊したけど", "最後に笑う", "主役は遅れて",
    "まさかの展開", "追い風に乗る", "奇跡の予感", "隠れた才能", "逆転ホームラン",
    "棚からぼたもち", "思わぬところに", "今日だけ無敵", "幸運の抜け道", "静かなる勝者",
    "ひらめき暴走", "ご縁が急接近", "努力が発芽", "運命のいたずら", "小さな革命",
    "眠れる獅子", "レアキャラ遭遇", "人生の伏線回収", "ピンチがチャンス", "笑う門には",
    "直感が冴える", "気まぐれ天使", "福が迷い込む", "追試を回避する", "主役級の偶然",
    "雲の上の気分", "幸せの前借り", "勝手に好転", "まわりまわって", "急にモテ期",
    "願いがすべりこむ", "大器晩成モード", "なんか持ってる", "予想外の才能", "明日はもっと",
]
SUFFIXES = ["大吉", "中吉", "小吉", "吉", "末吉"]
FORTUNES = [f"{p}{s}" for p in PREFIXES for s in SUFFIXES]

MESSAGES = [
    "小さな幸せを見つけられそう。",
    "いつもより少しだけ前向きに。",
    "気になっていたことを始めるチャンス。",
    "焦らず、自分のペースで進もう。",
    "誰かへのひと言が良い流れを作りそう。",
    "休憩を取ると、いいアイデアが浮かぶかも。",
    "思いがけない発見に出会える予感。",
    "今日は自分をほめてあげよう。",
    "迷ったら、心が軽くなる方を選んでみて。",
    "いつもの道にも楽しい発見がありそう。",
    "丁寧に取り組むと、うれしい結果につながりそう。",
    "笑顔が幸運を呼び込む日。",
    "ひとつ片づけると気分もすっきり。",
    "新しいものを試すと発見がありそう。",
    "無理せず、できることからで大丈夫。",
]


def apply_font(widget, font_name=FONT_PATH):
    if not font_name:
        return
    if hasattr(widget, "font_name"):
        widget.font_name = font_name
    for child in getattr(widget, "children", []):
        apply_font(child, font_name)


class FortuneCard(BoxLayout):
    """画像として保存できる、運勢カード部分。"""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(20), spacing=dp(12), **kwargs)
        self.size_hint = (1, 1)
        self._bg_color = (0.98, 0.78, 0.32, 1)

        with self.canvas.before:
            self._color_instruction = Color(*self._bg_color)
            self._rounded = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(28)]
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

        self.kicker = Label(
            text="きょうの運だめし",
            font_name=FONT_PATH,
            font_size="20sp",
            color=(0.25, 0.14, 0.06, 1),
            size_hint=(1, 0.18),
        )
        self.fortune_label = Label(
            text="準備中",
            font_name=FONT_PATH,
            font_size="38sp",
            bold=True,
            color=(0.20, 0.10, 0.03, 1),
            halign="center",
            valign="middle",
            size_hint=(1, 0.43),
        )
        self.message_label = Label(
            text="スタートを押してね！",
            font_name=FONT_PATH,
            font_size="19sp",
            color=(0.20, 0.10, 0.03, 1),
            halign="center",
            valign="middle",
            size_hint=(1, 0.25),
        )
        self.footer = Label(
            text="HAPPY DAY!",
            font_name=FONT_PATH,
            font_size="16sp",
            bold=True,
            color=(0.25, 0.14, 0.06, 1),
            size_hint=(1, 0.14),
        )
        self.add_widget(self.kicker)
        self.add_widget(self.fortune_label)
        self.add_widget(self.message_label)
        self.add_widget(self.footer)

    def _update_canvas(self, *_):
        self._rounded.pos = self.pos
        self._rounded.size = self.size

    def show_fortune(self, fortune, message, color):
        self._bg_color = (*color, 1)
        self._color_instruction.rgba = self._bg_color
        self.fortune_label.text = fortune
        self.message_label.text = message

    def show_weekday(self, weekday, fortune, message, color):
        self._bg_color = (*color, 1)
        self._color_instruction.rgba = self._bg_color
        self.kicker.text = weekday
        self.fortune_label.text = fortune
        self.message_label.text = message

    def save_card(self, filepath):
        # カード部分だけをPNG画像として保存します。
        self.export_to_png(filepath)


class TanakujiApp(App):
    title = "きょうの運だめし"

    def build(self):
        # デスクトップで動かすときの仮サイズ。スマホでは画面に合わせて表示されます。
        Window.clearcolor = (0.12, 0.10, 0.18, 1)

        self.running = False
        self.remaining = 0.0
        self.interval_event = None
        self.timer_event = None
        self.weekly_event = None
        self.change_interval = 0.1
        self.last_fortune = None
        self.weekly_index = 0
        self.weekly_mode = False
        self.weekly_manual_mode = False
        self.weekly_capture_mode = False
        self.save_folder = os.path.join(APP_DIR, "tanakuji_photos")
        os.makedirs(self.save_folder, exist_ok=True)

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(18), dp(18), dp(14)],
            spacing=dp(12),
        )

        title = Label(
            text="[b]きょうの運だめし[/b]",
            markup=True,
            font_name=FONT_PATH,
            font_size="27sp",
            size_hint=(1, 0.10),
            color=(1, 1, 1, 1),
        )
        root.add_widget(title)

        self.card = FortuneCard(size_hint=(1, 0.60))
        root.add_widget(self.card)

        controls = BoxLayout(
            orientation="vertical", spacing=dp(9), size_hint=(1, 0.20)
        )
        top_row = BoxLayout(spacing=dp(8), size_hint=(1, 0.42))

        self.duration_spinner = Spinner(
            text="10秒",
            values=("10秒", "20秒"),
            font_name=FONT_PATH,
            font_size="18sp",
            size_hint=(0.28, 1),
            background_normal="",
            background_color=(0.32, 0.28, 0.48, 1),
            color=(1, 1, 1, 1),
            option_cls=FontSpinnerOption,
        )
        self.day_spinner = Spinner(
            text="月曜日",
            values=("月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"),
            font_name=FONT_PATH,
            font_size="18sp",
            size_hint=(0.30, 1),
            background_normal="",
            background_color=(0.38, 0.50, 0.72, 1),
            color=(1, 1, 1, 1),
            option_cls=FontSpinnerOption,
        )
        self.start_button = Button(
            text="スタート",
            font_name=FONT_PATH,
            font_size="20sp",
            bold=True,
            size_hint=(0.22, 1),
            background_normal="",
            background_color=(0.22, 0.62, 0.42, 1),
        )
        self.week_button = Button(
            text="1週間を撮る",
            font_name=FONT_PATH,
            font_size="17sp",
            bold=True,
            size_hint=(0.20, 1),
            background_normal="",
            background_color=(0.58, 0.44, 0.85, 1),
        )
        self.start_button.bind(on_release=self.start_draw)
        self.week_button.bind(on_release=self.start_weekly_capture)
        top_row.add_widget(self.duration_spinner)
        top_row.add_widget(self.day_spinner)
        top_row.add_widget(self.start_button)
        top_row.add_widget(self.week_button)
        controls.add_widget(top_row)

        bottom_row = BoxLayout(spacing=dp(8), size_hint=(1, 0.42))
        self.capture_button = Button(
            text="この瞬間を撮影",
            font_name=FONT_PATH,
            font_size="18sp",
            background_normal="",
            background_color=(0.95, 0.48, 0.24, 1),
        )
        self.capture_button.bind(on_release=self.capture_now)
        self.capture_button.disabled = True

        self.status_label = Label(
            text="曜日を選んで、気に入った瞬間を撮影！",
            font_name=FONT_PATH,
            font_size="14sp",
            color=(0.92, 0.90, 1, 1),
            halign="center",
        )
        bottom_row.add_widget(self.capture_button)
        bottom_row.add_widget(self.status_label)
        controls.add_widget(bottom_row)

        root.add_widget(controls)

        self.gallery_label = Label(
            text="保存済み写真",
            font_name=FONT_PATH,
            font_size="15sp",
            color=(1, 1, 1, 1),
            size_hint=(1, 0.08),
        )
        root.add_widget(self.gallery_label)

        self.gallery_scroll = ScrollView(
            size_hint=(1, 0.18),
            do_scroll_x=True,
            do_scroll_y=False,
            bar_width=0,
        )
        self.gallery_content = BoxLayout(
            size_hint_x=None,
            width=0,
            spacing=dp(8),
            padding=[dp(4), 0, dp(4), 0],
        )
        self.gallery_scroll.add_widget(self.gallery_content)
        root.add_widget(self.gallery_scroll)

        self.refresh_gallery()
        apply_font(root, FONT_PATH)
        return root

    def refresh_gallery(self):
        for child in list(self.gallery_content.children):
            self.gallery_content.remove_widget(child)

        image_files = []
        if os.path.isdir(self.save_folder):
            image_files = [
                os.path.join(self.save_folder, name)
                for name in os.listdir(self.save_folder)
                if name.lower().endswith(".png")
            ]
            image_files.sort(key=os.path.getmtime, reverse=True)

        max_items = 6
        for path in image_files[:max_items]:
            button = Button(
                size_hint_x=None,
                width=dp(110),
                background_normal="",
                background_color=(0, 0, 0, 0),
            )
            button.bind(on_release=lambda _, p=path: self.open_image_preview(p))
            image = Image(source=path, allow_stretch=True, keep_ratio=True)
            image.size_hint = (1, 1)
            button.add_widget(image)
            self.gallery_content.add_widget(button)

        self.gallery_content.width = max(dp(110) * min(len(image_files[:max_items]), max_items), dp(200))

    def open_image_preview(self, path):
        popup_content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(12))
        preview = Image(source=path, allow_stretch=True, keep_ratio=True)
        preview.size_hint = (1, 0.8)

        action_row = BoxLayout(size_hint=(1, 0.12), spacing=dp(8))
        open_folder = Button(text="保存先フォルダを開く", font_name=FONT_PATH)
        open_folder.bind(on_release=lambda *_: self.open_save_folder())
        close = Button(text="閉じる", font_name=FONT_PATH)
        close.bind(on_release=lambda *_: popup.dismiss())
        action_row.add_widget(open_folder)
        action_row.add_widget(close)

        popup_content.add_widget(preview)
        popup_content.add_widget(action_row)

        popup = Popup(
            title=os.path.basename(path),
            content=popup_content,
            size_hint=(0.9, 0.8),
            auto_dismiss=True,
        )
        popup.open()

    def open_save_folder(self):
        if os.path.isdir(self.save_folder):
            try:
                subprocess.Popen(["open", self.save_folder])
                self.status_label.text = f"フォルダを開きました: {self.save_folder}"
            except Exception as exc:
                self.status_label.text = f"フォルダを開けませんでした: {exc}"

    def choose_fortune(self):
        # 直前の運勢名が連続しないようにします。
        choices = [f for f in FORTUNES if f != self.last_fortune]
        fortune = random.choice(choices)
        self.last_fortune = fortune

        palettes = [
            (0.98, 0.78, 0.32), (0.98, 0.60, 0.55), (0.58, 0.82, 0.72),
            (0.66, 0.75, 0.98), (0.87, 0.68, 0.94), (0.98, 0.84, 0.67),
            (0.73, 0.88, 0.98), (0.98, 0.72, 0.80), (0.80, 0.88, 0.55),
        ]
        self.card.show_fortune(
            fortune, random.choice(MESSAGES), random.choice(palettes)
        )

    def choose_weekday_fortune(self, weekday):
        choices = [f for f in FORTUNES if f != self.last_fortune]
        fortune = random.choice(choices)
        self.last_fortune = fortune

        palettes = [
            (0.98, 0.78, 0.32), (0.98, 0.60, 0.55), (0.58, 0.82, 0.72),
            (0.66, 0.75, 0.98), (0.87, 0.68, 0.94), (0.98, 0.84, 0.67),
            (0.73, 0.88, 0.98), (0.98, 0.72, 0.80), (0.80, 0.88, 0.55),
        ]
        self.card.show_weekday(
            weekday,
            fortune,
            random.choice(MESSAGES),
            random.choice(palettes),
        )

    def get_selected_weekday(self):
        return self.day_spinner.text if self.day_spinner and self.day_spinner.text in WEEKDAYS else "月曜日"

    def start_draw(self, *_):
        self.stop_events()
        self.running = True
        self.weekly_mode = False
        self.remaining = 10 if self.duration_spinner.text == "10秒" else 20
        self.start_button.text = "もう一度スタート"
        self.duration_spinner.disabled = True
        self.day_spinner.disabled = False
        self.capture_button.disabled = False
        self.choose_fortune()
        selected_day = self.get_selected_weekday()
        self.status_label.text = f"{selected_day} を撮影中… 0.1秒ごとに切り替わるカードから気に入った瞬間を保存"

        self.interval_event = Clock.schedule_interval(self.tick_card, 0.1)
        self.timer_event = Clock.schedule_interval(self.tick_timer, 0.1)

    def start_weekly_capture(self, *_):
        self.stop_events()
        self.running = True
        self.weekly_mode = False
        self.weekly_manual_mode = False
        self.weekly_capture_mode = True
        self.weekly_index = 0
        self.remaining = 10 if self.duration_spinner.text == "10秒" else 20
        if hasattr(self, "start_button"):
            self.start_button.disabled = True
        if hasattr(self, "week_button"):
            self.week_button.disabled = True
        if hasattr(self, "duration_spinner"):
            self.duration_spinner.disabled = True
        if hasattr(self, "day_spinner"):
            self.day_spinner.disabled = False
        if hasattr(self, "capture_button"):
            self.capture_button.disabled = False
        self._show_weekday_card()
        self.interval_event = Clock.schedule_interval(self.tick_card, 0.1)
        self.timer_event = Clock.schedule_interval(self.tick_timer, 0.1)

    def _show_weekday_card(self):
        if not self.weekly_capture_mode or self.weekly_index >= len(WEEKDAYS):
            self._finish_weekly_capture()
            return
        weekday = WEEKDAYS[self.weekly_index]
        if hasattr(self, "day_spinner"):
            self.day_spinner.text = weekday
        self.choose_weekday_fortune(weekday)
        self.status_label.text = f"{weekday} の {self.remaining:.0f} 秒の中から気に入った1枚を撮影してください"

    def _finish_weekly_capture(self):
        self.running = False
        self.weekly_mode = False
        self.weekly_manual_mode = False
        self.weekly_capture_mode = False
        if hasattr(self, "start_button"):
            self.start_button.disabled = False
        if hasattr(self, "week_button"):
            self.week_button.disabled = False
        if hasattr(self, "duration_spinner"):
            self.duration_spinner.disabled = False
        if hasattr(self, "day_spinner"):
            self.day_spinner.disabled = False
        if hasattr(self, "capture_button"):
            self.capture_button.disabled = True
        self.status_label.text = "1週間分の撮影を終了しました。"

    def tick_card(self, _dt):
        if self.running and not self.weekly_manual_mode:
            self.choose_fortune()

    def tick_timer(self, dt):
        if not self.running:
            return
        if self.weekly_capture_mode:
            self.remaining -= dt
            if self.remaining <= 0:
                self.remaining = 0
                self.capture_now()
                return
            current_weekday = self.get_selected_weekday()
            self.status_label.text = f"{current_weekday} の残り {self.remaining:.1f} 秒"
            return
        if self.weekly_mode or self.weekly_manual_mode:
            return
        self.remaining -= dt
        if self.remaining <= 0:
            self.remaining = 0
            self.finish_draw()
        else:
            self.status_label.text = f"残り {self.remaining:.1f} 秒"

    def capture_now(self, *_):
        if not self.running:
            return
        if self.weekly_capture_mode:
            self.save_current_card(prefix=f"{self.get_selected_weekday()}")
            self.weekly_index += 1
            if self.weekly_index < len(WEEKDAYS):
                self.remaining = 10 if self.duration_spinner.text == "10秒" else 20
                self._show_weekday_card()
            else:
                self._finish_weekly_capture()
            return
        if self.weekly_manual_mode:
            self.save_current_card(prefix=f"{self.get_selected_weekday()}")
            self.weekly_index += 1
            if self.weekly_index < len(WEEKDAYS):
                self._show_weekday_card()
            else:
                self._finish_weekly_capture()
            return
        self.finish_draw(manual=True)

    def finish_draw(self, manual=False):
        self.running = False
        self.stop_events()
        if hasattr(self, "duration_spinner"):
            self.duration_spinner.disabled = False
        if hasattr(self, "capture_button"):
            self.capture_button.disabled = True
        self.save_current_card(prefix=self.get_selected_weekday())

        if manual:
            self.status_label.text = f"{self.get_selected_weekday()} を撮影しました！画像を保存しました。"
        else:
            self.status_label.text = f"時間終了！{self.get_selected_weekday()} の最後の運勢を保存しました。"

    def stop_events(self):
        if self.interval_event is not None:
            self.interval_event.cancel()
            self.interval_event = None
        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None
        if self.weekly_event is not None:
            self.weekly_event.cancel()
            self.weekly_event = None

    def save_current_card(self, prefix="tanakuji"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(
            c if c.isalnum() else "_" for c in self.card.fortune_label.text
        )
        safe_prefix = "".join(c if c.isalnum() else "_" for c in str(prefix))
        filepath = os.path.join(
            self.save_folder, f"{safe_prefix}_{timestamp}_{safe_name}.png"
        )
        try:
            self.card.save_card(filepath)
            self.status_label.text = f"保存先: {filepath}"
            self.refresh_gallery()
        except Exception as exc:
            self.status_label.text = f"保存に失敗しました: {exc}"

    def on_start(self):
        self.refresh_gallery()

    def on_stop(self):
        self.stop_events()


if __name__ == "__main__":
    TanakujiApp().run()
