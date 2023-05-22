import time
import serial
from enum import Enum
import threading


class State:
    class StateConst(Enum):
        """ State Const """
        PRESS_LEVEL = 0  # 按下引脚电平
        DOUBLE_DELAY = 25  # 双击等待判定
        LONG_DELAY = 50  # 单击等待判定

    # 枚举处理端状态
    class Status(Enum):
        IDLE = 0  # 空闲态
        ENROLL = 1  # 注册态
        WORK = 2  # 工作态
        QUIT = 3  # 退出
        CONFIRM_QUIT = 4  # 确认退出态

    # 枚举事件
    class Event(Enum):
        NULL = 0  # 无事件
        ENROLL_WEB = 1  # 靶箱注册事件
        GUN_ENROLL = 2  # 枪来注册
        OPEN_DETECT = 3
        CLOSE_DETECT = 4  # 关闭探测器
        SEND_CURVE = 5  # 发送轨迹信息
        SEND_POINT = 6  # 发送着弹点

    # 枚举动作
    class Action(Enum):
        NULL = 0  # 无触发

    # 通信状态枚举
    class Communication(Enum):
        SEND_FLAG = 0  # 发送标志位
        RECV_FLAG = 1  # 接收标志位


class Lc12s(object):
    # ID number1,ID number2,flag
    # ID number1,ID number2,flag

    def __init__(self, uart_baud, set_pin, machine_idh, machine_idl, net_idh, net_idl, rf_power,
                 rf_channel, data_length):

        self.net_idl = net_idl
        self.start = None
        self.data_length = data_length  # frame length
        self.uart = serial.Serial('/dev/ttyUSB0', uart_baud, timeout=1)
        # AA 5A 00 00 FF FF 00 1E 00 04 00 14 00 01 00 12 00 4B
        self.init_order = [0xaa, 0x5a, 0x00, 0x00, 0x00, 0x0c, 0x00, 0x1E, 0x00, 0x04, 0x00, 0x14, 0x00, 0x01, 0x00,
                           0x12, 0x00, 0x59]
        self.order = bytearray(self.init_order)
        self.machineid_high = machine_idh  # 1byte
        self.machineid_low = machine_idl  # 1byte
        self.init_order[4] = net_idh  # 1byte
        self.init_order[5] = net_idl  # 1byte
        self.init_order[7] = rf_power  # 0:6dbm 1:3dbm 2:1dbm 3:-2dbm 4:-8dbm
        self.init_order[11] = rf_channel  # 0~127
        self.checksum = self.check
        self.init_order[17] = self.checksum

        # byte0:0x0b:core and gun,0x16:core and web.
        # byte1:enroll:0x00 quit: 0x01 data:10 set:11
        # byte2:direction:0x10 up 0x01 down
        # byte3 and byte4: gun_id_high and gun_id_low
        # byte5 and byte6:target_id_high and target_id_low
        # byte7:axis
        # byte8:ack
        # byte9:bullet
        # byte10 and byte11: gun nc core aix
        # byte12 ,byte13 and byte14:nc
        self.core_gun = [0x0b, 0x10, 0x10, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x1E, 0x67, 0x68]
        self.core_web = [0x16, 0x10, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x01, 0x00, 0x1E, 0x07, 0x08, 0x69, 0x70, 0x71]
        self.datat_gun = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.datat_web = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.data_temp = None
        # state machine
        self.count = 0
        self.action = State.Action.NULL
        self.status = State.Status.IDLE
        self.event = State.Event.NULL
        # function flag
        self.receive_flag_g = False
        self.receive_flag_w = False
        self.target_enroll = False
        self.core_gun_flag = False
        self.core_web_flag = False
        self.receive_enroll_flag = False
        self.receive_data_flag = False
        self.receive_quit_flag = False
        self.confirm_set_flag = False
        self.send_interval = False

        self.open_flag = False
        # LOCK
        self.target_enroll_lock = threading.Lock()
        self.receive_enroll_lock = threading.Lock()
        self.receive_quit_lock = threading.Lock()
        self.confirm_set_lock = threading.Lock()
        self.gun_data_lock = threading.Lock()
        self.web_data_lock = threading.Lock()
        self.receive_gun_lock = threading.Lock()
        self.receive_web_lock = threading.Lock()
        self.receive_data_lock = threading.Lock()
        # Send state
        self.send_flag = False

    def config(self):
        # 设置
        self.uart.write(bytearray(self.order))
        time.sleep(0.5)
        self.uart.flushInput()

    def check(self):
        # checksum count
        temp = 0
        for i in range(17):
            temp = self.init_order[i] + temp
        temp = (temp & 0xff)
        return temp

    # 发送消息函数
    def send(self, data_buffer):
        temp = bytearray(data_buffer)
        self.uart.write(temp)
        if not self.send_interval:
            time.sleep(0.01)
        else:
            time.sleep(0.100)

    # 接收消息函数
    def recv(self):
        self.start = time.time()
        uart_temp = ''
        if self.uart.inWaiting():
            uart_temp = self.uart.read(1)
        if len(uart_temp) > 0:
            head = int(uart_temp[0])
            if head == 0xaa:
                uart_temp = self.uart.read(17)
                uart_temp = 0
            if head == 0x0b:
                self.gun_data_lock.acquire()
                self.datat_gun = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                self.datat_gun[0] = head
                uart_temp = self.uart.read(11)
                for i in range(1, len(self.datat_gun)):
                    self.datat_gun[i] = int(uart_temp[i - 1])
                self.gun_data_lock.release()
                self.receive_gun_lock.acquire()
                self.receive_flag_g = True
                self.receive_gun_lock.release()
            if head == 0x16:
                self.web_data_lock.acquire()
                self.datat_web = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                self.datat_web[0] = head
                uart_temp = self.uart.read(14)
                for i in range(1, len(self.datat_web)):
                    self.datat_web[i] = int(uart_temp[i - 1])
                self.web_data_lock.release()
                self.receive_web_lock.acquire()
                self.receive_flag_w = True
                self.receive_web_lock.release()
        # self.get_message()

    #        end = time.time()
    #        print(end - self.start )
    def get_message(self):
        if self.receive_flag_g:
            self.receive_gun_lock.acquire()
            self.receive_flag_g = False
            self.receive_gun_lock.release()
            if self.datat_gun[0] == 11 and (self.datat_gun[2] == 16):
                self.gun_data_lock.acquire()
                temp = self.datat_gun
                self.gun_data_lock.release()
                temp[8] = 153
                temp[2] = 0x01
                #                buffer = 0
                #                buffer = bytearray(temp)
                #                self.uart.write(buffer)
                self.send_interval = True
                self.send(temp)
                self.send_interval = False
                if self.datat_gun[1] == 0:
                    self.receive_enroll_lock.acquire()
                    self.receive_enroll_flag = True
                    self.receive_enroll_lock.release()
                    self.receive_quit_lock.acquire()
                    self.receive_quit_flag = False
                    self.receive_quit_lock.release()
                    self.core_gun[3] = self.datat_gun[3]
                    self.core_gun[4] = self.datat_gun[4]
                elif self.datat_gun[1] == 0x01:
                    self.receive_enroll_lock.acquire()
                    self.receive_enroll_flag = False
                    self.receive_enroll_lock.release()
                    self.receive_quit_lock.acquire()
                    self.receive_quit_flag = True
                    self.receive_quit_lock.release()
                    self.core_gun[3] = 0xff
                    self.core_gun[4] = 0xff
                elif self.datat_gun[1] == 0x10:
                    self.receive_data_lock.acquire()
                    self.receive_data_flag = True
                    self.receive_data_lock.release()
                elif self.datat_gun[1] == 0x11:
                    self.confirm_set_flag = True
        elif self.receive_flag_w:
            self.receive_web_lock.acquire()
            self.receive_flag_w = False
            self.receive_web_lock.release()
            if self.datat_web[0] == 0x16 and self.datat_web[2] == 0x01:
                if self.datat_web[1] == 0x00:
                    if self.datat_web[8] == 0x99:
                        print("确认注册")
                        self.target_enroll_lock.acquire()
                        self.target_enroll = True
                        self.target_enroll_lock.release()
                elif self.datat_web[1] == 0x01:
                    if self.datat_web[8] == 0x99:
                        print("quit confirm")
                elif self.datat_web[1] == 0x10:
                    if self.datat_web[8] == 0x99:
                        print("data confirm")
                elif self.datat_web[1] == 0x11:
                    print("收到设置")
                    self.core_gun_flag = True

        else:
            self.gun_data_lock.acquire()
            self.datat_web = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.gun_data_lock.release()
            self.web_data_lock.acquire()
            self.datat_gun = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.web_data_lock.release()

    # enroll
    def enroll(self):
        self.core_web[0] = 0x16
        self.core_web[1] = 0x00
        self.core_web[2] = 0x10
        self.core_web[8] = 0x00
        self.send_interval = True
        self.send(self.core_web)
        self.send_interval = False
        # quit

    def quit(self):
        self.core_web[0] = 0x16
        self.core_web[1] = 0x01
        self.core_web[2] = 0x10
        self.core_web[8] = 0x00
        self.send_interval = True
        self.send(self.core_web)
        self.send_interval = False
        # send axis

    def hit(self, flag, aim_ring, shoot_ring, shake, shake_v, shoot_shake, shoot_shake_v, axis_x, axis_y):
        self.core_web[0] = 0x16
        self.core_web[1] = 0x10
        self.core_web[2] = 0x10
        self.core_web[3] = flag  # 击中靶子
        self.core_web[4] = aim_ring
        self.core_web[5] = shoot_ring
        self.core_web[6] = shake
        self.core_web[7] = shake_v
        self.core_web[8] = shoot_shake
        self.core_web[9] = shoot_shake_v
        axis_xh = int(axis_x / 480.0 * 100)
        axis_xl = int((axis_x / 480.0 * 100 - axis_xh)) * 100
        axis_yh = int(axis_y / 480.0 * 100)
        axis_yl = int((axis_y / 480.0 * 100) - axis_yh) * 100
        self.core_web[10] = axis_xh  # 取出高位
        self.core_web[11] = axis_xl  # 取出低位
        self.core_web[12] = axis_yh  # 取出高位
        self.core_web[13] = axis_yl  # 取出低位
        print("坐标为", axis_x, axis_y)
        self.send_interval = False
        self.send(self.core_web)
        self.send_interval = True
        # confirm to recv

    def recv_fsm(self):
        if self.status == State.Status.IDLE:
            if self.target_enroll:
                self.target_enroll_lock.acquire()
                self.target_enroll = False
                self.target_enroll_lock.release()
                print("confirm target enroll")
                self.status = State.Status.ENROLL
                self.event = State.Event.NULL
                self.count = 0
            else:
                self.status = State.Status.IDLE
                self.event = State.Event.NULL
                self.count = self.count + 1
                print("target enroll")
                if self.count > 600:
                    print("try again")
                    self.status = State.Status.IDLE
                    self.event = State.Event.NULL
                    self.count = 0
                self.enroll()
        if self.status == State.Status.ENROLL:
            if self.receive_enroll_flag:  # enroll ack
                self.receive_enroll_lock.acquire()
                self.receive_enroll_flag = False
                self.receive_enroll_lock.release()
                self.status = State.Status.WORK  # gun enroll
                self.event = State.Event.ENROLL_WEB
                self.count = 0
            else:
                print("wait for gun")
                self.status = State.Status.ENROLL
                self.event = State.Event.NULL
                self.count = self.count + 1
                if self.count > 600:
                    print("timeout ")
                    self.count = 0
        if self.status == State.Status.WORK:
            # gun enroll
            if self.receive_data_flag:
                if self.open_flag:
                    self.status = State.Status.WORK
                    self.event = State.Event.SEND_POINT
            else:
                if self.open_flag:
                    self.status = State.Status.WORK
                    self.event = State.Event.SEND_CURVE
                else:
                    pass
            if self.receive_quit_flag:
                self.status = State.Status.ENROLL
                self.event = State.Event.CLOSE_DETECT
                self.count = 0

    # event_handle
    def event_handle(self):
        if self.event == State.Event.OPEN_DETECT:
            self.open_flag = True
            self.event = State.Event.NULL
        elif self.event == State.Event.CLOSE_DETECT:
            print("close camera")
            self.event = State.Event.NULL
        elif self.event == State.Event.SEND_CURVE:
            if self.open_flag:
                pass
        elif self.event == State.Event.SEND_POINT:
            if self.open_flag:
                self.event = State.Event.NULL
                print("hit target")

# core = Lc12s(9600,12,0x01,0xc8,0x00,0x0C,0x1E,0x14,0X12)
# def recv():
#     while 1:
#         core.recv()
#
#
# def get():
#     while 1:
#         core.get_message()
#
#
# def recv_fsm():
#     while 1:
#         core.recv_fsm()
# serial_thread = threading.Thread(target=recv)
# serial_thread.start()
# play_thread = threading.Thread(target=get)
# play_thread.start()
# fsm = threading.Thread(target=recv_fsm)
# fsm.start()
#
# if __name__ == "__main__":
# core = Lc12s(9600,12,0x01,0xc8,0x00,0x0C,0x1E,0x14,0X12)
# while True:
# core.recv_fsm()
# core.event_handle()
