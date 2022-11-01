from socket import *
from threading import *
import os
import datetime
import time
import winsound as alarm
import pandas as pd
import os

import asyncio


Host = '127.0.0.10'
Port = 9190

global currsecond

def beepsound() :
    freq = 2000 # 빈도
    dur = 1000 # 지속시간
    alarm.Beep(freq, dur)


def now_time():
    now = datetime.datetime.now()
    time_str = now.strftime('[%H:%M] ')
    return time_str


def send_func():
    while True:
        send_data = input('당신 : ')
        client_sock.send(send_data.encode('utf-8'))
        if send_data == '!quit':
            print('연결을 종료하였습니다.')
            break
        elif send_data=='!start':
            try:
                client_sock.send(send_data.encode())
                timerRun(goaltime_hour,goaltime_min,currsecond) #지역변수 문제
            except KeyboardInterrupt:
                send_data='!stoptimer'
                client_sock.send(send_data.encode())
            #시작 구현되면 수정할것



    client_sock.close()
    os._exit(1)


def recv_func():
    while True:
        try:
            recv_data = (client_sock.recv(1024)).decode('utf-8')
            if len(recv_data) == 0:
                print('[SYSTEM] 서버와의 연결이 끊어졌습니다.')
                client_sock.close()
                os._exit(1)
        except Exception as e:
            print('예외가 발생했습니다.', e)
            print('[SYSTEM] 메시지를 수신하지 못하였습니다.')
        else:
            print(recv_data)
            pass


def timerRun(lefthour, leftminute, currsecond):

    leftsecond = lefthour * 3600 + leftminute * 60
    client_sock.send(str(currsecond).encode())

    try:
        while leftsecond != 0:

            #타이머 변수
            realLeftHour = leftsecond // 3600
            goaltime_hour=realLeftHour

            realLeftMinute = (leftsecond - realLeftHour * 3600) // 60
            goaltime_min=realLeftMinute

            realLeftSecond = leftsecond - (realLeftHour * 3600 + realLeftMinute * 60)
            goaltime_sec=realLeftSecond

            #스톱워치 변수
            currHour=currsecond//3600
            currMin=(currsecond - currHour * 3600) // 60
            currSec=currsecond - (currHour * 3600 + currMin * 60)

            time.sleep(1)

            timeformat_timer="{:02d}:{:02d}:{:02d}".format(realLeftHour,realLeftMinute,realLeftSecond) #타이머 표시
            timeformat_sw= "{:02d}:{:02d}:{:02d}".format(currHour, currMin, currSec)   #스톱워치 표시
            print("\x08" * 50 + "종료까지: "+timeformat_timer+"  남은 시간: "+timeformat_sw, end='')


            leftsecond-=1
            currsecond+=1

    except KeyboardInterrupt:

        print("\n타이머를 중단했습니다.")
        leftsecond = realLeftHour * 3600 + realLeftMinute * 60


        lefttime_fm="{:02d}:{:02d}:{:02d}".format(realLeftHour,realLeftMinute,realLeftSecond)
        timeformat_sw = "{:02d}:{:02d}:{:02d}".format(currHour, currMin, currsecond)
        print("남은 시간: ",lefttime_fm)


        pass





#======================main


client_sock = socket(AF_INET, SOCK_STREAM)
try:
    client_sock.connect((Host, Port))

except ConnectionRefusedError:
    print('서버에 연결할 수 없습니다.')
    print('1. 서버의 ip주소와 포트번호가 올바른지 확인하십시오.')
    print('2. 서버 실행 여부를 확인하십시오.')
    os._exit(1)

except:
    print('프로그램을 정상적으로 실행할 수 없습니다. 프로그램 개발자에게 문의하세요.')

else:
    print('[SYSTEM] 서버와 연결되었습니다.')


declStart = input("로그인을 원하시면 로그인을 입력해주세요 ! ")  # GUI 생기면 버튼으로 대체

if declStart=="로그인":

    while True:

        cname = str(input('사용하실 닉네임을 입력하세요 :'))

        if ' ' in cname:
            print('공백은 입력이 불가능합니다.')
            continue

        client_sock.send(cname.encode())
        is_possible_name = client_sock.recv(1024).decode()

        if is_possible_name == 'yes':

            print("입장했습니다.")
            client_sock.send('!enter'.encode())

            goaltime_hour = int(input('목표 시간(hour): '))
            client_sock.send((str(goaltime_hour)).encode())

            goaltime_min = int(input('목표 시간(min): '))
            client_sock.send((str(goaltime_min)).encode())

            goaltime_sec = int(input('목표 시간(sec): '))
            client_sock.send((str(goaltime_sec)).encode())

        elif is_possible_name == 'overlapped':
            print('[SYSTEM] 이미 사용중인 닉네임입니다.')

        elif len(client_sock.recv(1024).decode()) == 0:
            print('[SYSTEM] 서버와의 연결이 끊어졌습니다.')
            client_sock.close()
            os._exit(1)

        while True:
            if goaltime_hour <= 0 and goaltime_min <= 0:
                print('시간을 입력해주세요.')
                continue
            elif (str(type(goaltime_hour)) != "<class 'int'>") or (str(type(goaltime_min)) != "<class 'int'>"):
                print("숫자를 입력해주세요.")
                continue
            else: break

        pw = input("비밀번호를 입력해주세요 ! \n")
        client_sock.send((str(pw)).encode())

        print("로그인이 완료되었습니다. \n ")
        print(cname + "님 오늘도 열공하세요 ! ")

        #timerRun(goaltime_hour,goaltime_min)
        break

def hh_rank() :
    timetosec=goaltime_min*60+goaltime_hour*3600





sender = Thread(target=send_func, args=())
receiver = Thread(target=recv_func, args=())
sender.start()
receiver.start()

while True:
    time.sleep(1)
    pass

client_sock.close()