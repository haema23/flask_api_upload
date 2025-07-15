#include <DFRobot_DHT11.h>
#include <SoftwareSerial.h>
#include <HCMotor.h>

// --- 모터 ---
#define DIR_PIN 8
#define CLK_PIN 9
#define LLIMIT_PIN 3
#define RLIMIT_PIN 2

HCMotor HCMotor;
#define STEPS_FOR_30CM 30000L
#define PAUSE_DURATION 1500
#define ACTUAL_MOVE_DURATION 21000L
int Speed = 40;
int moveCount = 0;
int currentDirection = FORWARD;

// --- pH 센서 ---
#define PH_PIN A0

// --- DFRobot DHT11 ---
#define DHTPIN A1
DFRobot_DHT11 DHT;

// --- CO2 (UART) ---
SoftwareSerial mySerial(13, 11);
unsigned char Send_data[4] = {0x11,0x01,0x01,0xED};
unsigned char Receive_Buff[8];
unsigned char recv_cnt = 0;
unsigned int PPM_Value;

// --- CO2 함수 ---
void Send_CMD(void) {
  for (int i=0; i<4; i++) {
    mySerial.write(Send_data[i]);
    delay(1);
  }
}
unsigned char Checksum_cal(void) {
  unsigned char SUM=0;
  for(int count=0; count<7; count++) {
    SUM += Receive_Buff[count];
  }
  return 256 - SUM;
}

void setup() {
  Serial.begin(9600);

  // 모터
  HCMotor.Init();
  HCMotor.attach(0, STEPPER, CLK_PIN, DIR_PIN);
  HCMotor.DutyCycle(0, Speed);
  HCMotor.Direction(0, currentDirection);

  // 리미트 스위치
  pinMode(LLIMIT_PIN, INPUT_PULLUP);
  pinMode(RLIMIT_PIN, INPUT_PULLUP);

  // CO2
  pinMode(13, INPUT);
  pinMode(11, OUTPUT);
  mySerial.begin(9600);

  Serial.println("# READY"); // 필요시 동기화 신호
}

void loop() {
  // ============ 모터 이동 ============
  HCMotor.Direction(0, currentDirection);
  HCMotor.Steps(0, STEPS_FOR_30CM);

  unsigned long moveStart = millis();
  bool limitStop = false;
  while (millis() - moveStart < ACTUAL_MOVE_DURATION) {
    if ((currentDirection == FORWARD && digitalRead(LLIMIT_PIN) == LOW) ||
        (currentDirection == REVERSE && digitalRead(RLIMIT_PIN) == LOW)) {
      Serial.println("# LIMIT"); // ★ 파이썬에서 즉시 캡처 플래그 설정
      limitStop = true;
      break;
    }
  }

  HCMotor.Steps(0, 0);
  delay(PAUSE_DURATION);

  // ============ 센서 측정 ============
  float ph = analogRead(PH_PIN) * (5.0 / 1023.0);

  DHT.read(DHTPIN);
  int temp = DHT.temperature;
  int hum = DHT.humidity;

  Send_CMD();
  recv_cnt = 0;
  unsigned long co2Start = millis();
  while (millis() - co2Start < 500) {
    if (mySerial.available()) {
      Receive_Buff[recv_cnt++] = mySerial.read();
      if (recv_cnt ==8) break;
    }
  }
  if (recv_cnt == 8 && Checksum_cal() == Receive_Buff[7]) {
    PPM_Value = Receive_Buff[3]<<8 | Receive_Buff[4];
  } else {
    PPM_Value = 0;
  }

  // CSV 형식으로 출력
  Serial.print(ph, 2);
  Serial.print(",");
  Serial.print(temp);
  Serial.print(",");
  Serial.print(hum);
  Serial.print(",");
  Serial.println(PPM_Value);

  delay(1500); // DHT11 최소 주기

  // ============ 방향 전환 ============
  if (limitStop) {
    moveCount = 0;
    currentDirection = (currentDirection == FORWARD) ? REVERSE : FORWARD;
  } else {
    moveCount++;
    if (moveCount >= 2) {
      moveCount = 0;
      currentDirection = (currentDirection == FORWARD) ? REVERSE : FORWARD;
    }
  }
}
