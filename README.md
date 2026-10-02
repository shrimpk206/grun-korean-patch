# Grun.run 길드런 한글패치

Steam **Guildrun Demo**를 한국어로 플레이할 수 있게 해 주는 비공식 한글패치입니다.
[Grun.run - 길드런 커뮤니티](https://www.grun.run)에서 만들었고, 게임 화면의 영웅·아이템·유물 이름과 용어가 사이트와 같습니다.

## 내려받기

[최신 릴리스](https://github.com/shrimpk206/grun-korean-patch/releases/latest)에서 운영체제에 맞는 파일을 받습니다. 설치 안내는 [grun.run/patch](https://www.grun.run/patch)에도 있습니다.

| 파일 | 대상 |
|---|---|
| `GrunKoreanPatch-<버전>-windows.zip` | Windows |
| `GrunKoreanPatch-<버전>-macos-arm64.zip` | Mac (Apple 실리콘: M1 이후) |
| `GrunKoreanPatch-<버전>-macos-x64.zip` | Mac (인텔) |

## 설치 (Windows)

1. 게임을 끕니다.
2. 압축을 풀고 `GrunKoreanPatch.exe`를 실행해 **1번(설치)** 을 고릅니다. Steam 라이브러리에서 게임 폴더를 자동으로 찾습니다.
3. 게임 **설정 > 언어**에서 **한국어**를 고릅니다.

Windows가 "PC 보호" 창을 띄우면 '추가 정보 → 실행'을 누릅니다. 서명하지 않은 개인 제작 프로그램이라 나오는 안내입니다.

## 설치 (macOS, 시험판)

게임을 끄고 터미널(응용 프로그램 > 유틸리티 > 터미널)에 아래 한 줄을 붙여 넣습니다. 이 Mac에 맞는 패처를 받아 실행하고, 끝나면 내려받은 파일을 지웁니다([`install-macos.sh`](install-macos.sh)).

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/shrimpk206/grun-korean-patch/main/install-macos.sh)"
```

압축 파일을 직접 받았다면 `GrunKoreanPatch.command`를 더블클릭합니다. "확인되지 않은 개발자" 창이 뜨면 시스템 설정 > 개인정보 보호 및 보안에서 '그래도 열기'를 누릅니다.
macOS판은 Windows판과 같은 코드지만, 아직 실제 Mac의 게임에서 확인하지 못했습니다. 문제가 있으면 [Issues](https://github.com/shrimpk206/grun-korean-patch/issues)에 알려 주세요.

## 제거 · 게임 업데이트

- 제거: 패처를 다시 실행해 **2번(패치 제거)**, 또는 Steam에서 '게임 파일 무결성 검사'.
- 게임이 업데이트되면 패처를 다시 실행합니다. 새로 생긴 문장은 다음 패치 전까지 영어로 나옵니다.

## 패처가 하는 일

게임 파일을 내려받거나 배포하지 않고, 사용자 PC에 있는 원본 4개를 고칩니다. 원본은 게임 데이터 폴더(Windows `Guildrun_Data`, macOS `Guildrun.app/Contents/Resources/Data`)의 `GrunKorean/backup`에 보관합니다.

| 파일 | 바꾸는 내용 |
|---|---|
| `localization-string-tables-chinese(traditional)(zh-hant)_assets_all.bundle` | 번체 중국어 문자열 표를 한국어로 (영어 표의 키·서식 구조를 그대로 사용) |
| `resources.assets` | Noto Sans TC 글꼴 9종 → Noto Sans KR 같은 굵기 |
| `global-metadata.dat` | 언어 메뉴의 이름 `中文（繁体）` → `한국어` |
| `catalog.bin` | 고친 번들의 크기, CRC 검사 끄기 |

게임의 '번체 중국어' 자리를 쓰므로 패치 중에는 번체 중국어를 고를 수 없습니다.
코드는 [`grunpatch.py`](grunpatch.py) 하나입니다(Python 3.12, UnityPy). 배포 파일은 PyInstaller로 묶은 것이고, macOS판은 [GitHub Actions](.github/workflows/macos.yml)에서 만듭니다.

## 번역

- 게임 문장 3,923개 전부를 영어 원문에서 직접 번역했습니다.
- 번역 데이터: [`ko-game.json`](ko-game.json) — 게임의 문자열 키(예: `Heroes.Hero_1.Name`) → 한국어. 패처는 이 파일을 그대로 넣습니다.
- 번역 규칙과 용어표: [`TRANSLATING.md`](TRANSLATING.md). `{0}`, `[텍스트]<태그>` 같은 자리 표시는 글자 하나 바꾸면 게임에서 깨집니다.
- 오역이나 어색한 문장은 [Issues](https://github.com/shrimpk206/grun-korean-patch/issues)나 [grun.run 커뮤니티](https://www.grun.run/community)에 알려 주세요.

## 소스에서 직접 실행

Python 3.12에서:

```bash
pip install UnityPy==1.25.3 fonttools
python make_fonts.py   # work/fontsrc/NotoSansKR[wght].ttf (google/fonts) → fonts/NotoSansKR-*.ttf
python grunpatch.py    # 설치·제거 메뉴. --out <폴더> 를 주면 게임은 그대로 두고 고친 파일만 만든다
```

## 글꼴

[Noto Sans KR](https://github.com/google/fonts/tree/main/ofl/notosanskr)을 게임 굵기 9종으로 고정하고 한글·영문·기호만 남겨 넣었습니다([`make_fonts.py`](make_fonts.py)).
SIL Open Font License 1.1을 따릅니다([`fonts/OFL.txt`](fonts/OFL.txt)).

## 알림

비공식 팬 패치입니다. 사용에 따른 문제는 사용자 책임입니다. Guildrun과 게임의 글·그림에 대한 권리는 Leyline에 있습니다.
