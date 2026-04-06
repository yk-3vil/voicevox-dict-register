# CLAUDE.md

## プロジェクト概要

VOICEVOX Engine ユーザー辞書一括登録ツール。
YAMLファイルに定義したIT技術用語の読みを、REST API経由でVOICEVOX Engineに登録する。

## 技術スタック

- Python 3 + PyYAML
- Nix Flakes（環境管理）

## 実行方法

```bash
# dry-run
nix run . -- --dry-run

# 登録
nix run . -- -f dict.yaml

# 重複削除してから登録
nix run . -- --cleanup -f dict.yaml
```

## 注意事項

- VOICEVOX Engine接続先は `127.0.0.1:50021`（`localhost` はIPv6解決されPodman passt経由で接続失敗する）
- VOICEVOX Engineはsurfaceを全角に正規化する（`vim` → `ｖｉｍ`）。スクリプト側でNFKC正規化して一致判定済み
- `--cleanup` で重複エントリを削除可能（各surfaceにつき1件だけ残す）

## 辞書カテゴリ（164件）

- エディタ・シェル、コマンド・ツール、コンテナ・インフラ
- 言語・ランタイム、フレームワーク・ライブラリ、データベース
- クラウド・サービス、プロトコル・略語、OS・ディストリビューション
- AI・機械学習、拡張子・ファイル形式
