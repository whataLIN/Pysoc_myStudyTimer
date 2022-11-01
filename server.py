from socket import *
from threading import *
from queue import *
import sys
import pandas as pd #*
import datetime
import time

from dataclasses import dataclass
#!stop 입력 시

HOST = '127.0.0.10'
PORT = 9190

s = ''
s += '\n  -------------< 사용 방법 >-------------'
s += '\n   연결 종료 : !quit 입력 or ctrl + c     '
s += '\n   참여 중인 멤버 보기 : !member 입력      '
s += '\n   귓속말 보내기 : /w [상대방이름] [메시지]   '
s += '\n'
s += '\n     이 프로그램은 Jupyter Notebook에      '
s += '\n            최적화되어 있습니다.             '
s += '\n  --------------------------------------\n\n'

class timeuser:
    name: str=None
    goaltime_hour: int=None
    goaltime_min: int=None
    goaltime_sec: int=None
    currsecone: int=0
    profilePic:int = 1


def now_time():
    now = datetime.datetime.now()
    time_str = now.strftime('[%H:%M] ')
    return time_str


def send_func(lock):
    while True:
        try:
            recv = received_msg_info.get()

            if recv[0] == '!quit' or len(recv[0]) == 0:
                msg = str('[SYSTEM] ' + now_time() + left_member_name) + '님이 연결을 종료하였습니다.'

            elif recv[0] == '!enter' or recv[0] == '!member':
                now_member_msg = '현재 멤버 : '
                for mem in member_name_list:
                    if mem != '-1':
                        now_member_msg += '[' + mem + '] '
                recv[1].send(now_member_msg.encode())
                if (recv[0] == '!enter'):
                    msg = str('[SYSTEM] ' + now_time() + member_name_list[recv[2]]) + '님이 입장하였습니다.'
                else:
                    recv[1].send(now_member_msg.encode())
                    continue


            elif recv[0].find('/w') == 0:           #귓속말
                split_msg = recv[0].split()
                if split_msg[1] in member_name_list:
                    msg = now_time() + '(귓속말) ' + member_name_list[recv[2]] + ' : '
                    msg += recv[0][len(split_msg[1]) + 4:len(recv[0])]
                    idx = member_name_list.index(split_msg[1])
                    whisper_list[idx] = recv[2]
                    socket_descriptor_list[idx].send(msg.encode())
                else:
                    msg = '해당 사용자가 존재하지 않습니다.'
                    recv[1].send(msg.encode())
                continue

            elif recv[0].find('/r') == 0:
                whisper_receiver = whisper_list[recv[2]]
                if whisper_receiver != -1:
                    msg = now_time() + '(귓속말) ' + member_name_list[recv[2]] + ' : '
                    msg += recv[0][3:len(recv[0])]
                    socket_descriptor_list[whisper_receiver].send(msg.encode())
                    whisper_list[whisper_receiver] = recv[2]
                else:
                    msg = '귓속말 대상이 존재하지 않습니다.'
                    recv[1].send(bytes(msg.encode()))
                continue

            elif recv[0]=='!starttimer': ##start 시 리스트 옮기기
                '''whereisC=waiting_member_list.index(recv[2])
                active_member_list.append(waiting_member_list[whereisC])
                del waiting_member_list[whereisC]'''

                #timerRun(recv[2].)        해당 유저 sec만큼 timer 시작


            elif recv[0]=='!stoptimer':
                           ##stop 시 리스트 옮기기
                whereisC=active_member_list.index(recv[2])
                waiting_member_list.append(active_member_list[whereisC])
                del active_member_list



            else:
                msg = str(now_time() + member_name_list[recv[2]]) + ' : ' + str(recv[0])

            for conn in socket_descriptor_list:
                if conn == '-1':
                    continue
                elif recv[1] != conn:
                    conn.send(msg.encode())
                else:
                    pass
            if recv[0] == '!quit':
                recv[1].close()

            if recv[0] == '!start':
                 return

        except:
            pass


def recv_func(conn, count, lock):
    if socket_descriptor_list[count] == '-1':
        return -1
    while True:
        global left_member_name
        data = conn.recv(1024).decode()
        received_msg_info.put([data, conn, count])

        if data == '!quit' or len(data) == 0:
            lock.acquire()
            print(str(now_time() + member_name_list[count]) + '님이 연결을 종료하였습니다.')
            left_member_name = member_name_list[count]
            socket_descriptor_list[count] = '-1'
            for i in range(len(whisper_list)):
                if whisper_list[i] == count:
                    whisper_list[i] = -1
            member_name_list[count] = '-1'
            lock.release()
            break

    conn.close()

def member_data() :
    member_data = {'member': member_name_list,
          'password': pw_list,
          'time': stopwatch_time_list } # 누적시간
    member_frame= pd.DataFrame(member_data, columns=['member', 'time', 'password'])


def timerRun(lefthour, leftminute, currsecond):  #시간 저장의 문제

    leftsecond = lefthour * 3600 + leftminute * 60

    try:
        while leftsecond != 0:

            realLeftHour = leftsecond // 3600
            goaltime_hour=realLeftHour

            realLeftMinute = (leftsecond - realLeftHour * 3600) // 60
            goaltime_min=realLeftMinute

            realLeftSecond = leftsecond - (realLeftHour * 3600 + realLeftMinute * 60)
            goaltime_sec=realLeftSecond

            currHour=currsecond//3600
            currMin=(currsecond - currHour * 3600) // 60
            currSec=currsecond - (currHour * 3600 + currMin * 60)

            time.sleep(1)

            leftsecond-=1
            currsecond+=1

    except KeyboardInterrupt:

        print("\n타이머를 중단했습니다.")
        leftsecond = realLeftHour * 3600 + realLeftMinute * 60


        lefttime_fm="{:02d}:{:02d}:{:02d}".format(realLeftHour,realLeftMinute,realLeftSecond)
        timeformat_sw = "{:02d}:{:02d}:{:02d}".format(currHour, currMin, currsecond)
        print("남은 시간: ",lefttime_fm)

        pass




#=============================================================================main


print(now_time() + '서버를 시작합니다')
server_sock = socket(AF_INET, SOCK_STREAM)
server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen()

count = 0
socket_descriptor_list = ['-1', ]
waiting_member_list=['-1', ]
active_member_list=['-1', ]
member_name_list = ['-1', ]
pw_list = ['-1', ] #비밀번호 리스트 추가 *
stopwatch_time_list = ['-1', ] #누적시간 리스트 추가 **
whisper_list = [-1, ]

received_msg_info = Queue()
left_member_name = ''
lock = Lock()

while True:
    count = count + 1
    conn, addr = server_sock.accept()

    client=timeuser()

    while True:
        username = conn.recv(1024).decode()

        if not username in member_name_list:
            conn.send('yes'.encode())
            break
        else:
            conn.send('overlapped'.encode())
    client.name = username

    clientHour = int(conn.recv(1024).decode())  # 시간수신
    client.goaltime_hour = clientHour

    clientMin = int(conn.recv(1024).decode())  # 분수신
    client.goaltime_min = clientMin

    clientsec = int(conn.recv(1024).decode())  # 초수신
    client.goaltime_sec = clientsec

    client.c


    member_name_list.append(client)
    socket_descriptor_list.append(conn)
    whisper_list.append(-1)
    print(str(now_time()) + client.name + '님이 연결되었습니다. 연결 ip : ' + str(addr[0]))

    if count > 1:
        sender = Thread(target=send_func, args=(lock,))
        sender.start()
        pass
    else:
        sender = Thread(target=send_func, args=(lock,))
        sender.start()
    receiver = Thread(target=recv_func, args=(conn, count, lock))
    receiver.start()





server_sock.close()