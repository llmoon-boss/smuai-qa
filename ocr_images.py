import os
import sys

from rapidocr_onnxruntime import RapidOCR

IMG_DIR = "smudata"
OUT_DIR = os.path.join(IMG_DIR, "extracted")
os.makedirs(OUT_DIR, exist_ok=True)

paths = [
    os.path.join(IMG_DIR, "地图.png"),
]
paths += sorted(
    os.path.join(IMG_DIR, "图片", f)
    for f in os.listdir(os.path.join(IMG_DIR, "图片"))
    if f.lower().endswith(".png")
)

engine = RapidOCR()

for path in paths:
    name = os.path.splitext(os.path.basename(path))[0]
    print("=" * 30, name, "=" * 30)
    out = engine(path)
    lines = []
    if out is not None:
        # 兼容不同版本 API
        if hasattr(out, "txts"):
            lines = list(out.txts)
        elif isinstance(out, tuple):
            lines = [item[1] for item in (out[0] or [])]
        else:
            lines = [item[1] for item in (out or [])]
    for t in lines:
        print(t)
    if not lines:
        print("（未识别到文字）")
    with open(os.path.join(OUT_DIR, f"ocr_{name}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print()
