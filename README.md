# Vertex AI Gemini API を利用したサンプルアプリケーション
## はじめに
このリポジトリは Vertex AI の Gemini API を利用し、Cloud Run 上で動作する Python アプリケーション、および、そのロジックのベースとなる Notebook のサンプルを提供します。以下の 3 パターンにおける Gemini を利用した RAG 実装の違いを確認頂けます。
 - Gemini に PDF ファイルを直接連携
 - Vertex AI Search を利用したグラウンディング
 - Google Search を利用したグラウンディング


## ローカルでの実行
ローカルで実行する場合は、Google Cloud の `Vertex AI ユーザー`、`ディスカバリー エンジン閲覧者` 権限を保持するサービスアカウントキーを作成し、キーファイルを保存しておきます。

環境変数に以下の値を設定してください。
```shell
export GOOGLE_APPLICATION_CREDENTIALS="KEY_PATH"
```
```shell
export PROJECT_ID=<your_project_id>
export DATA_STORE_ID=<datastore_id>
```

Cloud Workstations で動かす場合は venv のインストールも併せて行います。
```shell
sudo apt update
sudo apt install python3.12-venv
```
以下のコマンドで Streamlit アプリケーションを起動します。
```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
```

## Cloud Run での実行

Cloud Console の Cloud Run のサービス作成 UI を利用する場合、
- ソースリポジトリからビルドタイプ Docker ファイルでビルド
- 認証に未認証の呼び出しを許可
- セキュリティのサービスアカウントに、`Vertex AI ユーザー`、`ディスカバリー エンジン閲覧者` 権限を保持するサービスアカウントを指定
- 環境変数 PROJECT_ID=<your_project_id>
- 環境変数 DATA_STORE_ID=<datastore_id>

を各自の環境用に指定すれば自動でデプロイ、動作します。

コマンドの場合は、以下を利用します。
```shell
gcloud run deploy gemini2apps \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --service-account=<your-service-account-email> \
  --set-env-vars PROJECT_ID=<your_project_id>,DATA_STORE_ID=<datastore_id> \
  --project=<your_project_id>
```

