"""生成 Chrome Web Store 上架素材。

输出（marketing/output/）：
  store-hero-1280x800.png   — 主视觉：模仿 claude.ai 的 tool-use limit 提示 + 自动点视觉
  store-popup-1280x800.png  — 展示扩展的 popup 面板
  store-flow-1280x800.png   — 三步流程图
  promo-tile-440x280.png    — 商店浏览页小图

字体策略：CJK 用 Hiragino Sans GB（macOS 系统自带），英文用 Helvetica。
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
ICON_DIR = ROOT.parent / "icons"

# Colors
YELLOW = (250, 204, 21)
YELLOW_DARK = (202, 138, 4)
BG_CREAM = (254, 253, 248)
BG_WHITE = (255, 255, 255)
GRAY_BORDER = (231, 229, 228)
GRAY_TEXT = (87, 83, 78)
GRAY_LIGHT = (250, 250, 249)
BLACK = (24, 24, 27)
GREEN = (22, 163, 74)

# Fonts
F_CN = "/System/Library/Fonts/Hiragino Sans GB.ttc"
F_EN = "/System/Library/Fonts/Helvetica.ttc"


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


# Hiragino Sans GB has both CN and Latin coverage; use it everywhere to avoid
# tofu boxes from missing CJK glyphs in Helvetica.
def cn(size, bold=False):
    return font(F_CN, size, index=1 if bold else 0)


def en(size, bold=False):
    # Alias: same font as cn() — Hiragino covers Latin too. Kept for readability.
    return font(F_CN, size, index=1 if bold else 0)


def rounded_rect(d, xy, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text_w(d, text, fnt):
    bbox = d.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def paste_icon(canvas, size, position):
    icon_src = Image.open(ICON_DIR / "icon128.png").convert("RGBA")
    icon = icon_src.resize((size, size), Image.LANCZOS)
    canvas.paste(icon, position, icon)


# ────────────────────────────────────────────────────────────────────
# 1. Hero — mock claude.ai 的 tool-use limit 提示
# ────────────────────────────────────────────────────────────────────

def make_hero():
    W, H = 1280, 800
    img = Image.new("RGB", (W, H), BG_CREAM)
    d = ImageDraw.Draw(img)

    # 左上 logo
    paste_icon(img, 56, (60, 50))
    d.text((130, 64), "Claude Auto Continue", font=cn(22, bold=True), fill=BLACK)

    # 主文案
    title_y = 150
    d.text((60, title_y), "不用再手动点", font=cn(72, bold=True), fill=BLACK)
    # "Continue" 黄色高亮
    pre_w = text_w(d, "不用再手动点 ", cn(72, bold=True))
    cont_text = "Continue"
    cont_w = text_w(d, cont_text, en(72, bold=True))
    cont_x = 60 + pre_w
    d.rounded_rectangle(
        [cont_x - 14, title_y - 4, cont_x + cont_w + 14, title_y + 90],
        radius=10,
        fill=YELLOW,
    )
    d.text((cont_x, title_y), cont_text, font=en(72, bold=True), fill=BLACK)
    d.text((60 + pre_w + cont_w + 30, title_y), "。", font=cn(72, bold=True), fill=BLACK)

    # 副文案
    d.text(
        (60, title_y + 120),
        "一个 Chrome 扩展。它替你点。安全、本地、可关。",
        font=cn(28),
        fill=GRAY_TEXT,
    )

    # 中间偏下：模仿 claude.ai 的 limit 提示卡片
    card_x, card_y, card_w, card_h = 60, 470, 1160, 110
    rounded_rect(d, [card_x, card_y, card_x + card_w, card_y + card_h], 12,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=1)

    # info 圆圈
    info_cx, info_cy = card_x + 50, card_y + card_h // 2
    d.ellipse([info_cx - 14, info_cy - 14, info_cx + 14, info_cy + 14],
              fill=GRAY_LIGHT, outline=GRAY_BORDER, width=1)
    d.text((info_cx - 4, info_cy - 11), "i", font=en(20, bold=True), fill=GRAY_TEXT)

    # limit 文案
    d.text((card_x + 90, card_y + 38),
           "Claude reached its tool-use limit for this turn.",
           font=en(22), fill=GRAY_TEXT)

    # Continue 按钮
    btn_w, btn_h = 130, 46
    btn_x = card_x + card_w - btn_w - 30
    btn_y = card_y + (card_h - btn_h) // 2
    rounded_rect(d, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 8,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=1)
    btn_text = "Continue"
    tw = text_w(d, btn_text, en(18, bold=True))
    d.text((btn_x + (btn_w - tw) // 2, btn_y + 11), btn_text,
           font=en(18, bold=True), fill=BLACK)

    # "已自动点" 黄色徽章贴在按钮右上
    badge_text = "已自动点"
    bw = text_w(d, badge_text, cn(16, bold=True))
    bx = btn_x + btn_w - bw // 2 - 10
    by = btn_y - 18
    rounded_rect(d, [bx - 14, by - 6, bx + bw + 14, by + 24], 14, fill=YELLOW)
    d.text((bx, by), badge_text, font=cn(16, bold=True), fill=BLACK)

    # 下方提示
    d.text((60, 640),
           "claude.ai 单轮工具调用超过约 20 次时弹出 Continue。装上这个扩展，弹一次自动点一次。",
           font=cn(22), fill=GRAY_TEXT)

    img.save(OUT / "store-hero-1280x800.png", optimize=True)
    print("  ✓ store-hero-1280x800.png")


# ────────────────────────────────────────────────────────────────────
# 2. Popup — 展示扩展设置面板
# ────────────────────────────────────────────────────────────────────

def make_popup():
    W, H = 1280, 800
    img = Image.new("RGB", (W, H), BG_CREAM)
    d = ImageDraw.Draw(img)

    # 左侧文案
    d.text((80, 120), "Allowlist 匹配", font=cn(48, bold=True), fill=BLACK)
    d.text((80, 200),
           "只点你授权的按钮文本。",
           font=cn(28), fill=GRAY_TEXT)
    d.text((80, 248),
           "其他全部跳过。包括登录、删除、付款。",
           font=cn(28), fill=GRAY_TEXT)

    # bullets
    bullets = [
        ("默认匹配", "Continue / 继续 / 继续生成"),
        ("默认排除", "Continue with / Cancel / 删除"),
        ("可自定义", "popup 里增删，无需改代码"),
    ]
    by = 340
    for label, text in bullets:
        # 黄色小圆点
        d.ellipse([80, by + 8, 96, by + 24], fill=YELLOW)
        d.text((110, by), label, font=cn(22, bold=True), fill=BLACK)
        d.text((110, by + 32), text, font=cn(20), fill=GRAY_TEXT)
        by += 90

    # 右侧 popup mock
    popup_x, popup_y, popup_w, popup_h = 720, 90, 480, 620
    rounded_rect(d, [popup_x, popup_y, popup_x + popup_w, popup_y + popup_h], 14,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=1)
    # 顶部标题
    d.text((popup_x + 30, popup_y + 30), "Claude Auto Continue",
           font=cn(20, bold=True), fill=BLACK)

    # 启用开关行
    row_y = popup_y + 90
    d.text((popup_x + 30, row_y), "启用自动点击", font=cn(18), fill=BLACK)
    # 开关
    sw_x, sw_y = popup_x + popup_w - 80, row_y - 4
    rounded_rect(d, [sw_x, sw_y, sw_x + 50, sw_y + 28], 14, fill=YELLOW_DARK)
    d.ellipse([sw_x + 24, sw_y + 2, sw_x + 48, sw_y + 26], fill=BG_WHITE)

    # 计数卡片
    stat_y = popup_y + 150
    rounded_rect(d, [popup_x + 24, stat_y, popup_x + popup_w - 24, stat_y + 60], 8,
                 fill=(255, 247, 237), outline=(254, 215, 170), width=1)
    d.text((popup_x + 40, stat_y + 12), "已自动点击", font=cn(14), fill=GRAY_TEXT)
    d.text((popup_x + 40, stat_y + 30), "127 次",
           font=cn(20, bold=True), fill=BLACK)

    # 匹配文本框
    box_y = popup_y + 240
    d.text((popup_x + 30, box_y), "匹配按钮文本", font=cn(14, bold=True), fill=BLACK)
    rounded_rect(d, [popup_x + 24, box_y + 24, popup_x + popup_w - 24, box_y + 130], 6,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=1)
    sample = ["continue", "continue generating", "继续", "继续生成"]
    for i, line in enumerate(sample):
        d.text((popup_x + 36, box_y + 32 + i * 24), line,
               font=en(15), fill=BLACK)

    # 排除框
    exc_y = popup_y + 400
    d.text((popup_x + 30, exc_y), "排除含这些子串的按钮",
           font=cn(14, bold=True), fill=BLACK)
    rounded_rect(d, [popup_x + 24, exc_y + 24, popup_x + popup_w - 24, exc_y + 110], 6,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=1)
    exsample = ["continue with", "cancel", "delete", "删除"]
    for i, line in enumerate(exsample):
        d.text((popup_x + 36, exc_y + 32 + i * 20), line,
               font=en(13), fill=BLACK)

    # 保存按钮
    btn_y = popup_y + 540
    btn_w_ = 140
    btn_x = popup_x + 24
    rounded_rect(d, [btn_x, btn_y, btn_x + btn_w_, btn_y + 36], 6,
                 fill=YELLOW_DARK)
    d.text((btn_x + 50, btn_y + 9), "保存",
           font=cn(15, bold=True), fill=BG_WHITE)

    img.save(OUT / "store-popup-1280x800.png", optimize=True)
    print("  ✓ store-popup-1280x800.png")


# ────────────────────────────────────────────────────────────────────
# 3. Flow — 三步流程
# ────────────────────────────────────────────────────────────────────

def make_flow():
    W, H = 1280, 800
    img = Image.new("RGB", (W, H), BG_CREAM)
    d = ImageDraw.Draw(img)

    d.text((80, 80), "它怎么工作", font=cn(48, bold=True), fill=BLACK)
    d.text((80, 160),
           "三层防护，确保只点对的按钮。",
           font=cn(26), fill=GRAY_TEXT)

    steps = [
        ("01", "MutationObserver",
         ["守在 DOM 上，", "按钮一出现就检测，", "无轮询开销。"]),
        ("02", "Allowlist + Exclude",
         ["文本必须命中匹配列表，", "且不含排除关键词。"]),
        ("03", "频率限制",
         ["两次点击 ≥1.5s 间隔，", "同按钮 3s 内不重点。"]),
    ]
    base_y = 280
    for i, (num, title, desc_lines) in enumerate(steps):
        x = 80 + i * 380
        d.text((x, base_y), num, font=en(96, bold=True), fill=YELLOW_DARK)
        d.rectangle([x, base_y + 110, x + 60, base_y + 116], fill=YELLOW)
        d.text((x, base_y + 140), title, font=cn(26, bold=True), fill=BLACK)
        for li, line in enumerate(desc_lines):
            d.text((x, base_y + 190 + li * 32), line, font=cn(20), fill=GRAY_TEXT)

    # 底部强调
    paste_icon(img, 48, (80, 700))
    d.text((140, 712), "本地运行 · 零网络请求 · 可随时关闭",
           font=cn(22, bold=True), fill=BLACK)

    img.save(OUT / "store-flow-1280x800.png", optimize=True)
    print("  ✓ store-flow-1280x800.png")


# ────────────────────────────────────────────────────────────────────
# 4. Promo tile 440x280
# ────────────────────────────────────────────────────────────────────

def make_promo():
    W, H = 440, 280
    img = Image.new("RGB", (W, H), YELLOW)
    d = ImageDraw.Draw(img)

    paste_icon(img, 64, (32, 32))
    d.text((28, 130), "Claude Auto", font=en(36, bold=True), fill=BLACK)
    d.text((28, 168), "Continue", font=en(36, bold=True), fill=BLACK)
    d.text((28, 216), "不用再手动点 Continue。",
           font=cn(16), fill=BLACK)
    # 角落小标
    d.text((28, 244), "Chrome Extension · MIT",
           font=en(11), fill=BLACK)

    img.save(OUT / "promo-tile-440x280.png", optimize=True)
    print("  ✓ promo-tile-440x280.png")


# ────────────────────────────────────────────────────────────────────
# 5. Marquee promo tile 1400x560 — 商店首页轮播大图
# ────────────────────────────────────────────────────────────────────

def make_marquee():
    W, H = 1400, 560
    img = Image.new("RGB", (W, H), BG_CREAM)
    d = ImageDraw.Draw(img)

    # 左侧黄色背景块（占 55%）
    split_x = int(W * 0.55)
    d.rectangle([0, 0, split_x, H], fill=YELLOW)

    # 左侧：logo + 标题
    paste_icon(img, 80, (60, 60))
    d.text((160, 78), "Claude Auto Continue",
           font=cn(28, bold=True), fill=BLACK)

    # 大标题
    d.text((60, 200), "不用再手动点", font=cn(64, bold=True), fill=BLACK)
    d.text((60, 280), "Continue。", font=cn(64, bold=True), fill=BLACK)

    # 副文案
    d.text((60, 400),
           "一个 Chrome 扩展。它替你点。",
           font=cn(22), fill=BLACK)
    d.text((60, 432),
           "安全、本地、可关。",
           font=cn(22), fill=BLACK)

    # 右侧：仿 claude.ai 的提示卡片
    card_x = split_x + 60
    card_y = 200
    card_w = W - card_x - 60
    card_h = 110
    rounded_rect(d, [card_x, card_y, card_x + card_w, card_y + card_h], 12,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=1)

    # info 圆圈
    info_cx, info_cy = card_x + 38, card_y + card_h // 2
    d.ellipse([info_cx - 12, info_cy - 12, info_cx + 12, info_cy + 12],
              fill=GRAY_LIGHT, outline=GRAY_BORDER, width=1)
    d.text((info_cx - 3, info_cy - 9), "i", font=cn(16, bold=True), fill=GRAY_TEXT)

    # limit 文案
    d.text((card_x + 64, card_y + 32),
           "Claude reached its tool-use",
           font=en(16), fill=GRAY_TEXT)
    d.text((card_x + 64, card_y + 56),
           "limit for this turn.",
           font=en(16), fill=GRAY_TEXT)

    # Continue 按钮
    btn_w, btn_h = 100, 40
    btn_x = card_x + card_w - btn_w - 20
    btn_y = card_y + (card_h - btn_h) // 2
    rounded_rect(d, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 8,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=1)
    btn_text = "Continue"
    tw = text_w(d, btn_text, en(16, bold=True))
    d.text((btn_x + (btn_w - tw) // 2, btn_y + 11), btn_text,
           font=en(16, bold=True), fill=BLACK)

    # 黄色"已自动点"徽章
    badge_text = "已自动点"
    bw = text_w(d, badge_text, cn(14, bold=True))
    bx = btn_x + btn_w - bw // 2 - 8
    by = btn_y - 14
    rounded_rect(d, [bx - 12, by - 4, bx + bw + 12, by + 22], 12, fill=YELLOW)
    d.text((bx, by), badge_text, font=cn(14, bold=True), fill=BLACK)

    # 下方箭头 + 状态
    arrow_y = card_y + card_h + 30
    d.text((card_x + 30, arrow_y), "↓", font=cn(20), fill=GRAY_TEXT)

    status_y = arrow_y + 40
    status_x = card_x + 20
    rounded_rect(d, [status_x, status_y, status_x + card_w - 40, status_y + 50], 8,
                 fill=(255, 247, 237), outline=(254, 215, 170), width=1)
    d.text((status_x + 18, status_y + 16),
           "对话继续。今日已自动点击 38 次。",
           font=cn(15), fill=BLACK)

    img.save(OUT / "store-marquee-1400x560.png", optimize=True)
    print("  ✓ store-marquee-1400x560.png")


# ────────────────────────────────────────────────────────────────────
# 6. 小红书封面 1080x1440 (3:4 竖版) + 第二张内容图
# ────────────────────────────────────────────────────────────────────

def make_xiaohongshu_cover():
    W, H = 1080, 1440
    img = Image.new("RGB", (W, H), YELLOW)
    d = ImageDraw.Draw(img)

    # 顶部小标
    paste_icon(img, 90, (60, 70))
    d.text((170, 90), "Claude Auto Continue",
           font=cn(28, bold=True), fill=BLACK)
    d.text((170, 130), "/ Chrome 扩展", font=cn(22), fill=BLACK)

    # 主标题（大字，三行）
    d.text((60, 320), "再也不用", font=cn(110, bold=True), fill=BLACK)
    d.text((60, 460), "点 Continue", font=cn(110, bold=True), fill=BLACK)
    d.text((60, 600), "了", font=cn(110, bold=True), fill=BLACK)

    # 中段说明
    d.text((60, 800),
           "Claude.ai 一天点几十次 Continue",
           font=cn(34), fill=BLACK)
    d.text((60, 850),
           "我做了个扩展替我点",
           font=cn(34), fill=BLACK)

    # 底部强调（黑色色块 + 白字）
    rect_y = 1100
    d.rectangle([60, rect_y, W - 60, rect_y + 200], fill=BLACK)
    d.text((90, rect_y + 30), "开源 · 本地运行", font=cn(36, bold=True), fill=YELLOW)
    d.text((90, rect_y + 90), "MIT License", font=cn(28), fill=BG_WHITE)
    d.text((90, rect_y + 140),
           "github.com/lijiarui/claude-auto-continue",
           font=cn(22), fill=BG_WHITE)

    # 右上角"5 分钟"圆形贴纸
    cx, cy, r = 920, 230, 100
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLACK)
    d.text((cx - 50, cy - 60), "5 分钟", font=cn(28, bold=True), fill=YELLOW)
    d.text((cx - 50, cy - 20), "搞定", font=cn(36, bold=True), fill=BG_WHITE)
    d.text((cx - 50, cy + 30), "免费", font=cn(28), fill=YELLOW)

    img.save(OUT / "xiaohongshu-cover-1080x1440.png", optimize=True)
    print("  ✓ xiaohongshu-cover-1080x1440.png")


def make_xiaohongshu_value():
    """第二张：放大版的"自动点击"价值传达，3:4 竖版。"""
    W, H = 1080, 1440
    img = Image.new("RGB", (W, H), BG_CREAM)
    d = ImageDraw.Draw(img)

    # 顶部标题
    d.text((60, 80), "原本：", font=cn(36, bold=True), fill=GRAY_TEXT)
    d.text((60, 140), "你手动点 Continue", font=cn(50, bold=True), fill=BLACK)

    # 模拟 claude.ai 的提示卡
    card_x, card_y, card_w, card_h = 60, 240, W - 120, 130
    rounded_rect(d, [card_x, card_y, card_x + card_w, card_y + card_h], 14,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=2)
    info_cx, info_cy = card_x + 50, card_y + card_h // 2
    d.ellipse([info_cx - 16, info_cy - 16, info_cx + 16, info_cy + 16],
              fill=GRAY_LIGHT, outline=GRAY_BORDER, width=2)
    d.text((info_cx - 5, info_cy - 14), "i", font=cn(22, bold=True), fill=GRAY_TEXT)
    d.text((card_x + 100, card_y + 30),
           "Claude reached its", font=en(22), fill=GRAY_TEXT)
    d.text((card_x + 100, card_y + 60),
           "tool-use limit for this turn.", font=en(22), fill=GRAY_TEXT)
    btn_w, btn_h = 130, 50
    btn_x = card_x + card_w - btn_w - 30
    btn_y = card_y + (card_h - btn_h) // 2
    rounded_rect(d, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 8,
                 fill=BG_WHITE, outline=GRAY_BORDER, width=2)
    tw = text_w(d, "Continue", en(22, bold=True))
    d.text((btn_x + (btn_w - tw) // 2, btn_y + 14),
           "Continue", font=en(22, bold=True), fill=BLACK)

    # 中间：大箭头
    d.text((W // 2 - 30, 440), "↓", font=cn(80, bold=True), fill=YELLOW_DARK)

    # 装上扩展之后
    d.text((60, 580), "现在：", font=cn(36, bold=True), fill=GRAY_TEXT)
    d.text((60, 640), "扩展替你点掉", font=cn(50, bold=True), fill=BLACK)

    # 黄色卡片（高亮）
    yc_x, yc_y, yc_w, yc_h = 60, 740, W - 120, 200
    rounded_rect(d, [yc_x, yc_y, yc_x + yc_w, yc_y + yc_h], 14, fill=YELLOW)
    paste_icon(img, 80, (yc_x + 40, yc_y + 60))
    d.text((yc_x + 150, yc_y + 50),
           "已自动点 87 次", font=cn(48, bold=True), fill=BLACK)
    d.text((yc_x + 150, yc_y + 120),
           "今日 0 次手动操作", font=cn(28), fill=BLACK)

    # 底部三层防护
    d.text((60, 1010), "三层防误点：", font=cn(28, bold=True), fill=BLACK)
    bullets = [
        "1. Allowlist：只点 Continue / 继续 / 继续生成",
        "2. Exclude：跳过 Continue with / Cancel / 删除",
        "3. 节流：1.5s 间隔，同按钮 3s 内不重点",
    ]
    for i, line in enumerate(bullets):
        by_ = 1070 + i * 50
        d.ellipse([60, by_ + 12, 76, by_ + 28], fill=YELLOW_DARK)
        d.text((96, by_), line, font=cn(24), fill=BLACK)

    # 底部
    d.text((60, 1340),
           "github.com/lijiarui/claude-auto-continue",
           font=cn(22), fill=GRAY_TEXT)

    img.save(OUT / "xiaohongshu-value-1080x1440.png", optimize=True)
    print("  ✓ xiaohongshu-value-1080x1440.png")


if __name__ == "__main__":
    print("Generating Chrome Web Store assets...")
    make_hero()
    make_popup()
    make_flow()
    make_promo()
    make_marquee()
    print("\nGenerating 小红书 assets...")
    make_xiaohongshu_cover()
    make_xiaohongshu_value()
    print(f"\nAll assets in: {OUT}")
