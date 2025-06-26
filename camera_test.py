import cv2
import time
import os
import datetime

# --- 설정값 (GUI나 설정 파일에서 받아오도록 수정 가능) ---
RTSP_URL = "rtsp://admin:dasung35$$@192.168.0.64:554/Streaming/Channels/101"
SAVE_PATH = "captured_images"  # 이미지를 저장할 폴더
CAPTURE_INTERVAL_SECONDS = 5  # 캡처 간격 (초)
FILENAME_PREFIX = "cam01_"
SHOW_PREVIEW = True # 미리보기 창 표시 여부
# ----------------------------------------------------

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"폴더 생성: {directory}")

def main():
    ensure_dir(SAVE_PATH)
    print(f"이미지 저장 위치: {os.path.abspath(SAVE_PATH)}")
    print(f"캡처 간격: {CAPTURE_INTERVAL_SECONDS}초")

    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print(f"오류: 카메라를 열 수 없습니다. RTSP URL을 확인하세요: {RTSP_URL}")
        return

    print("카메라 연결 성공. 이미지 수집을 시작합니다. (Ctrl+C로 종료)")

    last_capture_time = time.time()
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("오류: 프레임을 읽을 수 없습니다. 스트림이 종료되었거나 문제가 있습니다.")
                # 재연결 로직 등을 추가할 수 있습니다.
                time.sleep(5) # 잠시 대기 후 재시도
                cap.release()
                cap = cv2.VideoCapture(RTSP_URL)
                if not cap.isOpened():
                    print("오류: 카메라 재연결 실패. 프로그램을 종료합니다.")
                    break
                else:
                    print("카메라 재연결 성공.")
                continue

            current_time = time.time()

            # 미리보기 (선택 사항)
            if SHOW_PREVIEW:
                preview_frame = cv2.resize(frame, (640, 360)) # 창 크기에 맞게 조절
                cv2.imshow('Live Preview - Hikvision (Press "q" to close this window)', preview_frame)
                # 'q' 키를 누르면 미리보기 창만 닫고 프로그램은 계속 실행
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyWindow('Live Preview - Hikvision (Press "q" to close this window)')
                    # SHOW_PREVIEW = False # 다시 켜지지 않도록 설정 변경도 가능


            # 지정된 간격으로 이미지 캡처 및 저장
            if current_time - last_capture_time >= CAPTURE_INTERVAL_SECONDS:
                frame_count += 1
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] # 밀리초까지
                filename = os.path.join(SAVE_PATH, f"{FILENAME_PREFIX}{timestamp}_{frame_count:04d}.jpg")

                try:
                    # 이미지 품질 설정 (0-100, 높을수록 고품질, 용량 커짐)
                    cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
                    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 이미지 저장: {filename}")
                    last_capture_time = current_time
                except Exception as e:
                    print(f"오류: 이미지 저장 실패 - {filename}, {e}")

            # CPU 사용량 줄이기 위해 짧은 대기 시간 추가 (waitKey에서 이미 어느정도 처리됨)
            # time.sleep(0.01) # cv2.waitKey(1)이 비슷한 역할

    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 중단되었습니다.")
    finally:
        print("자원 해제 중...")
        cap.release()
        cv2.destroyAllWindows()
        print("프로그램 종료.")

if __name__ == "__main__":
    main()