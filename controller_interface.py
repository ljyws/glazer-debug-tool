# coding:utf-8
from PyQt5.QtGui import QColor, QIntValidator
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer
from qfluentwidgets import FluentIcon, setFont, InfoBarIcon
from qfluentwidgets import FluentIcon as FIF
from resource.ui.Ui_controller import Ui_Controller

class ControllerInterface(Ui_Controller, QWidget):

    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setupUi(self)

        self.send_comprosser_en_ = False
        self.send_comprosser_duty_ = self.comprosser_duty.value()
        self.send_condenser_en_ = False
        self.send_condenser_duty_ = self.condenser_duty.value()
        self.send_stir_motor_en_ = False
        self.send_stir_motor_duty_ = self.stir_motor_duty.value()
        self.send_lift_pi_en_ = False
        self.send_drop_pi_en_ = False
        self.send_ball_pi_en_ = False
        self.send_from_tank_en_ = False
        self.send_to_tank_en_ = False
        self.send_lift_motor_reset_flag_ = False
        self.send_lift_motor_send_flag_ = False
        self.send_lift_motor_current_pos_val_ = 0
        self.send_lift_motor_set_pos_val_ = 0
        self.send_lift_to_big_cube_pos_ = False
        self.send_lift_to_small_cube_pos_ = False
        self.send_lift_to_ball_pos_ = False
        self.send_ice_door_reset_flag_ = False
        self.send_ice_door_open_door_ = False
        self.send_ice_door_close_door_ = False
        self.send_put_down_ice_flag_ = False
        self.send_ref_valve_reset_flag_ = False
        self.send_ref_valve_to_ice_make_ = False
        self.send_ref_valve_to_store_ = False
        self.send_store_fan_en_ = False
        self.send_store_heating_en_ = False
        self.timer_init()
        self.moudle_init()

    def timer_init(self):
        self.timerout = QTimer(self)
        self.timerout.timeout.connect(self.handle_timeout)

    def start_timer(self, callback_method, timeout):
        self.current_timeout_cb = callback_method
        self.timerout.setSingleShot(True)
        self.timerout.start(timeout)

    def handle_timeout(self):
        getattr(self, self.current_timeout_cb)()


    """  压缩机控制回调函数   """
    def comprosser_en_button_cb(self, isChecked: bool):
        self.send_comprosser_en_ = True if isChecked else False
        text = '开' if isChecked else '关'
        self.comprosser_en_button.setText(text)

    def comprosser_duty_cb(self):
        self.send_comprosser_duty_ = self.comprosser_duty.value()
        self.comprosser_duty_label.setText(str(self.comprosser_duty.value())+'%')
        
    """  冷凝器控制回调函数   """
    def condenser_en_button_cb(self, isChecked: bool):
        self.send_condenser_en_ = True if isChecked else False
        text = '开' if isChecked else '关'
        self.condenser_en_button.setText(text)

    def condenser_duty_cb(self):
        self.send_condenser_duty_ = self.condenser_duty.value()
        self.condenser_duty_label.setText(str(self.condenser_duty.value())+'%')

    """  搅拌电机控制回调函数   """
    def stir_motor_en_button_cb(self, isChecked: bool):
        self.send_stir_motor_en_ = True if isChecked else False
        text = '开' if isChecked else '关'
        self.stir_motor_button.setText(text)

    def stir_motor_duty_cb(self):
        self.send_stir_motor_duty_ = self.stir_motor_duty.value()
        self.stir_duty_label.setText(str(self.stir_motor_duty.value())+'%')

    """  加热膜控制回调函数   """
    def lift_pi_en_button_cb(self,isChecked):
        self.send_lift_pi_en_ = True if isChecked else False
        text = '开' if isChecked else '关'
        self.lift_pi_en_button.setText(text)

    def drop_pi_en_button_cb(self,isChecked):
        self.send_drop_pi_en_ = True if isChecked else False
        text = '开' if isChecked else '关'
        self.drop_pi_en_button.setText(text)

    def ball_pi_en_button_cb(self,isChecked):
        self.send_ball_pi_en_ = True if isChecked else False
        text = '开' if isChecked else '关'
        self.ball_pi_en_button.setText(text)

    """  水路控制回调函数   """
    def from_tank_pump_button_cb(self,isChecked):
        self.send_from_tank_en_ = True if isChecked else False
        text = '开' if isChecked else '关'
        self.from_tank_pump_button.setText(text)

    def to_tank_pump_button_cb(self,isChecked):
        self.send_to_tank_en_ = True if isChecked else False
        text = '开' if isChecked else '关'
        self.to_tank_pump_button.setText(text)

    def lift_motor_reset_cb(self):
        self.send_lift_motor_reset_flag_ = True 
        self.start_timer('reset_lift_motor_reset_flag_cb',500)

    def reset_lift_motor_reset_flag_cb(self):
        self.send_lift_motor_reset_flag_ = False

    def lift_motor_set_send_pos_cb(self):
        text =  self.lift_motor_set_pos_val.text().strip()
        if text.isdigit():
            number = int(text)
            if(number>100):
                self.lift_motor_set_pos_val.clear()
            else:
                if number >= 0:
                    self.send_lift_motor_send_flag_ = True
                    self.start_timer('reset_lift_motor_send_flag_cb',1000)
                    self.send_lift_motor_set_pos_val_ = number

    def reset_lift_motor_send_flag_cb(self):
        self.send_lift_motor_send_flag_ = False

    def lift_motor_send_to_big_cube_cb(self):
        self.send_lift_motor_reset_flag_ = True
        self.start_timer('reset_lift_motor_send_to_big_cube_cb',1000)

    def reset_lift_motor_send_to_big_cube_cb(self):
        self.send_lift_motor_reset_flag_ = False

    def lift_motor_send_to_small_cube_cb(self):
        self.send_lift_to_small_cube_pos_ = True
        self.start_timer('reset_lift_motor_send_to_small_cube_cb',1000)

    def reset_lift_motor_send_to_small_cube_cb(self):
        self.send_lift_to_small_cube_pos_ = False

    def lift_motor_send_to_ball_pos_cb(self):
        self.send_lift_to_ball_pos_ = True
        self.start_timer('reset_lift_motor_send_to_ball_cb',1000)

    def reset_lift_motor_send_to_ball_cb(self):
        self.send_lift_to_ball_pos_ = False
        
    def ice_door_reset_cb(self):
        self.send_ice_door_reset_flag_ = True
        self.start_timer('reset_ice_door_reset_cb',1000)

    def reset_ice_door_reset_cb(self):
        self.send_ice_door_reset_flag_ = False


    def ice_door_set_open_door_cb(self):
        self.send_ice_door_open_door_ = True
        self.start_timer('reset_ice_door_set_open_door_cb',1000)

    def reset_ice_door_set_open_door_cb(self):
        self.send_ice_door_open_door_ = False


    def ice_door_set_close_door_cb(self):
        self.send_ice_door_close_door_ = True
        self.start_timer('reset_ice_door_set_close_door_cb',1000)

    def reset_ice_door_set_close_door_cb(self):
        self.send_ice_door_close_door_ = False

    def put_down_ice_motor_cb(self,isChecked):
        self.send_put_down_ice_flag_ = True if isChecked else False

    """ 切换阀回调 """
    def ref_valve_reset_cb(self):
        self.send_ref_valve_reset_flag_ = True
        self.start_timer('reset_ref_valve_reset_cb',1000)
        
    def reset_ref_valve_reset_cb(self):
        self.send_ref_valve_reset_flag_ = False
        
        
    def ref_valve_to_make_cb(self):
        self.send_ref_valve_to_ice_make_ = True
        self.start_timer('reset_ref_valve_to_make_cb',1000)
      
    def reset_ref_valve_to_make_cb(self):
        self.send_ref_valve_to_ice_make_ = False  
        
    def ref_valve_to_store_cb(self):
        self.send_ref_valve_to_store_ = True
        self.start_timer('reset_ref_valve_to_store_cb',1000)
        
    def reset_ref_valve_to_store_cb(self):
        self.send_ref_valve_to_store_ = False  
        
    """ 风冷回调 """
    def store_fan_switch_cb(self, isChecked):
        self.send_store_fan_en_ = True if isChecked else False
        
    def store_heating_switch_cb(self, isChecked):
        self.send_store_heating_en_ = True if isChecked else False
        

    def moudle_init(self):
        """  初始化压缩机配置   """
        self.comprosser_en_button.setChecked(False)
        self.comprosser_en_button.checkedChanged.connect(self.comprosser_en_button_cb)
        self.comprosser_duty.setRange(0, 100)
        self.comprosser_duty.setValue(20)
        self.comprosser_duty_label.setText(str(self.comprosser_duty.value())+'%')
        self.comprosser_duty.valueChanged.connect(self.comprosser_duty_cb)

        """  初始化冷凝器配置   """
        self.condenser_en_button.setChecked(False)
        self.condenser_en_button.checkedChanged.connect(self.condenser_en_button_cb)
        self.condenser_duty.setRange(0, 100)
        self.condenser_duty.setValue(60)
        self.condenser_duty_label.setText(str(self.condenser_duty.value())+'%')
        self.condenser_duty.valueChanged.connect(self.condenser_duty_cb)

        """  初始化搅拌电机配置   """ 
        self.stir_motor_button.setChecked(False)
        self.stir_motor_button.checkedChanged.connect(self.stir_motor_en_button_cb)
        self.stir_motor_duty.setRange(0, 50)
        self.stir_motor_duty.setValue(25)
        self.stir_duty_label.setText(str(self.stir_motor_duty.value())+'%')
        self.stir_motor_duty.valueChanged.connect(self.stir_motor_duty_cb)


        """  初始化PI膜配置   """
        self.lift_pi_en_button.setChecked(False)
        self.lift_pi_en_button.checkedChanged.connect(self.lift_pi_en_button_cb)
        self.drop_pi_en_button.setChecked(False)
        self.drop_pi_en_button.checkedChanged.connect(self.drop_pi_en_button_cb)
        self.ball_pi_en_button.setChecked(False)
        self.ball_pi_en_button.checkedChanged.connect(self.ball_pi_en_button_cb)

        """  初始化水路配置   """
        self.from_tank_pump_button.setChecked(False)
        self.from_tank_pump_button.checkedChanged.connect(self.from_tank_pump_button_cb)
        self.to_tank_pump_button.setChecked(False)
        self.to_tank_pump_button.checkedChanged.connect(self.to_tank_pump_button_cb)

        """  初始抬升控制配置   """
        self.lift_motor_reset_button.setIcon(FIF.VPN)
        self.lift_motor_reset_button.clicked.connect(self.lift_motor_reset_cb)

        self.lift_motor_set_pos_val.setValidator(QIntValidator(0,100))
        self.lift_motor_set_pos_val.setPlaceholderText("输入升降位置，参考看旁边提示框")
        self.lift_motor_set_pos_val.returnPressed.connect(self.lift_motor_set_send_pos_cb)
        self.lift_motor_set_button.clicked.connect(self.lift_motor_set_send_pos_cb)

        self.to_big_cube_pos_button.setIcon(FIF.EMBED)
        self.to_big_cube_pos_button.clicked.connect(self.lift_motor_send_to_big_cube_cb)

        self.to_small_cube_pos_button.setIcon(FIF.EMBED)
        self.to_small_cube_pos_button.clicked.connect(self.lift_motor_send_to_small_cube_cb)

        self.to_ball_pos_button.setIcon(FIF.EMBED)
        self.to_ball_pos_button.clicked.connect(self.lift_motor_send_to_ball_pos_cb)

        """  初始冰门控制配置   """
        self.ice_door_reset_button.setIcon(FIF.VPN)
        self.ice_door_reset_button.clicked.connect(self.ice_door_reset_cb)

        self.open_door_button.clicked.connect(self.ice_door_set_open_door_cb)
        self.close_door_button.clicked.connect(self.ice_door_set_close_door_cb)

        self.put_down_line_button.setChecked(False)
        self.put_down_line_button.checkedChanged.connect(self.put_down_ice_motor_cb)

        """ 初始化切换阀 """
        self.ref_valve_reset_button.clicked.connect(self.ref_valve_reset_cb)
        self.ref_valve_to_make_button.clicked.connect(self.ref_valve_to_make_cb)
        self.ref_valve_to_store_button.clicked.connect(self.ref_valve_to_store_cb)

        """ 初始化风冷配件 """
        self.store_fan_switch.checkedChanged.connect(self.store_fan_switch_cb)
        self.store_heating_switch.checkedChanged.connect(self.store_heating_switch_cb)













        


        
        


