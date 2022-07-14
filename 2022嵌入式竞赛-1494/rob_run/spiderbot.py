# pip install pyserial
# https://pyserial.readthedocs.io/en/latest/pyserial.html
# 提供串口服务
import serial
import serial.tools.list_ports
# 数据类型
import numpy as np
# 线程实现监听
import threading
# 计时服务
import time
# 获取可用端口号
port_list = list(serial.tools.list_ports.comports())
# 列出可用端口号和详细数据
for port,desc,hwid in sorted(port_list):
    print("{}:{} [{}]".format(port,desc,hwid))


class listeningThread(threading.Thread):
    def __init__(self, uart):
        threading.Thread.__init__(self)
        self.uart = uart
        self.runFlag = False
        self.buff = list()
        self.getSuccess = 0

    def getdate(self):
        buff = list()
        if (self.getSuccess == 3):
            buff = self.buff.copy()
            self.clearBuf()
        return buff

    def state(self):
        return [self.runFlag, self.getSuccess]

    def open(self):
        self.runFlag = True
        self.start()

    def close(self):
        self.runFlag = False

    def clearBuf(self):
        self.buff.clear()
        self.getSuccess = 0

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print("start listen")
        while self.runFlag:
            """start = time.time()
            while(time.time()- start <0.10):
                pass
            buff = self.uart.readall() # 读出全部字符
            for i in range(len(buff)):
                if( buff[i] ==  buff[i+1] == 0x55):
                    print(buff[i+2:i+2+buff[i+2]])
                    self.buff.append(buff[i+2:i+2+buff[i+2]])
                    self.getSuccess = 3
            """
            if (self.getSuccess == 3):
                continue
            # getSuccess 0: 未接收 1：接收到第一个0x55 2:接收到第二个0x55 3：接收完毕
            _temp = self.uart.read()  # 读取数据
            _temp = int(bytes.hex(_temp), base=16)  # 将数据从字符串转为 int 型
            if ((self.getSuccess == 0) and (_temp == 0x55)):
                time_start = time.time()
                self.getSuccess = 1
            elif ((self.getSuccess == 1) and (_temp == 0x55)):
                self.getSuccess = 2
            elif (self.getSuccess == 2):  # 开始接收
                self.buff.append(_temp)
                if (self.buff[0] <= len(self.buff)):  # 接收到指定长度
                    self.getSuccess = 3
            if ((self.getSuccess >= 1) and (time.time() - time_start > 1)):  # 接收数据超时
                print("time out")
                self.clearBuf()
            pass


class Uart:
    # 默认波特率 9600， 超时 1s
    def __init__(self, COM, BPS=9600, timeout=1.0):
        self.__uart = serial.Serial(COM, BPS, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE, timeout=timeout)
        self.action = {
            # "获取电压"
            "getBattery": [0x0F],
            # "动作名称" : [指令码 舵机个数 时间低八位 时间高八位 舵机1ID 舵机1动作低八位 舵机1动作高八位 舵机2ID 舵机2动作低八位 舵机2动作高八位... ...]
            "test": [0x03, 0x01, 0xE8, 0x03, 0x12, 0x20, 0x03],
            "test_same": [3, 2, np.uint8((1000 & 0xFF)), np.uint8((1000 & 0xFF00) >> 8), 2, np.uint8(0 & 0xFF),
                          np.uint8((0 & 0xFF00) >> 8), 3, np.uint8((800 & 0xFF)), np.uint8((800 & 0xFF00) >> 8)],
            "stand_up_0":[3, 3, np.uint8((500 & 0xFF)), np.uint8((500 & 0xFF00) >> 8),
                          1, np.uint8(500 & 0xFF),np.uint8((500 & 0xFF00) >> 8),
                          2, 0x38, np.uint8((312 & 0xFF00) >> 8),
                          3, np.uint8(200 & 0xFF), np.uint8((200 & 0xFF00) >> 8)]}

        # 创建接受缓存区
        self.buffer = []

    def spiderSend(self, data: list):
        # 添加帧头和数据长度信息
        senddata = [0x55, 0x55, len(data) + 1] + data
        self.__uart.write(senddata)
        # 返回发送的数据
        return senddata

    def read(self):
        return self.__uart.read()

    def listeningOpen(self):
        self.__listenythread = listeningThread(self.__uart)
        self.__listenythread.open()

    def listeningClose(self):
        self.__listenythread.close()

    def encode(self, data: list):
        if (data[1] == 15):  # 15 == 0x0F 电池电压
            print("battery: {}V".format((data[3] * 1. * 255 + data[2]) / 1000))
        else:
            print("code not in code list")

    def listeningStatue(self):
        state = self.__listenythread.state()
        if state[0] == True:
            if state[1] == 0:
                print("no data receive")
            elif state[1] == 1 or state[1] == 2:
                print("data has not receive all code:{}".format(state[1]))
            elif state[1] == 3:
                self.buffer.clear()
                self.buffer = self.__listenythread.getdate()
                self.encode(self.buffer)
            else:
                print("state error")
        else:
            print("listen no running")

    # 关闭串口
    def close(self):
        self.__uart.close()

    def __exit__(self):
        self.close()


uart = Uart("COM5")
uart.spiderSend(uart.action["stand_up_0"])
start = time.time()
uart.listeningOpen()
for i in range(20):
    uart.spiderSend(uart.action["getBattery"])
    _start = time.time()
    while(time.time()- _start < 0.1):
                pass
    uart.listeningStatue()
uart.listeningClose()
# uart.listeningStatue()
print("{}s".format(time.time()-start))
uart.close()