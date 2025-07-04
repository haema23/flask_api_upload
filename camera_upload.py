import cv2
import time
import os
import datetime
import requests
import serial
import threading

# ================================
# 설정값
# ================================
RTSP_URL = "rtsp://admin:dasung35$$@192.168.0.64/Streaming/Channels/101"
SAVE_PATH = "captured_images"
CAPTURE_INTERVAL_SECONDS = 29

SERIAL_PORT = 'COM11'  # Windows면 'COM4' 이런 식
SERIAL_BAUDRATE = 9600

# Render 서버 엔드포인트
API_IMAGE_UPLOAD = "https://flask-api-upload.onrender.com/upload"
API_PH = "https://flask-api-upload.onrender.com/upload_ph"
API_TEMP = "https://flask-api-upload.onrender.com/upload_temp"
API_HUM = "https://flask-api-upload.onrender.com/upload_hum"
API_CO2 = "https://flask-api-upload.onrender.com/upload_co2"

# ================================
# 함수
# ================================
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def upload_image(filepath):
    try:
        with open(filepath, 'rb') as f:
            files = {'image': f}
            response = requests.post(API_IMAGE_UPLOAD, files=files)
            if response.status_code == 200:
                print(f"✅ 이미지 업로드 성공: {os.path.basename(filepath)}")
            else:
                print(f"❌ 이미지 업로드 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 이미지 업로드 오류: {e}")

def upload_ph(ph):
    try:
        response = requests.post(API_PH, json={"ph": ph})
        print(f"✅ pH 업로드: {ph}, 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ pH 업로드 오류: {e}")

def upload_temp(temp):
    try:
        response = requests.post(API_TEMP, json={"temp": temp})
        print(f"✅ 온도 업로드: {temp}, 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ 온도 업로드 오류: {e}")

def upload_hum(hum):
    try:
        response = requests.post(API_HUM, json={"humidity": hum})
        print(f"✅ 습도 업로드: {hum}, 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ 습도 업로드 오류: {e}")

def upload_co2(co2):
    try:
        response = requests.post(API_CO2, json={"co2": co2})
        print(f"✅ CO2 업로드: {co2}, 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ CO2 업로드 오류: {e}")

# ================================
# 카메라 루프
# ================================
def camera_loop():
    ensure_dir(SAVE_PATH)
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print(f"❌ 카메라 연결 실패: {RTSP_URL}")
        return

    last_capture_time = time.time()
    frame_count = 0
    last_minute_marker = datetime.datetime.now().strftime("%y%m%d_%H%M")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ 카메라 프레임 실패")
            time.sleep(5)
            continue

        current_time = time.time()
        if current_time - last_capture_time >= CAPTURE_INTERVAL_SECONDS:
            now = datetime.datetime.now()
            current_minute_marker = now.strftime("%y%m%d_%H%M")
            if current_minute_marker != last_minute_marker:
                frame_count = 0
                last_minute_marker = current_minute_marker
            frame_count += 1

            filename = os.path.join(SAVE_PATH, f"{current_minute_marker}_{frame_count:04d}.jpg")
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            print(f"📸 이미지 저장: {filename}")
            upload_image(filename)
            last_capture_time = current_time

        cv2.waitKey(1)

# ================================
# 센서 루프 (버퍼 초기화 포함)
# ================================
def sensor_loop():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        ser.reset_input_buffer()  # 💥 시리얼 버퍼 클리어
        print(f"[센서] 시리얼 연결됨: {SERIAL_PORT}")
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    ph, temp, hum, co2 = map(float, line.split(","))
                    upload_ph(ph)
                    upload_temp(temp)
                    upload_hum(hum)
                    upload_co2(co2)
                except Exception as e:
                    print(f"[센서] 데이터 파싱 실패: '{line}' → {e}")
    except Exception as e:
        print(f"[센서] 시리얼 연결 실패: {e}")

# ================================
# 메인
# ================================
if __name__ == "__main__":
    threading.Thread(target=camera_loop, daemon=True).start()
    threading.Thread(target=sensor_loop, daemon=True).start()

    # 메인 쓰레드를 유지
    while True:
        time.sleep(1)
