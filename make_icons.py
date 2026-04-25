"""生成扩展图标。亮黄底 + 黑色双箭头，高对比度，16px 也清晰。"""
from PIL import Image, ImageDraw
from pathlib import Path

YELLOW = (250, 204, 21, 255)      # tailwind yellow-400
YELLOW_DARK = (202, 138, 4, 255)  # 边框/阴影
BLACK = (24, 24, 27, 255)          # zinc-900
OUT_DIR = Path(__file__).parent / "icons"
OUT_DIR.mkdir(exist_ok=True)


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 圆角方形底色，几乎填满整个画布（图标已经够小）
    pad = max(1, size // 32)
    radius = size // 5
    d.rounded_rectangle(
        [pad, pad, size - pad - 1, size - pad - 1],
        radius=radius,
        fill=YELLOW,
        outline=YELLOW_DARK,
        width=max(1, size // 32),
    )

    # 双箭头 >>，用两个粗 V 形拼出来
    # 箭头位于中心稍偏左，整体占图标 ~60% 宽
    cx, cy = size / 2, size / 2
    arrow_w = size * 0.22       # 单个 chevron 横向宽度
    arrow_h = size * 0.50       # chevron 高度
    stroke = max(2, int(size * 0.14))
    gap = size * 0.10           # 两箭头之间间距
    total = arrow_w * 2 + gap
    start_x = cx - total / 2

    for i in range(2):
        ax = start_x + i * (arrow_w + gap)
        top = (ax, cy - arrow_h / 2)
        mid = (ax + arrow_w, cy)
        bot = (ax, cy + arrow_h / 2)
        d.line([top, mid], fill=BLACK, width=stroke, joint="curve")
        d.line([mid, bot], fill=BLACK, width=stroke, joint="curve")

    return img


for size in (16, 32, 48, 128):
    icon = make_icon(size)
    path = OUT_DIR / f"icon{size}.png"
    icon.save(path)
    print(f"wrote {path} ({size}x{size})")
