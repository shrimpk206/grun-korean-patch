"""Noto Sans KR 가변 글꼴 → 게임 굵기 9종(Thin~Black) 고정 글꼴, 한글·영문·기호만 남겨 용량을 줄인다.

원본: https://github.com/google/fonts/tree/main/ofl/notosanskr (SIL OFL 1.1, patch/fonts/OFL.txt)
python patch/make_fonts.py  (patch/work/fontsrc/NotoSansKR[wght].ttf 필요, pip install fonttools)
"""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "work", "fontsrc", "NotoSansKR[wght].ttf")
OUT = os.path.join(HERE, "fonts")
WEIGHTS = {"Thin": 100, "ExtraLight": 200, "Light": 300, "Regular": 400, "Medium": 500,
           "SemiBold": 600, "Bold": 700, "ExtraBold": 800, "Black": 900}
# 게임 문장에 필요한 글자: 라틴·기호·한글. 한자·가나는 뺀다(번역문에 쓰지 않음).
RANGES = [(0x20, 0x7E), (0xA0, 0x24F), (0x2000, 0x206F), (0x2070, 0x209F), (0x20A0, 0x20CF),
          (0x2100, 0x214F), (0x2150, 0x218F), (0x2190, 0x21FF), (0x2200, 0x22FF), (0x2300, 0x23FF),
          (0x2460, 0x24FF), (0x2500, 0x257F), (0x25A0, 0x25FF), (0x2600, 0x26FF), (0x2700, 0x27BF),
          (0x3000, 0x303F), (0x3130, 0x318F), (0x1100, 0x11FF), (0xA960, 0xA97F), (0xD7B0, 0xD7FF),
          (0xAC00, 0xD7A3), (0xFF00, 0xFFEF)]


URL = "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"


def main():
    if not os.path.exists(SRC):  # 원본이 없으면 google/fonts 에서 받는다
        import urllib.request
        os.makedirs(os.path.dirname(SRC), exist_ok=True)
        urllib.request.urlretrieve(URL, SRC)
    os.makedirs(OUT, exist_ok=True)
    unicodes = [u for a, b in RANGES for u in range(a, b + 1)]
    for name, wght in WEIGHTS.items():
        font = instancer.instantiateVariableFont(TTFont(SRC), {"wght": wght}, updateFontNames=True)
        opts = subset.Options()
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=unicodes)
        sub.subset(font)
        path = os.path.join(OUT, f"NotoSansKR-{name}.ttf")
        font.save(path)
        print(path, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main()
