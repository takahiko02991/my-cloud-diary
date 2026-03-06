# my-cloud-diary
# 📝 My Cloud Diary

自分専用のクラウド型日記アプリです。
場所を選ばず、PCやスマートフォンからいつでも日常の出来事を記録し、クラウド上で安全に管理できます。

## 🚀 概要
このプロジェクトは、PythonとStreamlitを使用して作成されたWebアプリケーションです。
バックエンドにSupabase（PostgreSQL）を採用しており、投稿した内容はリアルタイムでデータベースに保存・同期されます。

## ✨ 主な機能
- **クラウド投稿**: テキストを入力してボタンを押すだけで即座にクラウド保存。
- **レスポンシブデザイン**: PC、スマホの両方に最適化されたカード形式のUI。
- **削除機能**: 不要になった投稿をアプリ上から簡単に削除。
- **マルチデバイス対応**: Streamlit Cloudにデプロイ済みのため、URL一つでどこからでもアクセス可能。

## 🛠 使用技術（Tech Stack）
- **Language**: Python 3.13
- **Frontend**: Streamlit
- **Backend/Database**: Supabase (PostgreSQL)
- **Deployment**: Streamlit Cloud
- **Version Control**: GitHub

## 📦 セットアップ（ローカル実行用）
```bash
# リポジトリをクローン
git clone [https://github.com/あなたのユーザー名/my-cloud-diary.git](https://github.com/あなたのユーザー名/my-cloud-diary.git)

# 必要なライブラリをインストール
pip install -r requirements.txt

# アプリを起動
streamlit run app.py
