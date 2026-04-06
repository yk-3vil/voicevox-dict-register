# voicevox-dict

VOICEVOX Engine のユーザー辞書を一括登録するツールです。YAML ファイルに読み方を定義し、REST API 経由でまとめて登録します。新規追加・既存更新・dry-run プレビューに対応しています。

## インストール

1. [Nix](https://nixos.org/)（flakes 有効）をインストールしてください。
2. リポジトリをクローンします:
   ```bash
   git clone <repository-url>
   cd voicevox-dict
   ```

## 使い方

1. `dict.yaml` に単語を定義します:
   ```yaml
   words:
     - surface: vimrc
       pronunciation: ヴィムアールシー
       accent_type: 3
     - surface: nginx
       pronunciation: エンジンエックス
       accent_type: 5
       word_type: PROPER_NOUN
       priority: 8
   ```

2. 登録せずにプレビューします:
   ```bash
   nix run . -- --dry-run
   ```

3. VOICEVOX Engine に登録します:
   ```bash
   nix run . -- -f dict.yaml
   ```

4. 利用可能なオプション:
   ```
   -f, --file FILE    辞書 YAML ファイル (デフォルト: dict.yaml)
   --url URL          VOICEVOX Engine URL (デフォルト: http://127.0.0.1:50021)
   --dry-run          登録せずプレビューのみ
   ```

### YAML スキーマ

| フィールド       | 必須 | デフォルト     | 説明                                                  |
|-----------------|------|--------------|------------------------------------------------------|
| `surface`       | Yes  | -            | 登録する単語（表層形）                                   |
| `pronunciation` | Yes  | -            | カタカナ読み                                            |
| `accent_type`   | No   | `1`          | アクセント核の位置（0 = 平板、1以上 = その位置に核）         |
| `word_type`     | No   | `PROPER_NOUN`| `PROPER_NOUN` / `COMMON_NOUN` / `VERB` / `ADJECTIVE` / `SUFFIX` |
| `priority`      | No   | `5`          | 優先度 0-10（高いほど優先）                               |

## 開発

- 必要な環境: Nix（flakes 対応）、VOICEVOX Engine が localhost で起動していること
- 開発シェルに入る: `nix develop`
- 直接実行: `python3 main.py --dry-run`

## アーキテクチャ

- システム概要:

  ```mermaid
  graph TB
      YAML[dict.yaml]
      SCRIPT[main.py]
      API[VOICEVOX Engine API<br/>localhost:50021]
      DICT[(User Dictionary)]
      YAML --> SCRIPT
      SCRIPT -->|GET /user_dict| API
      SCRIPT -->|POST /user_dict_word| API
      SCRIPT -->|PUT /user_dict_word/uuid| API
      API --> DICT
  ```

- データフロー:

  ```mermaid
  flowchart LR
      A[YAML ファイル] --> B[読み込み・解析]
      B --> C[登録済み単語を取得]
      C --> D{登録済み?}
      D -->|Yes| E[PUT 更新]
      D -->|No| F[POST 登録]
      E --> G[結果サマリー]
      F --> G
  ```

## ライセンス

MIT License。詳細は [LICENSE](LICENSE) を参照してください。
