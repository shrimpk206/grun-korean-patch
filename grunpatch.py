"""Grun.run 길드런 한글패치 (Windows, macOS).

게임의 '中文（繁体）'(번체 중국어) 언어 자리를 한국어로 바꾼다. 게임 파일 4개를 사용자의 PC에서 직접 고친다.
  1. 번체 중국어 문자열 번들: 영어 표의 구조(키·서식 정보)를 그대로 쓰고 글만 한국어로
  2. resources.assets: Noto Sans TC 글꼴 9종의 데이터를 Noto Sans KR 같은 굵기로
  3. global-metadata.dat: 언어 이름 '中文（繁体）' → '한국어'
  4. catalog.bin: 고친 번들의 크기와 CRC(0 = 검사 안 함)
원본은 데이터 폴더의 GrunKorean/backup 에 보관해서 '패치 제거'로 되돌릴 수 있다.
데이터 폴더: Windows 'Guildrun Demo/Guildrun_Data', macOS 'Guildrun Demo/Guildrun.app/Contents/Resources/Data'

개발용: python patch/grunpatch.py --out <폴더>  (게임은 건드리지 않고 고친 파일만 만든다)
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import UnityPy

VERSION = "1.1.1"
HERE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
FONTS = HERE / "fonts"
KO_FILE = HERE / "dist" / "ko-game.json" if (HERE / "dist" / "ko-game.json").exists() else HERE / "ko-game.json"
MAC = sys.platform == "darwin"

# 데이터 폴더 안의 경로. {aa} 는 번들 폴더(StandaloneWindows64 / StandaloneOSX)
TARGET = {
    "bundle": "StreamingAssets/aa/{aa}/localization-string-tables-chinese(traditional)(zh-hant)_assets_all.bundle",
    "resources": "resources.assets",
    "metadata": "il2cpp_data/Metadata/global-metadata.dat",
    "catalog": "StreamingAssets/aa/catalog.bin",
}
SOURCE = {  # 읽기만 한다
    "english": "StreamingAssets/aa/{aa}/localization-string-tables-english(en)_assets_all.bundle",
    "shared": "StreamingAssets/aa/{aa}/localization-assets-shared_assets_all.bundle",
}
LAYOUTS = [("Guildrun_Data", "StandaloneWindows64"), ("Guildrun.app/Contents/Resources/Data", "StandaloneOSX")]
STATE_DIR = "GrunKorean"
OLD_NAME = "中文（繁体）"
NEW_NAME = "한국어"
WEIGHTS = ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]


class PatchError(Exception):
    pass


class Game:
    """게임 폴더('Guildrun Demo')와 그 안의 데이터 폴더."""

    def __init__(self, root: Path):
        root = Path(root)
        if root.suffix == ".app":  # macOS에서 Guildrun.app 을 넘겨도 된다
            root = root.parent
        self.root = root
        for data, aa in LAYOUTS:
            if (root / data).is_dir():
                self.data, self.aa = root / data, aa
                break
        else:
            raise PatchError(f"Guildrun Demo 폴더가 아닙니다: {root}")

    def rel(self, key: str) -> str:
        return {**TARGET, **SOURCE}[key].format(aa=self.aa)

    def path(self, key: str) -> Path:
        return self.data / self.rel(key)

    @property
    def state_dir(self) -> Path:
        return self.data / STATE_DIR

    def backup(self, key: str, state: dict | None = None) -> Path:
        if state is not None and "layout" not in state:  # 1.0.0(Windows)은 게임 폴더 기준 경로로 백업했다
            return self.state_dir / "backup" / "Guildrun_Data" / self.rel(key)
        return self.state_dir / "backup" / self.rel(key)

    def check(self) -> None:
        missing = [self.rel(k) for k in list(TARGET) + list(SOURCE) if not self.path(k).exists()]
        if missing:
            raise PatchError("게임 파일이 없습니다:\n  " + "\n  ".join(missing))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ------------------------------------------------------------ 1. 문자열 번들
def table_name(tree: dict) -> str:
    return tree["m_Name"].rsplit("_", 1)[0]  # 'UI_en' → 'UI'


def string_tables(env) -> dict:
    out = {}
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            tree = obj.read_typetree()
            if "m_TableData" in tree:
                out[table_name(tree)] = (obj, tree)
    return out


def load(path: Path):
    return UnityPy.load(path.read_bytes())  # 파일을 열어 두면 Windows에서 덮어쓸 수 없다


def build_bundle(game: Game, ko: dict) -> tuple[bytes, dict]:
    keys = {}
    for obj in load(game.path("shared")).objects:
        if obj.type.name == "MonoBehaviour":
            tree = obj.read_typetree()
            if "m_Entries" in tree:
                keys[tree["m_TableCollectionName"]] = {e["m_Id"]: e["m_Key"] for e in tree["m_Entries"]}
    english = string_tables(load(game.path("english")))
    env = load(game.path("bundle"))
    target = string_tables(env)
    if set(target) != set(english):
        raise PatchError(f"문자열 표 구성이 다릅니다: {sorted(set(target) ^ set(english))}")
    done = total = 0
    for name, (obj, tree) in target.items():
        en_tree = english[name][1]
        table_keys = keys.get(name, {})
        rows = []
        for e in en_tree["m_TableData"]:
            text = ko.get(table_keys.get(e["m_Id"], ""))
            total += 1
            if text is not None:
                done += 1
            rows.append({"m_Id": e["m_Id"], "m_Localized": e["m_Localized"] if text is None else text,
                         "m_Metadata": copy.deepcopy(e["m_Metadata"])})
        tree["m_TableData"] = rows
        # 서식(SmartFormat) 정보는 표 전체 것까지 영어 표를 따른다 (참조 번호가 짝을 이뤄야 한다)
        tree["m_Metadata"] = copy.deepcopy(en_tree["m_Metadata"])
        tree["references"] = copy.deepcopy(en_tree["references"])
        obj.save_typetree(tree)
    return env.file.save(packer="lz4"), {"strings": total, "translated": done}


# ------------------------------------------------------------ 2. 글꼴
def build_resources(game: Game) -> tuple[bytes, dict]:
    env = load(game.path("resources"))
    replaced = []
    for obj in env.objects:
        if obj.type.name != "Font":
            continue
        font = obj.read()
        m = re.fullmatch(r"NotoSansTC-(\w+)", font.m_Name)
        if not m or m.group(1) not in WEIGHTS:
            continue
        data = (FONTS / f"NotoSansKR-{m.group(1)}.ttf").read_bytes()
        font.m_FontData = list(data)
        font.m_FontNames = ["Noto Sans KR"]
        font.save()
        replaced.append(m.group(1))
    if sorted(replaced) != sorted(WEIGHTS):
        raise PatchError(f"Noto Sans TC 글꼴을 다 찾지 못했습니다: {replaced}")
    return env.file.save(), {"fonts": len(replaced)}


# ------------------------------------------------------------ 3. 언어 이름
def build_metadata(game: Game) -> tuple[bytes, dict]:
    data = bytearray(game.path("metadata").read_bytes())
    sanity, version = struct.unpack_from("<Ii", data, 0)
    if sanity != 0xFAB11BAF:
        raise PatchError("global-metadata.dat 형식이 아닙니다")
    lit_off, lit_size, str_off, str_size = struct.unpack_from("<4i", data, 8)
    old, new = OLD_NAME.encode(), NEW_NAME.encode()
    hits = []
    for i in range(lit_size // 8):  # Il2CppStringLiteral { uint32 length; int32 dataIndex }
        length, index = struct.unpack_from("<Ii", data, lit_off + i * 8)
        if length == len(old) and data[str_off + index:str_off + index + length] == old:
            hits.append((i, index))
    if len(hits) != 1:
        raise PatchError(f"언어 이름 '{OLD_NAME}'을 찾지 못했습니다 ({len(hits)}개)")
    i, index = hits[0]
    data[str_off + index:str_off + index + len(new)] = new  # 남는 뒷부분은 쓰지 않는 바이트로 남는다
    struct.pack_into("<I", data, lit_off + i * 8, len(new))
    return bytes(data), {"metadata_version": version}


# ------------------------------------------------------------ 4. 번들 목록
def build_catalog(game: Game, old_size: int, new_size: int) -> tuple[bytes, dict]:
    """AssetBundleRequestOptions 기록 { hash, name, crc, size, common } 중 번체 번들 것을 찾아 CRC=0, 크기를 새 값으로."""
    data = bytearray(game.path("catalog").read_bytes())
    english_size = game.path("english").stat().st_size

    def records(size):
        out = []
        for m in re.finditer(re.escape(struct.pack("<I", size)), data):
            start = m.start() - 12
            if start >= 0:
                h, name, crc, s, common = struct.unpack_from("<5I", data, start)
                if s == size and max(h, name, common) < len(data):
                    out.append((start, common))
        return out

    ours, ref = records(old_size), records(english_size)
    if len(ref) != 1:
        raise PatchError("catalog.bin에서 영어 번들 기록을 찾지 못했습니다")
    ours = [r for r in ours if r[1] == ref[0][1]]  # 영어 번들과 같은 설정(common)을 쓰는 기록
    if len(ours) != 1 or b"(zh-hant)_assets_all" not in data:
        raise PatchError("catalog.bin에서 번체 중국어 번들 기록을 찾지 못했습니다")
    struct.pack_into("<II", data, ours[0][0] + 8, 0, new_size)
    return bytes(data), {}


# ------------------------------------------------------------ 설치·제거
def game_running() -> bool:
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Guildrun.exe", "/NH"],
                             capture_output=True, text=True, creationflags=0x08000000).stdout
        return "Guildrun.exe" in out
    return subprocess.run(["pgrep", "-x", "Guildrun"], capture_output=True).returncode == 0


def load_state(game: Game) -> dict | None:
    p = game.state_dir / "state.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save_state(game: Game, state: dict) -> None:
    (game.state_dir / "state.json").write_text(json.dumps(state, indent=1), encoding="utf-8")


def restore(game: Game, state: dict) -> None:
    """백업해 둔 원본을 제자리로. 백업이 상했으면 멈춘다.
    지금 파일이 우리가 고친 그대로일 때만 되돌린다. 게임 업데이트(또는 무결성 검사)로 바뀐 파일은 이미 새 원본이라
    옛 백업을 덮으면 게임이 깨진다(예: 0.5.11 global-metadata.dat + 0.5.12 GameAssembly.dll)."""
    keys = [k for k in TARGET if sha256(game.path(k)) == state["patched"].get(k)]
    for key in keys:
        if sha256(game.backup(key, state)) != state["original"][key]:
            raise PatchError(f"백업 파일이 손상되었습니다: {game.rel(key)}\nSteam에서 '게임 파일 무결성 검사'를 해 주세요.")
    for key in keys:
        tmp = game.path(key).with_name(game.path(key).name + ".grun-tmp")
        shutil.copy2(game.backup(key, state), tmp)
        os.replace(tmp, game.path(key))


def build_all(game: Game, ko: dict, log=print) -> tuple[dict, dict]:
    """원본 4개를 읽어 고친 내용을 {키: bytes}로. 게임 폴더는 건드리지 않는다."""
    out, report = {}, {}
    log("  문자열 번들을 만드는 중…")
    old_size = game.path("bundle").stat().st_size
    out["bundle"], r = build_bundle(game, ko); report.update(r)
    log("  글꼴을 바꾸는 중… (1분 정도 걸립니다)")
    out["resources"], r = build_resources(game); report.update(r)
    log("  언어 이름과 번들 목록을 고치는 중…")
    out["metadata"], r = build_metadata(game); report.update(r)
    out["catalog"], r = build_catalog(game, old_size, len(out["bundle"])); report.update(r)
    return out, report


def install(game: Game, ko: dict, log=print) -> dict:
    tmps = [game.path(k).with_name(game.path(k).name + ".grun-tmp") for k in TARGET]
    for tmp in tmps:  # 지난번에 중간에 끊겼으면 남은 임시 파일
        tmp.unlink(missing_ok=True)
    state = load_state(game)
    if state:  # 이미 깔려 있으면 원본으로 되돌린 뒤 다시 만든다
        log("  이전에 설치한 패치를 원본으로 되돌리는 중…")
        restore(game, state)
        if "layout" not in state:  # 1.0.0 백업은 새 경로로 옮긴다
            shutil.rmtree(game.state_dir)
    original = {key: sha256(game.path(key)) for key in TARGET}
    files, report = build_all(game, ko, log)
    log("  원본을 백업하고 파일을 바꾸는 중…")
    for key in TARGET:
        dst = game.backup(key)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not (dst.exists() and sha256(dst) == original[key]):
            shutil.copy2(game.path(key), dst)
    state = {"version": VERSION, "layout": 2, "original": original, "patched": {}}
    save_state(game, state)
    try:
        for key, tmp in zip(TARGET, tmps):
            tmp.write_bytes(files[key])
            os.replace(tmp, game.path(key))
            state["patched"][key] = hashlib.sha256(files[key]).hexdigest()
    except Exception:  # 하나라도 실패하면 전부 원본으로
        for tmp in tmps:
            tmp.unlink(missing_ok=True)
        restore(game, state)
        raise
    save_state(game, state)
    return report


def uninstall(game: Game) -> bool:
    state = load_state(game)
    if not state:
        return False
    restore(game, state)
    shutil.rmtree(game.state_dir)
    return True


# ------------------------------------------------------------ 게임 폴더 찾기
def steam_libraries() -> list[Path]:
    roots = []
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                roots.append(Path(winreg.QueryValueEx(k, "SteamPath")[0]))
        except OSError:
            pass
        roots.append(Path(r"C:\Program Files (x86)\Steam"))
    else:
        roots.append(Path.home() / "Library" / "Application Support" / "Steam")
    libs = []
    for root in roots:
        vdf = root / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            libs += [Path(p.replace("\\\\", "\\")) for p in re.findall(r'"path"\s+"([^"]+)"', vdf.read_text(encoding="utf-8", errors="replace"))]
        libs.append(root)
    seen, out = set(), []
    for lib in libs:
        if str(lib).lower() not in seen:
            seen.add(str(lib).lower()); out.append(lib)
    return out


def find_game() -> Game | None:
    for lib in steam_libraries():
        try:
            return Game(lib / "steamapps" / "common" / "Guildrun Demo")
        except PatchError:
            continue
    return None


def load_ko() -> dict:
    return json.loads(KO_FILE.read_text(encoding="utf-8"))


# ------------------------------------------------------------ 콘솔 화면
def ask(prompt: str, choices: str) -> str:
    while True:
        answer = input(prompt).strip()
        if answer in choices:
            return answer


def console() -> int:
    print(f"Grun.run 길드런 한글패치 {VERSION}  (https://www.grun.run)")
    print("게임의 '번체 중국어' 언어 자리를 한국어로 바꿉니다. 설치 뒤 게임 설정에서 언어를 '한국어'로 고르세요.\n")
    try:
        game = find_game()
        if game:
            print(f"게임 폴더: {game.root}")
        else:
            where = "Guildrun Demo 폴더(또는 Guildrun.app)를 이 창에 끌어다 놓거나 경로를" if MAC else "Guildrun.exe가 있는 폴더 경로를"
            while True:
                path = input(f"게임 폴더를 찾지 못했습니다. {where} 붙여 넣고 Enter: ").strip().strip('"').strip("'")
                try:
                    game = Game(Path(path.replace("\\ ", " ")))
                    break
                except PatchError as e:
                    print(e)
        game.check()
        installed = load_state(game)
        print("상태: " + ("한글패치 설치됨" if installed else "설치 안 됨") + "\n")
        choice = ask("1) 설치(또는 다시 설치)  2) 패치 제거  3) 끝내기 : ", "123")
        if choice == "3":
            return 0
        while game_running():
            input("\n게임이 실행 중입니다. 게임을 끈 뒤 Enter를 누르세요.")
        if choice == "2":
            print("\n원본으로 되돌리는 중…")
            print("패치를 제거했습니다." if uninstall(game) else "이 패처로 설치한 기록이 없습니다. Steam '게임 파일 무결성 검사'로 되돌릴 수 있습니다.")
        else:
            print("\n설치하는 중…")
            report = install(game, load_ko())
            print(f"\n설치했습니다. 번역 {report['translated']}/{report['strings']}개.")
            print("게임 설정 > 언어에서 '한국어'를 고르세요. 게임이 업데이트되면 패처를 다시 실행하세요.")
    except PatchError as e:
        print(f"\n실패: {e}")
        return 1
    except Exception as e:  # 예상 못 한 오류도 창이 바로 닫히지 않게
        print(f"\n실패: {type(e).__name__}: {e}")
        return 1
    finally:
        if getattr(sys, "frozen", False) and not MAC:  # macOS는 터미널 창이 그대로 남는다
            input("\nEnter를 누르면 닫힙니다.")
    return 0


def main() -> int:
    if os.name == "nt":
        try:  # 한국어 Windows 콘솔(cp949)에서도 글자가 깨지지 않게
            sys.stdout.reconfigure(encoding="utf-8")
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Grun.run 길드런 한글패치")
    ap.add_argument("--game", type=Path, help="게임 폴더 (기본: Steam에서 찾기)")
    ap.add_argument("--out", type=Path, help="게임을 건드리지 않고 고친 파일만 이 폴더에 만든다")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="번역·글꼴이 들어 있는지만 확인 (빌드 점검용)")
    args = ap.parse_args()
    if args.selftest:
        fonts = [w for w in WEIGHTS if (FONTS / f"NotoSansKR-{w}.ttf").stat().st_size > 1_000_000]
        ko = load_ko()
        print(f"Grun.run 한글패치 {VERSION}: 번역 {len(ko)}개, 글꼴 {len(fonts)}/9, UnityPy {UnityPy.__version__}")
        return 0 if len(fonts) == 9 and len(ko) > 3000 else 1
    if not (args.out or args.install or args.uninstall):
        return console()
    game = Game(args.game) if args.game else find_game()
    if not game:
        raise SystemExit("게임 폴더를 찾지 못했습니다 (--game)")
    game.check()
    if args.uninstall:
        print("제거함" if uninstall(game) else "설치 기록 없음")
    elif args.install:
        print(install(game, load_ko()))
    else:
        files, report = build_all(game, load_ko())
        for key in TARGET:
            dst = args.out / game.rel(key)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(files[key])
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
