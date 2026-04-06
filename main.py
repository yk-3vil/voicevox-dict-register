#!/usr/bin/env python3
"""VOICEVOX Engine ユーザー辞書一括登録スクリプト."""

import argparse
import json
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

DEFAULT_DICT_FILE = Path.cwd() / "dict.yaml"
DEFAULT_BASE_URL = "http://127.0.0.1:50021"


def load_dict_yaml(path: Path) -> list[dict]:
    """YAML辞書ファイルを読み込み、単語リストを返す."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    words = data.get("words")
    if not words:
        print("辞書ファイルに words が定義されていません", file=sys.stderr)
        sys.exit(1)
    return words


def normalize_surface(surface: str) -> str:
    """VOICEVOX Engineの正規化に合わせ、NFKC正規化して小文字にする."""
    return unicodedata.normalize("NFKC", surface).lower()


def get_registered_words(base_url: str) -> dict[str, list[str]]:
    """登録済み辞書を取得し、正規化済みsurface -> UUIDリストのマッピングを返す."""
    url = f"{base_url}/user_dict"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    result: dict[str, list[str]] = {}
    for uuid, entry in data.items():
        key = normalize_surface(entry["surface"])
        result.setdefault(key, []).append(uuid)
    return result


def build_query(word: dict) -> str:
    """単語定義からURLクエリパラメータを構築する."""
    params = {
        "surface": word["surface"],
        "pronunciation": word["pronunciation"],
        "accent_type": word.get("accent_type", 1),
    }
    if "word_type" in word:
        params["word_type"] = word["word_type"]
    if "priority" in word:
        params["priority"] = word["priority"]
    return urllib.parse.urlencode(params)


def register_word(base_url: str, word: dict) -> str:
    """新規単語を登録し、UUIDを返す."""
    query = build_query(word)
    url = f"{base_url}/user_dict_word?{query}"
    req = urllib.request.Request(url, method="POST", data=b"")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def update_word(base_url: str, uuid: str, word: dict) -> None:
    """既存単語を更新する."""
    query = build_query(word)
    url = f"{base_url}/user_dict_word/{uuid}?{query}"
    req = urllib.request.Request(url, method="PUT", data=b"")
    with urllib.request.urlopen(req) as resp:
        resp.read()


def delete_word(base_url: str, uuid: str) -> None:
    """単語を削除する."""
    url = f"{base_url}/user_dict_word/{uuid}"
    req = urllib.request.Request(url, method="DELETE")
    with urllib.request.urlopen(req) as resp:
        resp.read()


def cleanup_duplicates(base_url: str) -> int:
    """重複エントリを削除し、各surfaceにつき1件だけ残す."""
    registered = get_registered_words(base_url)
    deleted = 0
    for surface, uuids in registered.items():
        if len(uuids) <= 1:
            continue
        for uuid in uuids[1:]:
            delete_word(base_url, uuid)
            deleted += 1
        print(f"  重複削除: {surface} ({len(uuids) - 1} 件)")
    return deleted


def main() -> None:
    parser = argparse.ArgumentParser(description="VOICEVOX ユーザー辞書一括登録")
    parser.add_argument(
        "-f", "--file",
        type=Path,
        default=DEFAULT_DICT_FILE,
        help=f"辞書YAMLファイル (default: {DEFAULT_DICT_FILE.name})",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_BASE_URL,
        help=f"VOICEVOX Engine URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際には登録せず、内容を表示するのみ",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="重複エントリを削除してから登録する",
    )
    args = parser.parse_args()

    words = load_dict_yaml(args.file)
    print(f"辞書ファイル: {args.file} ({len(words)} 件)")

    if args.dry_run:
        for w in words:
            print(f"  {w['surface']} → {w['pronunciation']} (accent: {w.get('accent_type', 1)})")
        print("(dry-run: 登録は行いません)")
        return

    try:
        registered = get_registered_words(args.url)
    except urllib.error.URLError as e:
        print(f"VOICEVOX Engine に接続できません ({args.url}): {e}", file=sys.stderr)
        sys.exit(1)

    if args.cleanup:
        deleted = cleanup_duplicates(args.url)
        if deleted:
            print(f"重複削除: 計 {deleted} 件")
            registered = get_registered_words(args.url)

    added = 0
    updated = 0
    skipped = 0

    for w in words:
        surface = w["surface"]
        key = normalize_surface(surface)
        existing_uuids = registered.get(key)

        try:
            if existing_uuids:
                update_word(args.url, existing_uuids[0], w)
                print(f"  更新: {surface} → {w['pronunciation']}")
                updated += 1
            else:
                uuid = register_word(args.url, w)
                print(f"  登録: {surface} → {w['pronunciation']} ({uuid})")
                added += 1
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"  失敗: {surface} - {e.code} {body}", file=sys.stderr)
            skipped += 1

    print(f"\n完了: 登録 {added} 件, 更新 {updated} 件, 失敗 {skipped} 件")


if __name__ == "__main__":
    main()
