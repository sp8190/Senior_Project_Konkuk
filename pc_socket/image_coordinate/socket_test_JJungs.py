# -*- coding: utf-8 -*-
# 라즈베리파이 GPIO 패키지
import os
import pigpio
import RPi.GPIO as GPIO
import time
import socket
import threading

os.system("sudo pigpiod") # pigpio on
time.sleep(1)
pi = pigpio.pi() # Connect to local Pi.

# 모터 상태
STOP  = 0
FORWARD  = 1
BACKWORD = 2
LEFT = 3
RIGHT = 4

# 모터 채널
CH1 = 0
CH2 = 1

# PIN 입출력 설정
OUTPUT = 1
INPUT = 0

# PIN 설정
HIGH = 1
LOW = 0

# 실제 핀 정의
#PWM PIN
ENA = 26  #37 pin
ENB = 0   #27 pin

#GPIO PIN
IN1 = 13  #37 pin
IN2 = 19  #35 pin
IN3 = 5   #31 pin
IN4 = 6   #29 pin

# 핀 설정 함수
def setPinConfig(EN, INA, INB):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(EN, GPIO.OUT)
    GPIO.setup(INA, GPIO.OUT)
    GPIO.setup(INB, GPIO.OUT)
    # 100khz 로 PWM 동작 시킴 
    pwm = GPIO.PWM(EN, 100) 
    # 우선 PWM 멈춤.   
    pwm.start(0) 
    return pwm

# 모터 제어 함수
def setMotorContorl(pwm, INA, INB, speed, stat):

    #모터 속도 제어 PWM
    pwm.ChangeDutyCycle(speed)  
    
    #앞으로
    if stat == FORWARD:
        GPIO.output(INA, HIGH)
        GPIO.output(INB, LOW)
        
    #뒤로
    elif stat == BACKWORD:
        GPIO.output(INA, LOW)
        GPIO.output(INB, HIGH)

    #왼쪽으로
    elif stat == LEFT:
        if pwm == pwmA:
            GPIO.output(INA, LOW)
            GPIO.output(INB, HIGH)
        else:
            GPIO.output(INA, HIGH)
            GPIO.output(INB, LOW)

    #오른쪽으로
    elif stat == RIGHT:
        if pwm == pwmA:
            GPIO.output(INA, HIGH)
            GPIO.output(INB, LOW)
        else:
            GPIO.output(INA, LOW)
            GPIO.output(INB, HIGH)
        
    #정지
    elif stat == STOP:
        GPIO.output(INA, LOW)
        GPIO.output(INB, LOW)
        
#모터 핀 설정
#핀 설정후 PWM 핸들 얻어옴 
pwmA = setPinConfig(ENA, IN1, IN2)
pwmB = setPinConfig(ENB, IN3, IN4)
        
# 모터 제어함수 간단하게 사용하기 위해 한번더 래핑(감쌈)
def setMotor(ch, speed, stat):
    if ch == CH1:
        #pwmA는 핀 설정 후 pwm 핸들을 리턴 받은 값이다.
        setMotorContorl(pwmA, IN1, IN2, speed, stat)
    else:
        #pwmB는 핀 설정 후 pwm 핸들을 리턴 받은 값이다.
        setMotorContorl(pwmB, IN3, IN4, speed, stat)

def wavesensor():
    # Yellow : Pin 18 : 24(Trig)
    GPIO.setup(24, GPIO.OUT)
    # White : Pin 16 : 23(Echo)
    GPIO.setup(23, GPIO.IN)
    
    global wave_distance
    global stop_thread
    stop_thread = False
    
    while True:
        if stop_thread == True:
            break
        
        GPIO.output(24, False)
        time.sleep(0.5)

        GPIO.output(24, True)
        time.sleep(0.00001)
        GPIO.output(24, False)

        # 18번이 OFF가 되는 시점을 시작시간으로 설정
        while GPIO.input(23) == 0:
            start = time.time()

        # 18번이 ON이 되는 시점을 반사파 수신시간으로 설정
        while GPIO.input(23) == 1:
            stop = time.time()

        # 초음파가 되돌아오는 시간차로 거리를 계산한다
        time_interval = stop - start
        distance = time_interval * 17000
        distance = round(distance, 2)
        wave_distance = distance

        print("Distance => ", wave_distance, "cm")
        
def server_bind():

    HOST = '192.168.1.165'
    # 서버 주소, 라즈베리파이 IP 입력
    PORT = 5521
    # 클라이언트 접속 대기 포트 번호

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #AF_INET : 주소 체계 IPv4 인터넷 프로토콜, SOCK_STREAM : TCP 통신

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # setsockopt : 소켓 옵션을 정하는 함수 
    # SOL_SOCKET : 소켓 옵션 레벨 중 하나
    # SO_REUSEADDR : 커널이 소켓을 사용하는 중에도 계속 소켓을 사용할 수 있도록 한다.

    #소켓을 특정 네트워크 인터페이스와 포트 번호에 연결.
    server_socket.bind((HOST,PORT))

    #서버가 클라이언트의 접속을 허용하도록 함.
    server_socket.listen()

    #accept 함수에서 대기하다가 클라이언트가 접속하면 새로운 소켓과 주소을 리턴
    client_socket, addr = server_socket.accept()

    #클라이언트의 주소 리턴
    print("Connected by ",addr)


    while True:

        if stop_thread == True: # 스레드가 멈추면 빠져나오기
            break

        #클라이언트 보낸 메시지를 수신하기 위해 대기합니다.
        data = client_socket.recv(1024)

        str_list = data.decode().split("/")

        # 왼쪽일지 오른쪽일지 결정
        # X 좌표는 얼마만큼 돌지 결정
        if len(str_list) == 3:
            if str_list[0] == "L":
                setMotor(CH1, 100, LEFT)
                setMotor(CH2, 100, LEFT)
                time.sleep(1)

                setMotor(CH1, 80, STOP)
                setMotor(CH2, 80, STOP)
            elif str_list[0] == "R":
                setMotor(CH1, 100, RIGHT)
                setMotor(CH2, 100, RIGHT)
                time.sleep(1)

                setMotor(CH1, 80, STOP)
                setMotor(CH2, 80, STOP)

            # Y 좌표는 얼마만큼 움직일지 결정
            if int(str_list[2]) > 60: 
                if wave_distance > 10: # 앞 객체간 거리가 10 이상일 때만 움직임
                    setMotor(CH1, 100, FORWARD)
                    setMotor(CH2, 100, FORWARD)
                    time.sleep(1)

                    setMotor(CH1, 80, STOP)
                    setMotor(CH2, 80, STOP)
                
        #빈 문자열을 수신하면 루프를 중지합니다.
        if not data:
            break

        # data.decode() type = str
        #수신받은 문자열을 출력합니다.
        print("Received from ", addr, data.decode())


    #소켓을 닫습니다.
    client_socket.close()
    server_socket.close()
    
def streaming():
    os.system("cd /home/pi/gst-rtsp-0.10.8/gst-rtsp-server/examples ; ./test-launch \"( rpicamsrc preview=false bitrate=2000000 keyframe-interval=15 ! video/x-h264, width=1280, height=720, framerate=35/1 ! h264parse ! rtph264pay name=pay0 pt=96 )\"")

    
t_wavesensor = threading.Thread(target=wavesensor)
t_socket = threading.Thread(target=server_bind)
t_streamer = threading.Thread(target=streaming)

try:
    t_wavesensor.start()
    t_socket.start()
    t_streamer.start()

# 서보모터 종료
except KeyboardInterrupt:
    os.system("sudo killall pigpiod") # pigpio off
    stop_thread = True
    pi.stop()
    GPIO.cleanup()