
import streamlit as st
import re
import json
import copy
import io
from collections import OrderedDict
import multiprocessing

with open('sorted_vocab.json', 'r') as f:
    sorted_vocab = json.load(f, object_pairs_hook=OrderedDict)
with open('sorted_vocab_copy.json', 'r') as f:
    sorted_vocab_copy = json.load(f, object_pairs_hook=OrderedDict)
sorted_keys = list(sorted_vocab.keys())




def replacer(s, new_word):###置換する語根すべてについて小文字か大文字か頭だけ大文字かを確認し、変換後もそれに合わせるための関数。 
    if s.islower():##それぞれqqq,QQQ,Qqqから始まるunicode化した状態に変化させることで、元の語根の大文字小文字の情報を保存している。　あくまで近似である。 (頭だけ大文字の場合:Qqq&#110;&#117;&#114;)
        return new_word.lower()
    elif s.isupper():
        return new_word.upper()
    elif s[0].isupper():
        return new_word.capitalize()
    else:
        return new_word
def multi_smart_replace(text, replacements):##replacerを使って大文字小文字の状態を保ったままの変換
    # for old_word, new_word in sorted_replacements:
    for old_word, new_word in replacements.items():
        text = re.sub(re.escape(old_word), lambda match: replacer(match.group(0), new_word), text, flags=re.IGNORECASE)

    # print(sorted_replacements)
    return text
def multiple_replace(text, replace_dict):
    # 各キーを正規表現のパターンとして結合する
    pattern = re.compile("|".join([re.escape(k) for k in replace_dict.keys()]), re.M)

    # 置換関数
    def sub_func(match):
        return replace_dict[match.group(0)]

    # 置換を実行
    return pattern.sub(sub_func, text)


def process_segment(lines, letter_type, esperanto_to_x, x_to_jijofu, x_to_hat, replacements_1, replacements_2):
    # 文字列のリストを結合してから置換処理を実行
    segment = '\n'.join(lines)
    segment = multiple_replace(segment, esperanto_to_x)
    segment = multi_smart_replace(segment, replacements_1)
    segment = multi_smart_replace(segment, replacements_2)

    if letter_type == '字上符':
        segment = multiple_replace(segment, x_to_jijofu)
    elif letter_type == '^形式':
        segment = multiple_replace(segment, x_to_hat)

    return segment

def parallel_process(text, num_processes, letter_type, esperanto_to_x, x_to_jijofu, x_to_hat, replacements_1, replacements_2):
    # テキストを行で分割
    lines = text.split('\n')
    num_lines = len(lines)
    lines_per_process = num_lines // num_processes

    # 各プロセスに割り当てる行のリストを決定
    ranges = [(i * lines_per_process, (i + 1) * lines_per_process) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], num_lines)  # 最後のプロセスが残り全てを処理

    with multiprocessing.Pool(processes=num_processes) as pool:
        # 並列処理を実行
        results = pool.starmap(process_segment, [(lines[start:end], letter_type, esperanto_to_x, x_to_jijofu, x_to_hat, replacements_1, replacements_2) for start, end in ranges])

    # 結果を結合
    return '\n'.join(result for result in results)

esperanto_to_x = {"ĉ": "cx","ĝ": "gx","ĥ": "hx","ĵ": "jx","ŝ": "sx","ŭ": "ux","Ĉ": "Cx","Ĝ": "Gx","Ĥ": "Hx","Ĵ": "Jx","Ŝ": "Sx","Ŭ": "Ux",
"c^": "cx","g^": "gx","h^": "hx","j^": "jx","s^": "sx","u^": "ux","C^": "Cx","G^": "Gx","H^": "Hx","J^": "Jx","S^": "Sx","U^": "Ux"}
x_to_jijofu={'cx': 'ĉ', 'gx': 'ĝ', 'hx': 'ĥ', 'jx': 'ĵ', 'sx': 'ŝ', 'ux': 'ŭ', 'Cx': 'Ĉ',
             'Gx': 'Ĝ', 'Hx': 'Ĥ', 'Jx': 'Ĵ', 'Sx': 'Ŝ', 'Ux': 'Ŭ'}
x_to_hat={'cx': 'c^', 'gx': 'g^', 'hx': 'h^', 'jx': 'j^', 'sx': 's^', 'ux': 'u^', 'Cx': 'C^',
          'Gx': 'G^', 'Hx': 'H^', 'Jx': 'J^', 'Sx': 'S^', 'Ux': 'U^'}

st.title("エスペラントの漢字化")
st.caption('これはエスペラント文を漢字表記に変換するアプリです。')

st.subheader('自己紹介')
st.text('webページの作り方')

code = '''
import streamlit as st
'''
st.code(code,language='python')





#画像
from PIL import Image

image = Image.open('エスペラントの漢字化の理想図.png')
st.image(image)
##動画も可能

with st.form(key='profile_form'):
    # テキストボックス
    

    # ラジオボタン
    letter_type = st.radio('文字形式',('字上符','x形式','^形式'))###select_boxでもいい

    sentence = st.text_area('エスペラントの文章')
    
    # ボタン
    submit_btn = st.form_submit_button('送信')
    cancel_btn = st.form_submit_button('キャンセル')
    if submit_btn:    
        # process the Esperanto text
        ## 原文がX型か字上符型か^型かを確認(0はX型、1は字上符型、2は^型)
        # 置換辞書を準備
        replacements_1 = {key: sorted_vocab[key][0] for key in sorted_keys}
        replacements_2 = {sorted_vocab_copy[key][0]: key for key in sorted_keys if '&#' in sorted_vocab_copy[key][0]}

        # 並列処理の実行
        processed_text = parallel_process(sentence, 8, letter_type, esperanto_to_x, x_to_jijofu, x_to_hat, replacements_1, replacements_2)
        
        st.text_area("", processed_text, height=300)
          
        
to_download = io.BytesIO(processed_text.encode())
st.download_button(
label="テキストをダウンロード",
data=to_download,
file_name="processed_text.html",
mime="text/plain"
)
    
# print(name)

