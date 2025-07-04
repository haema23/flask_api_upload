from flask import Flask, request, jsonify
import os
import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "received_images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ========= 메모리 내 센서 데이터 저장 =========
data_storage = {
    "ph": [],
    "temp": [],
    "hum": [],
    "co2": []
}

@app.route("/", methods=["GET"])
def index():
    return """
    ✅ 서버 작동 중<br>
    <ul>
      <li><a href='/data'>전체 센서 데이터 보기</a></li>
      <li><a href='/ph'>pH 데이터만 보기</a></li>
      <li><a href='/temp'>온도 데이터만 보기</a></li>
      <li><a href='/hum'>습도 데이터만 보기</a></li>
      <li><a href='/co2'>CO2 데이터만 보기</a></li>
      <li><a href='/files'>저장된 이미지 파일 리스트</a></li>
    </ul>
    """

@app.route("/upload", methods=["POST"])
def upload_image():
    if 'image' not in request.files:
        return "❌ 이미지 파일이 없습니다.", 400

    image = request.files['image']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{image.filename}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(save_path)
    print(f"✅ 이미지 수신 및 저장: {save_path}")
    return "ok", 200

@app.route("/upload_ph", methods=["POST"])
def upload_ph():
    data = request.json
    data_storage["ph"].append(data)
    print(f"✅ pH 데이터 수신: {data}")
    return "ok", 200

@app.route("/upload_temp", methods=["POST"])
def upload_temp():
    data = request.json
    data_storage["temp"].append(data)
    print(f"✅ 온도 데이터 수신: {data}")
    return "ok", 200

@app.route("/upload_hum", methods=["POST"])
def upload_hum():
    data = request.json
    data_storage["hum"].append(data)
    print(f"✅ 습도 데이터 수신: {data}")
    return "ok", 200

@app.route("/upload_co2", methods=["POST"])
def upload_co2():
    data = request.json
    data_storage["co2"].append(data)
    print(f"✅ CO2 데이터 수신: {data}")
    return "ok", 200

# ========= 각 센서 데이터 확인 =========
@app.route("/data", methods=["GET"])
def show_all_data():
    return jsonify(data_storage)

@app.route("/ph", methods=["GET"])
def show_ph():
    return jsonify(data_storage["ph"])

@app.route("/temp", methods=["GET"])
def show_temp():
    return jsonify(data_storage["temp"])

@app.route("/hum", methods=["GET"])
def show_hum():
    return jsonify(data_storage["hum"])

@app.route("/co2", methods=["GET"])
def show_co2():
    return jsonify(data_storage["co2"])

# ========= 이미지 파일 리스트 =========
@app.route("/files", methods=["GET"])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    files.sort(reverse=True)
    return "<br>".join(files)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
