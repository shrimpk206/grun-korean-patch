#!/bin/bash
# Grun.run 길드런 한글패치 macOS 설치 도우미
# 터미널에 붙여 넣기: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/shrimpk206/grun-korean-patch/main/install-macos.sh)"
# 최신 릴리스에서 이 Mac에 맞는 패처(Apple 실리콘/인텔)를 임시 폴더에 받아 실행하고, 끝나면 지운다.
set -euo pipefail

REPO="shrimpk206/grun-korean-patch"
case "$(uname -m)" in
  arm64) ARCH=arm64 ;;
  x86_64) ARCH=x64 ;;
  *) echo "지원하지 않는 Mac입니다: $(uname -m)"; exit 1 ;;
esac

# releases/latest 가 넘겨주는 주소(…/tag/v1.2.3)에서 최신 버전을 읽는다
TAG=$(curl -fsSLI -o /dev/null -w '%{url_effective}' "https://github.com/$REPO/releases/latest")
TAG=${TAG##*/}
VERSION=${TAG#v}
URL="https://github.com/$REPO/releases/download/$TAG/GrunKoreanPatch-$VERSION-macos-$ARCH.zip"

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
echo "Grun.run 한글패치 $VERSION ($ARCH) 받는 중…"
curl -fL --progress-bar -o "$WORK/patch.zip" "$URL"
/usr/bin/ditto -x -k "$WORK/patch.zip" "$WORK"
chmod +x "$WORK/GrunKoreanPatch"
"$WORK/GrunKoreanPatch" </dev/tty
