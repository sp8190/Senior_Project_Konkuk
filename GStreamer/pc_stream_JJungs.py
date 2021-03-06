# -*- coding: utf-8 -*-
import socket
import threading
import sys
import subprocess
import os
from datetime import datetime
import cv2 as cv2
import math
from queue import Queue

queue = Queue() #쓰레드간 작업 공유

def mouse_callback(event, x, y, flags, param): 
    
    if event == cv2.EVENT_LBUTTONDOWN:
        my_str = "x: "+str(x)+" y: "+str(y)+" 입니다"
        print(my_str) # 이벤트 발생한 마우스 위치 출력
        queue.put(my_str)
    
def opencv_img():

    cap = cv2.VideoCapture("gst-launch-1.0 -v tcpclientsrc host=192.168.1.165 port=5000 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false",cv2.CAP_GSTREAMER)
    cv2.namedWindow('frame_color')  #마우스 이벤트 영역 윈도우 생성
    cv2.setMouseCallback('frame_color', mouse_callback)

    while(True):
        ret, frame = cap.read()    # Read 결과와 frame

        if(ret) :

            cv2.imshow('frame_color', frame)    # 컬러 화면 출력
            if cv2.waitKey(1) == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()


def client_send():
    HOST = '192.168.1.165'
    # 서버 주소, 라즈베리파이 IP 입력
    PORT = 5521
    # 클라이언트 접속 대기 포트 번호

    #소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    #지정한 HOST와 PORT로 연결
    client_socket.connect((HOST, PORT))
    

    while True:
        #메시지를 전송합니다
        my_str = queue.get()
        user_command = my_str

        client_socket.sendall(user_command.encode())

        #메시지 수신

        data = client_socket.recv(1024)
        print("Received ", repr(data.decode()))
        # qkdkran https://shoark7.github.io/programming/python/difference-between-__repr__-vs-__str__

        if user_command == 'break':
            print("연결 종료")
            break
            


#쓰레드 열기
t_socket = threading.Thread(target=client_send)
t_imgShow = threading.Thread(target=opencv_img)
t_socket.start()
t_imgShow.start()

k = cv2.waitKey(1) & 0xFF
if k == 27:    # ESC 키 눌러졌을 경우 종료
    print("ESC 키 눌러짐")
    t_socket.close()
    t_imgShow.close()

