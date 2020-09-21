# voice2text

Cloud Speech APIでWAVファイルから文字起こししてStorageにファイルを保存する

## 環境・周辺ツール

- Python 3.8
- Direnv

## 事前準備

### パッケージインストール

```
$ pipenv shell && \
pipenv install
```

### GCP側の設定

1. プロジェクト作成
2. [gcloud コマンドインストール](https://cloud.google.com/sdk/docs?hl=ja)
3. [ストレージバケットを作成](https://cloud.google.com/storage/docs/creating-buckets?hl=ja)
    * 音声ファイルアップロード用
    * 文字起こし後のファイルアップロード用

### (テスト用) 環境変数に設定

```
$ cp .envrc.sample .envrc
```

### (テスト) スクリプトを一部書き換え
音声ファイルアップロード用のバケットに音声ファイルをアップロード


スクリプトファイル(main.py)一部調整

```
def voice2text(event, context):
    """
    main handler
    """
    source_file_name = event['name']

↓
if __name__ == "__main__":
    source_file_name = '音声ファイル名'
```

```
$ python main.py
```

### Cloud Functions へスクリプトのデプロイ

```
$ sh bin/deploy-functions.sh
```
