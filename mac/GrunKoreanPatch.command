#!/bin/bash
# 더블클릭하면 터미널에서 패처를 실행한다. (압축을 푼 폴더 안에 GrunKoreanPatch 와 같이 둘 것)
cd "$(dirname "$0")"
xattr -d com.apple.quarantine ./GrunKoreanPatch 2>/dev/null || true
chmod +x ./GrunKoreanPatch
./GrunKoreanPatch
echo
read -n 1 -s -r -p "아무 키나 누르면 닫힙니다."
