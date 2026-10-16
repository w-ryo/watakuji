const WEEKDAYS = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"];

const PREFIXES = [
  "ダークホース", "伏兵あらわる", "寝坊したけど", "最後に笑う", "主役は遅れて",
  "まさかの展開", "追い風に乗る", "奇跡の予感", "隠れた才能", "逆転ホームラン",
  "棚からぼたもち", "思わぬところに", "今日だけ無敵", "幸運の抜け道", "静かなる勝者",
  "ひらめき暴走", "ご縁が急接近", "努力が発芽", "運命のいたずら", "小さな革命",
  "眠れる獅子", "レアキャラ遭遇", "人生の伏線回収", "ピンチがチャンス", "笑う門には",
  "直感が冴える", "気まぐれ天使", "福が迷い込む", "追試を回避する", "主役級の偶然",
  "雲の上の気分", "幸せの前借り", "勝手に好転", "まわりまわって", "急にモテ期",
  "願いがすべりこむ", "大器晩成モード", "なんか持ってる", "予想外の才能", "明日はもっと",
];

const SUFFIXES = ["大吉", "中吉", "小吉", "吉", "末吉"];
const FORTUNES = PREFIXES.flatMap((prefix) => SUFFIXES.map((suffix) => `${prefix}${suffix}`));
const MESSAGES = [
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
];

const state = {
  running: false,
  remaining: 10,
  intervalId: null,
  timerId: null,
  lastFortune: null,
  weeklyCaptureMode: false,
  weeklyIndex: 0,
  savedImages: loadSavedImages(),
};

const fortuneCard = document.getElementById("fortuneCard");
const cardKicker = document.getElementById("cardKicker");
const fortuneLabel = document.getElementById("fortuneLabel");
const messageLabel = document.getElementById("messageLabel");
const statusText = document.getElementById("statusText");
const durationSelect = document.getElementById("durationSelect");
const daySelect = document.getElementById("daySelect");
const startButton = document.getElementById("startButton");
const weeklyButton = document.getElementById("weeklyButton");
const captureButton = document.getElementById("captureButton");
const gallery = document.getElementById("gallery");

function loadSavedImages() {
  try {
    const value = localStorage.getItem("tanakuji-gallery");
    return value ? JSON.parse(value) : [];
  } catch {
    return [];
  }
}

function saveGalleryToLocalStorage() {
  localStorage.setItem("tanakuji-gallery", JSON.stringify(state.savedImages));
}

function randomPalette() {
  const palettes = [
    [0.98, 0.78, 0.32],
    [0.98, 0.60, 0.55],
    [0.58, 0.82, 0.72],
    [0.66, 0.75, 0.98],
    [0.87, 0.68, 0.94],
    [0.98, 0.84, 0.67],
    [0.73, 0.88, 0.98],
    [0.98, 0.72, 0.80],
    [0.80, 0.88, 0.55],
  ];
  return palettes[Math.floor(Math.random() * palettes.length)];
}

function setCardStyle(color) {
  fortuneCard.style.background = `linear-gradient(180deg, rgb(${color[0] * 255}, ${color[1] * 255}, ${color[2] * 255}), rgb(${Math.min(1, color[0] + 0.08) * 255}, ${Math.min(1, color[1] + 0.1) * 255}, ${Math.min(1, color[2] + 0.05) * 255}))`;
}

function renderCardView({ weekday = null, fortune, message }) {
  const palette = randomPalette();
  setCardStyle(palette);
  if (weekday) {
    cardKicker.textContent = weekday;
  } else {
    cardKicker.textContent = "きょうの運だめし";
  }
  fortuneLabel.textContent = fortune;
  messageLabel.textContent = message;
}

function chooseFortune() {
  const options = FORTUNES.filter((f) => f !== state.lastFortune);
  const fortune = options[Math.floor(Math.random() * options.length)];
  state.lastFortune = fortune;
  renderCardView({ fortune, message: MESSAGES[Math.floor(Math.random() * MESSAGES.length)] });
}

function chooseWeekdayFortune(weekday) {
  const options = FORTUNES.filter((f) => f !== state.lastFortune);
  const fortune = options[Math.floor(Math.random() * options.length)];
  state.lastFortune = fortune;
  renderCardView({ weekday, fortune, message: MESSAGES[Math.floor(Math.random() * MESSAGES.length)] });
}

function stopTimers() {
  if (state.intervalId) {
    clearInterval(state.intervalId);
    state.intervalId = null;
  }
  if (state.timerId) {
    clearInterval(state.timerId);
    state.timerId = null;
  }
}

function getSelectedWeekday() {
  return daySelect.value || "月曜日";
}

function startNormalDraw() {
  stopTimers();
  state.running = true;
  state.weeklyCaptureMode = false;
  state.remaining = Number(durationSelect.value);
  startButton.textContent = "もう一度スタート";
  captureButton.disabled = false;
  statusText.textContent = `${getSelectedWeekday()} を撮影中… 0.1秒ごとに切り替わるカードから気に入った瞬間を保存`;
  chooseFortune();

  state.intervalId = setInterval(() => {
    if (!state.running || state.weeklyCaptureMode) return;
    chooseFortune();
  }, 100);

  state.timerId = setInterval(() => {
    if (!state.running || state.weeklyCaptureMode) return;
    state.remaining = Math.max(0, state.remaining - 0.1);
    if (state.remaining <= 0) {
      finishDraw();
      return;
    }
    statusText.textContent = `残り ${state.remaining.toFixed(1)} 秒`;
  }, 100);
}

function startWeeklyCapture() {
  stopTimers();
  state.running = true;
  state.weeklyCaptureMode = true;
  state.weeklyIndex = 0;
  state.remaining = Number(durationSelect.value);
  startButton.disabled = true;
  weeklyButton.disabled = true;
  captureButton.disabled = false;
  advanceToWeekday();

  state.intervalId = setInterval(() => {
    if (!state.running || !state.weeklyCaptureMode) return;
    chooseFortune();
  }, 100);

  state.timerId = setInterval(() => {
    if (!state.running || !state.weeklyCaptureMode) return;
    state.remaining = Math.max(0, state.remaining - 0.1);
    if (state.remaining <= 0) {
      captureNow();
      return;
    }
    const weekday = WEEKDAYS[state.weeklyIndex] || getSelectedWeekday();
    statusText.textContent = `${weekday} の残り ${state.remaining.toFixed(1)} 秒`;
  }, 100);
}

function advanceToWeekday() {
  if (!state.weeklyCaptureMode || state.weeklyIndex >= WEEKDAYS.length) {
    finishWeeklyCapture();
    return;
  }

  const weekday = WEEKDAYS[state.weeklyIndex];
  daySelect.value = weekday;
  chooseWeekdayFortune(weekday);
  state.remaining = Number(durationSelect.value);
  statusText.textContent = `${weekday} の ${Number(durationSelect.value)} 秒の中から気に入った1枚を撮影してください`;
}

function finishWeeklyCapture() {
  state.running = false;
  state.weeklyCaptureMode = false;
  stopTimers();
  startButton.disabled = false;
  weeklyButton.disabled = false;
  captureButton.disabled = true;
  statusText.textContent = "1週間分の撮影を終了しました。";
}

function captureNow() {
  if (!state.running) return;

  if (state.weeklyCaptureMode) {
    const weekday = getSelectedWeekday();
    saveCurrentCard(weekday);
    state.weeklyIndex += 1;

    if (state.weeklyIndex < WEEKDAYS.length) {
      advanceToWeekday();
    } else {
      finishWeeklyCapture();
    }
    return;
  }

  finishDraw(true);
}

function finishDraw(manual = false) {
  state.running = false;
  stopTimers();
  captureButton.disabled = true;
  saveCurrentCard(getSelectedWeekday());

  if (manual) {
    statusText.textContent = `${getSelectedWeekday()} を撮影しました！画像を保存しました。`;
  } else {
    statusText.textContent = `時間終了！${getSelectedWeekday()} の最後の運勢を保存しました。`;
  }
}

function createPngFromCard(labelText) {
  const canvas = document.createElement("canvas");
  canvas.width = 900;
  canvas.height = 1200;
  const ctx = canvas.getContext("2d");

  const colors = randomPalette();
  ctx.fillStyle = `rgb(${colors[0] * 255}, ${colors[1] * 255}, ${colors[2] * 255})`;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "rgba(255,255,255,0.12)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "rgba(38, 25, 16, 0.92)";
  ctx.font = "700 42px 'Noto Sans JP', sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(cardKicker.textContent || "きょうの運だめし", canvas.width / 2, 130);

  ctx.font = "800 74px 'Noto Sans JP', sans-serif";
  const fortuneText = fortuneLabel.textContent || "準備中";
  wrapText(ctx, fortuneText, canvas.width / 2, 420, 620, 84);

  ctx.font = "500 32px 'Noto Sans JP', sans-serif";
  const messageText = messageLabel.textContent || "";
  wrapText(ctx, messageText, canvas.width / 2, 740, 610, 42);

  ctx.font = "700 28px 'Noto Sans JP', sans-serif";
  ctx.fillText("HAPPY DAY!", canvas.width / 2, 1040);

  ctx.fillStyle = "rgba(0,0,0,0.22)";
  ctx.fillRect(0, 1100, canvas.width, 100);

  ctx.fillStyle = "#fff";
  ctx.font = "700 26px 'Noto Sans JP', sans-serif";
  ctx.fillText(labelText, canvas.width / 2, 1155);

  return canvas.toDataURL("image/png");
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(/(\s+)/);
  let line = "";
  let currentY = y;

  for (const word of words) {
    const test = line + word;
    const metrics = ctx.measureText(test);
    if (metrics.width > maxWidth && line) {
      ctx.fillText(line.trim(), x, currentY);
      line = word;
      currentY += lineHeight;
    } else {
      line = test;
    }
  }

  if (line.trim()) {
    ctx.fillText(line.trim(), x, currentY);
  }
}

function saveCurrentCard(labelText) {
  const name = `${labelText}_${new Date().toISOString().replace(/[:.]/g, "-")}`;
  const image = createPngFromCard(name);

  const item = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    name,
    dataUrl: image,
  };

  state.savedImages.unshift(item);
  state.savedImages = state.savedImages.slice(0, 24);
  saveGalleryToLocalStorage();
  renderGallery();

  const a = document.createElement("a");
  a.href = image;
  a.download = `${name}.png`;
  document.body.appendChild(a);
  a.click();
  a.remove();

  statusText.textContent = `保存先: ${name}.png`;
}

function renderGallery() {
  gallery.innerHTML = "";
  state.savedImages.forEach((item) => {
    const button = document.createElement("button");
    button.className = "thumb";
    button.type = "button";
    button.title = item.name;

    const img = document.createElement("img");
    img.src = item.dataUrl;
    img.alt = item.name;

    const label = document.createElement("span");
    label.className = "thumb-label";
    label.textContent = item.name;

    button.appendChild(img);
    button.appendChild(label);
    button.addEventListener("click", () => {
      const popup = window.open(item.dataUrl, "_blank", "width=420,height=620");
      if (!popup) {
        statusText.textContent = "ポップアップがブロックされました。画像を右クリックで保存してください。";
      }
    });

    gallery.appendChild(button);
  });
}

startButton.addEventListener("click", startNormalDraw);
weeklyButton.addEventListener("click", startWeeklyCapture);
captureButton.addEventListener("click", captureNow);

durationSelect.addEventListener("change", () => {
  if (!state.running) {
    statusText.textContent = `${getSelectedWeekday()} を選んで、気に入った瞬間を撮影！`;
  }
});

renderGallery();
renderCardView({ fortune: "準備中", message: "スタートを押してね！" });
