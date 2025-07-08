# -*- coding: utf-8 -*-
import cv2
import time
import os
import datetime
import requests
import serial
import threading

# ================================
# ?§Ï†ïÍ∞?# ================================
RTSP_URL = "rtsp://admin:dasung35$$@192.168.0.64/Streaming/Channels/101"
SAVE_PATH = "captured_images"
CAPTURE_INTERVAL_SECONDS = 29

SERIAL_PORT = '/dev/ttyACM0'  # WindowsÎ©?'COM4' ?¥Îü∞ 
SERIAL_BAUDRATE = 9600

# Render ?úÎ≤Ñ ?îÎìú?¨Ïù∏??API_IMAGE_UPLOAD = "https://flask-api-upload.onrender.com/upload"
API_PH = "https://flask-api-upload.onrender.com/upload_ph"
API_TEMP = "https://flask-api-upload.onrender.com/upload_temp"
API_HUM = "https://flask-api-upload.onrender.com/upload_hum"
API_CO2 = "https://flask-api-upload.onrender.com/upload_co2"

# ================================
# ?®Ïàò
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
                print(f"???¥Î?ÏßÄ ?ÖÎ°ú???±Í≥µ: {os.path.basename(filepath)}")
            else:
                print(f"???¥Î?ÏßÄ ?ÖÎ°ú???§Ìå®: {response.status_code}")
    except Exception as e:
        print(f"???¥Î?ÏßÄ ?ÖÎ°ú???§Î•ò: {e}")

def upload_ph(ph):
    try:
        response = requests.post(API_PH, json={"ph": ph})
        print(f"??pH ?ÖÎ°ú?? {ph}, ?ëÎãµ: {response.status_code}")
    except Exception as e:
        print(f"??pH ?ÖÎ°ú???§Î•ò: {e}")

def upload_temp(temp):
    try:
        response = requests.post(API_TEMP, json={"temp": temp})
        print(f"???®ÎèÑ ?ÖÎ°ú?? {temp}, ?ëÎãµ: {response.status_code}")
    except Exception as e:
        print(f"???®ÎèÑ ?ÖÎ°ú???§Î•ò: {e}")

def upload_hum(hum):
    try:
        response = requests.post(API_HUM, json={"humidity": hum})
        print(f"???µÎèÑ ?ÖÎ°ú?? {hum}, ?ëÎãµ: {response.status_code}")
    except Exception as e:
        print(f"???µÎèÑ ?ÖÎ°ú???§Î•ò: {e}")

def upload_co2(co2):
    try:
        response = requests.post(API_CO2, json={"co2": co2})
        print(f"??CO2 ?ÖÎ°ú?? {co2}, ?ëÎãµ: {response.status_code}")
    except Exception as e:
        print(f"??CO2 ?ÖÎ°ú???§Î•ò: {e}")

# ================================
# Ïπ¥Î©î??Î£®ÌîÑ
# ================================
def camera_loop():
    ensure_dir(SAVE_PATH)
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print(f"??Ïπ¥Î©î???∞Í≤∞ ?§Ìå®: {RTSP_URL}")
        return

    last_capture_time = time.time()
    frame_count = 0
    last_minute_marker = datetime.datetime.now().strftime("%y%m%d_%H%M")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("?†Ô∏è Ïπ¥Î©î???ÑÎ†à???§Ìå®")
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
            print(f"?ì∏ ?¥Î?ÏßÄ ?Ä?? {filename}")
            upload_image(filename)
            last_capture_time = current_time

        cv2.waitKey(1)

# ================================
# ?ºÏÑú Î£®ÌîÑ (Î≤ÑÌçº Ï¥àÍ∏∞???¨Ìï®)
# ================================
def sensor_loop():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        ser.reset_input_buffer()  # ?í• ?úÎ¶¨??Î≤ÑÌçº ?¥Î¶¨??        print(f"[?ºÏÑú] ?úÎ¶¨???∞Í≤∞?? {SERIAL_PORT}")
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
                    print(f"[?ºÏÑú] ?∞Ïù¥???åÏã± ?§Ìå®: '{line}' ??{e}")
    except Exception as e:
        print(f"[?ºÏÑú] ?úÎ¶¨???∞Í≤∞ ?§Ìå®: {e}")

# ================================
# Î©îÏù∏
# ================================
if __name__ == "__main__":
    threading.Thread(target=camera_loop, daemon=True).start()
    threading.Thread(target=sensor_loop, daemon=True).start()

    # Î©îÏù∏ ?∞Î†à?úÎ? ?†Ï?
    while True:
        time.sleep(1)
