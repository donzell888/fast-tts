import binascii
from quart import Quart, request, jsonify, Response, render_template
import json
import edge_tts

app = Quart(__name__)


@app.route('/')
async def home():
    return await render_template('home.html')


@app.route('/generate', methods=['POST'])
async def generate():
    data = await request.get_data()
    payload = binascii.hexlify(data).decode('utf8')
    t = {"code": 1, "audio_url": "/tts?payload=" + payload}
    return jsonify(t)


@app.route('/tts', methods=['GET'])
async def tts():
    payload = request.args.get("payload")
    plaintext = binascii.unhexlify(payload).decode('utf8')
    json_obj = json.loads(plaintext)
    content = json_obj["content"]
    voice = json_obj.get("voice", "zh-CN-XiaoxiaoNeural")
    headers = {'Transfer-Encoding': 'chunked', 'Content-Type': 'audio/mpeg'}
    response_content = ms_tts_async(content, voice)
    return Response(response_content, headers=headers)


async def ms_tts_async(text_input, voice="zh-CN-XiaoxiaoNeural"):
    communicate = edge_tts.Communicate(text_input, voice)
    async for chunked in communicate.stream():
        if chunked["type"] == "audio":
            yield chunked["data"]


if __name__ == '__main__':
    app.run()
