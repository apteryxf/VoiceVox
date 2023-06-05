import openai
import pyttsx3
import subprocess
import requests # APIを使う
import json # APIで取得するJSONデータを処理する
import pyaudio # wavファイルを再生する
import time # タイムラグをつける

# OpenAI APIの設定
openai.api_key = ""
model_engine = "gpt-3.5-turbo"

# 音声合成の設定
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# 音声認識の設定
r = sr.Recognizer()

# マイクから音声を取得して認識
with sr.Microphone() as source:
    print("話してください...")
    audio = r.listen(source)

try:
    # 音声をテキストに変換
    text = r.recognize_google(audio, language='ja-JP')
    print("入力されたテキスト：", text)
except sr.UnknownValueError:
    print("音声を認識できませんでした。")
except sr.RequestError as e:
    print("音声を変換できませんでした； {0}".format(e))

# テキストを送信して返答を取得
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "日本語で返答してください。"
        },
        {
            "role": "user",
            "content": text
        },
    ],
)

# 返答を取得
answer = response.choices[0]["message"]["content"].strip()
print(answer)

#　返答を音声で出力
def text_to_speech(answer):
    try:
        # 音声合成クエリの作成
        res1 = requests.post('http://127.0.0.1:50021/audio_query',params = {'text': answer, 'speaker': 1})
        # 音声合成データの作成
        res2 = requests.post('http://127.0.0.1:50021/synthesis',params = {'speaker': 1},data=json.dumps(res1.json()))
        # 
        data = res2.content

        # PyAudioのインスタンスを生成
        p = pyaudio.PyAudio()

        # ストリームを開く
        stream = p.open(format=pyaudio.paInt16,  # 16ビット整数で表されるWAVデータ
                        channels=1,  # モノラル
                        rate=24000,  # サンプリングレート
                        output=True)

        # 再生を少し遅らせる（開始時ノイズが入るため）
        time.sleep(0.2) # 0.2秒遅らせる

        # WAV データを直接再生する
        stream.write(data)  

        # ストリームを閉じる
        stream.stop_stream()
        stream.close()

        # PyAudio のインスタンスを終了する
        p.terminate()
    except subprocess.CalledProcessError as e:
        print("Voicevox実行時にエラーが発生しました:", e)

text_to_speech(answer)
