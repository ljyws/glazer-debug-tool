import sys
from PyQt5.QtWidgets import QApplication, QMainWindow  
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal, pyqtSlot
from resource.ui.Ui_controller import Ui_Form
from qfluentwidgets import setTheme, Theme, FluentTranslator

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()  # 创建主窗口实例
    ui = Ui_Form()  # 创建 UI 类的实例
    ui.setupUi(mainWindow)  # 使用 setupUi 方法加载 UI
    mainWindow.show()  # 显示窗口
    sys.exit(app.exec_()) 