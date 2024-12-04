# coding:utf-8
import sys
import time
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot,QBuffer, QByteArray
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtSerialPort import QSerialPortInfo
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import setTheme, Theme, FluentTranslator
from myFluentWindow import myFluentWindow
from controller_interface import ControllerInterface
from crc import CrcCheck

import serial.tools.list_ports
import logging, serial


class SerialThread(QThread):

    serial_signal = pyqtSignal(str)

    def __init__(self,controller_interface):
        super().__init__()

        self.controller_interface = controller_interface

        self.start_run_ = False
        self.glazer_serial = serial.Serial()
        self.glazer_serial.port = None
        self.glazer_serial.baudrate = "115200"
        self.glazer_serial.bytesize = serial.EIGHTBITS
        self.glazer_serial.parity = serial.PARITY_NONE
        self.glazer_serial.stopbits = serial.STOPBITS_ONE

        self.tx_data_ = bytearray(57)


    def run(self):
        while not self.start_run_:
            time.sleep(0.1)
        while self.start_run_:
            if self.glazer_serial.is_open:
                self.glazer_serial.write(self.tx_data_)
                time.sleep(0.1)

    def open(self):
        if self.glazer_serial.port is not None:  # 检查串口号是否设置
            self.glazer_serial.open()
            self.start_run_ = True  # 允许线程运行
            self.start()  # 启动线程
            print("我调用了open,打开了串口")
        else:
            print("无串口号！")

    def close(self):
        if self.glazer_serial.is_open:  # 检查串口是否打开
            self.start_run_ = False  # 停止线程运行
            self.glazer_serial.close()  # 关闭串口
            self.wait()  # 等待线程结束
            print("我调用了close,关闭了串口")
        else:
            print("请先打开串口 好吗")

    def write_data(self, data):
        if self.glazer_serial.is_open:  # 检查串口是否打开
            self.glazer_serial.write(data.encode('utf-8'))

    @pyqtSlot(str)
    def send_serial_port(self, message):
        """子线程接收主线程的信号并处理"""
        print(f"子线程 send_serial_port 收到消息: {message}")
        self.glazer_serial.port = message

    @pyqtSlot(str)
    def start_or_stop_flag(self, message):
        print(f"子线程收到消息: {message}")
        if message == "start":
            self.start_run_ = True
        else:
            self.start_run_ = False

    @pyqtSlot(str)
    def open_serial(self,message):
        print(f"子线程收到消息: {message}")
        if message == "open":
            self.start_run_ = True
            self.open()
        else:
            self.start_run_ = False
            self.close()

    @pyqtSlot(bytearray)
    def update_ctrl_data(self,message):
        self.tx_data_[:len(message)] = message
    


class MainWindow(myFluentWindow):
    
    start_serial_signal_ = pyqtSignal(str)
    open_serial_signal_ = pyqtSignal(str)
    send_serial_port_signal_ = pyqtSignal(str)

    tx_ctrl_data_signal_ = pyqtSignal(bytearray)

    def __init__(self):
        super().__init__()

        self.controller_interface = ControllerInterface(self)
        self.tx_data_crc_ = CrcCheck()

        self._selected_port = None  # 私有变量用于存储选中的串口
        self.serial = None  # 串口对象
        self.serial_is_open = None  # 串口对象
        
        self.initNavigation()
        self.initWindow()
        self.comboBoxSerial.activated.connect(self.select_port)
        self.pushButtonSerial.clicked.connect(self.open_or_close_serial)  # 连接激活信号以选择串口
        
        
        self.worker_thread = None
        self.start_task()
        # # 轮询串口，更新到串口选择器中
        self.update_serial_ports(first_init=True)
        self.select_port()
        self.timer_serial_list = QTimer()  # 创建定时器
        self.timer_serial_list.timeout.connect(self.update_serial_ports)  # 连接定时器的超时信号
        self.timer_serial_list.start(1000)

        self.timer_send_signal_ = QTimer()
        self.timer_send_signal_.timeout.connect(self.update_send_data_)
        self.timer_send_signal_.start(1)
        

    def start_task(self):
        if self.worker_thread is None or not self.worker_thread.isRunning():
            self.worker_thread = SerialThread(self.controller_interface)
            # 连接子线程的信号到主线程的槽函数
            self.start_serial_signal_.connect(self.worker_thread.start_or_stop_flag)
            self.open_serial_signal_.connect(self.worker_thread.open_serial)
            self.send_serial_port_signal_.connect(self.worker_thread.send_serial_port)
            self.tx_ctrl_data_signal_.connect(self.worker_thread.update_ctrl_data)

    def stop_task(self):
        if self.worker_thread:
            self.worker_thread.terminate()  # 强制结束线程（谨慎使用）
            self.worker_thread = None


    def open_or_close_serial(self):
        if self.pushButtonSerial.text() == "打开":  # 按下打开串口
            if self.check_serial_port():
                self.serial_is_open = True
                self.pushButtonSerial.setText("关闭")  # 打开成功，设置按钮文字为“关闭”
                self.open_serial_signal_.emit("open")
                self.start_serial_signal_.emit("start")
        else:  # 按下关闭串口
            self.serial_is_open = False
            self.pushButtonSerial.setText("打开")
            self.start_serial_signal_.emit("stop")
            self.open_serial_signal_.emit("close")
            print(f"已关闭串口")

    def check_serial_port(self):
        """检查串口是否可用"""
        try:
            serial_test = serial.Serial(self._selected_port)
            serial_test.close()
            return True
        except serial.SerialException:
            return False
        
    def select_port(self):
        self._selected_port = self.comboBoxSerial.currentText()  # 获取当前选中的串口
        self.send_serial_port_signal_.emit(self._selected_port)
        print(f"_selected_port: {self._selected_port}")

    def update_serial_ports(self, first_init=False):
        ports = serial.tools.list_ports.comports()
        current_selection = self.comboBoxSerial.currentText()

        if first_init == True:
            current_selection = str('Not Set')
        else:
            # 清空原来的项
            self.comboBoxSerial.clear()

        for port in ports:
            self.comboBoxSerial.addItem(port.device)  # 将串口号添加到 ComboBox

        # 如果当前选中的串口仍然存在列表中，保持选中状态
        if current_selection in [self.comboBoxSerial.itemText(i) for i in range(self.comboBoxSerial.count())]:
            index = self.comboBoxSerial.findText(current_selection)
            self.comboBoxSerial.setCurrentIndex(index)
        else:
            # 如果当前选中的串口不在新的列表中，清空选中项或设置为默认项
            self.comboBoxSerial.setCurrentIndex(-1)  # 设置为没有选中的状态，或者可以设置为一个默认串口

    def update_send_data_(self):
        
        _data = bytearray(57)

        _data[0]  = 0xAA
        _data[1]  = 0xBB
        _data[2]  = 0xA1
        _data[3]  = int(self.controller_interface.send_comprosser_en_)
        _data[4]  = 0xA2
        _data[5]  = int(self.controller_interface.send_comprosser_duty_)
        _data[6]  = 0xA3
        _data[7]  = int(self.controller_interface.send_condenser_en_)
        _data[8]  = 0xA4
        _data[9]  = int(self.controller_interface.send_condenser_duty_)
        _data[10] = 0xA5
        _data[11] = int(self.controller_interface.send_stir_motor_en_)
        _data[12] = 0xA6 
        _data[13] = int(self.controller_interface.send_stir_motor_duty_)
        _data[14] = 0xA7
        _data[15] = int(self.controller_interface.send_lift_pi_en_)
        _data[16] = 0xA8
        _data[17] = int(self.controller_interface.send_drop_pi_en_)
        _data[18] = 0xA9
        _data[19] = int(self.controller_interface.send_ball_pi_en_)
        _data[20] = 0xB1
        _data[21] = int(self.controller_interface.send_from_tank_en_)
        _data[22] = 0xB2
        _data[23] = int(self.controller_interface.send_to_tank_en_)
        _data[24] = 0xB3
        _data[25] = int(self.controller_interface.send_lift_motor_reset_flag_)
        _data[26] = 0xB4
        _data[27] = int(self.controller_interface.send_lift_motor_set_pos_val_)
        _data[28] = 0xB5
        _data[29] = int(self.controller_interface.send_lift_motor_send_flag_)
        _data[30] = 0xB6
        _data[31] = int(self.controller_interface.send_lift_to_big_cube_pos_)
        _data[32] = 0xB7
        _data[33] = int(self.controller_interface.send_lift_to_small_cube_pos_)
        _data[34] = 0xB8
        _data[35] = int(self.controller_interface.send_lift_to_ball_pos_)
        _data[36] = 0xB9
        _data[37] = int(self.controller_interface.send_ice_door_reset_flag_)
        _data[38] = 0xC1
        _data[39] = int(self.controller_interface.send_ice_door_open_door_)
        _data[40] = 0xC2
        _data[41] = int(self.controller_interface.send_ice_door_close_door_)
        _data[42] = 0xC3
        _data[43] = int(self.controller_interface.send_put_down_ice_flag_)
        _data[44] = 0xC4
        _data[45] = int(self.controller_interface.send_ref_valve_reset_flag_)
        _data[46] = 0xC5
        _data[47] = int(self.controller_interface.send_ref_valve_to_ice_make_)
        _data[48] = 0xC6
        _data[49] = int(self.controller_interface.send_ref_valve_to_store_)
        _data[50] = 0xC7
        _data[51] = int(self.controller_interface.send_store_fan_en_)
        _data[52] = 0xC8
        _data[53] = int(self.controller_interface.send_store_heating_en_)
        _data[54] = 0xCC
        _data[55] = 0xDD
        _data[56] = self.tx_data_crc_.crc8_checksum_get(_data[:56])
    
        self.tx_ctrl_data_signal_.emit(_data)



    def initNavigation(self):
        self.addSubInterface(self.controller_interface, FIF.SETTING, "设备测试")
        self.navigationInterface.addSeparator()
        self.navigationInterface.setExpandWidth(150)                # 设置导航栏宽度
        self.navigationInterface.setCollapsible(False)              # 导航栏不可收缩
        self.navigationInterface.setReturnButtonVisible(True)       # 返回按钮可见
        self.navigationInterface.setMenuButtonVisible(False)        # 菜单按钮不可见

    def initWindow(self):
        self.resize(1650, 870)
        self.setWindowIcon(QIcon("resource/img/glazer_icon.png"))
        self.setWindowTitle("GLAZER-DEBUG TOOL")
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

if __name__ == '__main__':

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    setTheme(Theme.DARK)
    app = QApplication(sys.argv)

    translator = FluentTranslator()
    app.installTranslator(translator)
    w = MainWindow()
    w.show()

    app.exec_()

