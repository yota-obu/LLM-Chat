from flask import Flask, request, jsonify, render_template
import os
from datetime import datetime
import psycopg2
# from langchain.memory.chat_message_histories import PostgresChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv


app = Flask(__name__)

# 環境変数からAPIキー設定
load_dotenv()

# DB接続


def get_db_connection():
    return psycopg2.connect("postgresql://myuser:mypassword@db:5432/mychatdb")


# LangChain設定
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_retries=5
)

prompt_profile = PromptTemplate.from_template("""
    #**Role**
    以下の簡素なプロフィールを想像で膨らませて、より具体的にして。
    全て架空で埋めること。
    出力はプロフィールのみ。                                
    ##プロフィール
    {pre_profile}
""")

prompt = PromptTemplate.from_template("""
    #**Role**
    あなたは以下のプロフィールになりきってqueryに対して返事をしてください。
    返事は簡素にすること。改行禁止。敬語禁止。友達のように。
    ##プロフィール
    {profile}
    #query
    {query}
""")


@app.route("/")
def index():
    return render_template("index.html")  # HTMLファイルをテンプレートとしてレンダリング


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        session_id = data.get("session_id", "default_session")
        user_id = data.get("user_id", "anonymous")
        query = data["query"]

        # プロフィール作成
        pre_profile = data["pre_profile"]  # クライアントから受け取る
        profile_chain = prompt_profile | model | StrOutputParser()
        profile = profile_chain.invoke({"pre_profile": pre_profile})

        # 応答生成
        chat_chain = prompt | model | StrOutputParser()
        answer = chat_chain.invoke({"query": query, "profile": profile})

        # DB保存
        conn = get_db_connection()
        cursor = conn.cursor()

        def get_next_message_id(session_id):
            cursor.execute(
                "SELECT COALESCE(MAX(message_id), 0) + 1 FROM message_store WHERE session_id = %s", (session_id,))
            return cursor.fetchone()[0]

        def save_message(role, text):
            message_id = get_next_message_id(session_id)
            cursor.execute("""
                INSERT INTO message_store (
                    user_id, session_id, message_id,
                    parent_message_id, message_role, message_text, received_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, session_id, message_id, None, role, text, datetime.now()))
            conn.commit()

        save_message("user", query)
        save_message("system", answer)

        cursor.close()
        conn.close()

        return jsonify({"profile": profile, "response": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Cloud Run用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
