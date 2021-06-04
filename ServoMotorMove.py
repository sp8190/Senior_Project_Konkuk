import RPi.GPIO as GPIO # ?????? GPIO ?? ???? ???
import pyautogui
import time

pyautogui.PAUSE=1
pyautogui.FAILSAFE=True

pin = 16

GPIO.setmode(GPIO.BOARD) # ?? ??? ?? ???? ??, BCM? GPIO ??? ???
GPIO.setup(pin, GPIO.OUT) # GPIO ??? ? ??
pwm=GPIO.PWM(pin, 50) # ????? PWM? ?????. 16??? 50Hz ??? ??

pwm.start(9) # ?? ???, ??? ?????
time.sleep(1) # ?? ????? ???? ?? ??? ? ??? ???? ??

#1??? ???? ??? ??(x,y)
try:
    while True:
        print("current mouse position:",pyautogui.position())
        #time.sleep(0.1)
        
        # 0 ~ 1919
                
        pwm.ChangeDutyCycle((pyautogui.position().x/1800)*7) # ?? 2~12 ??? ?? ?????
        time.sleep(0.05) # ????? ?????? ??? ??? ??. ?? ?? ?? ???? ????? ??


# ?? ??? ???? ????? ??? ???? ??? ??? ??
except KeyboardInterrupt:
    pwm.stop() 
GPIO.cleanup(pin)
