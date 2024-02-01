import streamlit as st
import io

# アプリのタイトル
st.title('テキスト処理アプリ')

# テキスト入力エリア
user_input = st.text_area("ここにテキストを入力してください", "")

# 処理する関数（ここでは例として大文字に変換）
def process_text(input_text):
    # ここに処理を追加（例：入力テキストを大文字にする）
    return input_text.upper()

# ユーザーがテキストを入力した場合に処理
if user_input:
    # テキストを処理
    processed_text = process_text(user_input)
    
    # 処理後のテキストを表示
    st.write("処理後のテキスト:")
    st.text_area("", processed_text, height=300)

    # 処理後のテキストをファイルとしてダウンロードさせる
    to_download = io.BytesIO(processed_text.encode())
    st.download_button(
        label="テキストをダウンロード",
        data=to_download,
        file_name="processed_text.txt",
        mime="text/plain"
    )
