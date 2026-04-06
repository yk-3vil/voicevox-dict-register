# voicevox-dict

A batch registration tool for VOICEVOX Engine's user dictionary. Define pronunciation rules in a YAML file and register them all at once via the REST API. Supports adding new words, updating existing entries, and dry-run previews.

## Installation

1. Ensure [Nix](https://nixos.org/) (with flakes enabled) is installed.
2. Clone this repository:
   ```bash
   git clone <repository-url>
   cd voicevox-dict
   ```

## Usage

1. Define words in `dict.yaml`:
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

2. Preview without registering:
   ```bash
   nix run . -- --dry-run
   ```

3. Register to VOICEVOX Engine:
   ```bash
   nix run . -- -f dict.yaml
   ```

4. Available options:
   ```
   -f, --file FILE    Dictionary YAML file (default: dict.yaml)
   --url URL          VOICEVOX Engine URL (default: http://127.0.0.1:50021)
   --dry-run          Preview only, do not register
   ```

### YAML Schema

| Field           | Required | Default      | Description                                          |
|-----------------|----------|--------------|------------------------------------------------------|
| `surface`       | Yes      | -            | Word to register (surface form)                      |
| `pronunciation` | Yes      | -            | Katakana reading                                     |
| `accent_type`   | No       | `1`          | Accent nucleus position (0 = flat, 1+ = position)    |
| `word_type`     | No       | `PROPER_NOUN`| `PROPER_NOUN` / `COMMON_NOUN` / `VERB` / `ADJECTIVE` / `SUFFIX` |
| `priority`      | No       | `5`          | Priority 0-10 (higher = stronger)                    |

## Development

- Required environment: Nix (with flakes), VOICEVOX Engine running on localhost
- Enter development shell: `nix develop`
- Run directly: `python3 register.py --dry-run`

## Architecture

- System overview:

  ```mermaid
  graph TB
      YAML[dict.yaml]
      SCRIPT[register.py]
      API[VOICEVOX Engine API<br/>localhost:50021]
      DICT[(User Dictionary)]
      YAML --> SCRIPT
      SCRIPT -->|GET /user_dict| API
      SCRIPT -->|POST /user_dict_word| API
      SCRIPT -->|PUT /user_dict_word/uuid| API
      API --> DICT
  ```

- Data flow:

  ```mermaid
  flowchart LR
      A[YAML file] --> B[Load & parse]
      B --> C[Fetch registered words]
      C --> D{Already exists?}
      D -->|Yes| E[PUT update]
      D -->|No| F[POST register]
      E --> G[Result summary]
      F --> G
  ```

## License

MIT License. See [LICENSE](LICENSE) for details.
