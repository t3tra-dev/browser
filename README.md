# simple-browser

Python と Qt6 を使ったシンプルなブラウザです。

## Usage

パッケージ管理に `uv` を使っているので以下の方法で実行できます。

1. 依存関係を同期
```bash
uv sync
```

2. 仮想環境の起動
```bash
source .venv/bin/activate  # Linux/macOS

.venv\Scripts\activate  # Windows
```

3. アプリケーションの起動
```bash
python main.py
```

## Features

- タブ機能
- 開発者ツール
- ショートカットキー
  - Ctrl+T: 新しいタブを開く
  - Ctrl+W: タブを閉じる
  - Ctrl+Q: アプリケーションを終了
  - F12: 開発者ツールを開く
  - Ctrl+Shift+D: 開発者ツールをポップアップ
- スタイルシートのホットリロード (アプリケーションの実行中に`./styles.qss`を編集すると動的に反映されます)

## Dependencies

- Python 3.8+
- PySide6

## License

MIT License
