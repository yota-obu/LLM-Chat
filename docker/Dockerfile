# Python 3.12 のベースイメージを使用
FROM python:3.12

# 作業ディレクトリを /workspace/app に設定
WORKDIR /workspace/app

# 必要なファイル（requirements.txt）をコンテナにコピー
COPY ./app/requirements.txt .

# pipをアップグレードし、requirements.txtに記載された依存関係をインストール
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# アプリケーションのコードをコンテナにコピー
COPY ./app /workspace/app

# コンテナが起動する際に Flask アプリケーションを実行
CMD ["python", "main.py"]

# コンテナがリッスンするポートを指定
EXPOSE 8080


