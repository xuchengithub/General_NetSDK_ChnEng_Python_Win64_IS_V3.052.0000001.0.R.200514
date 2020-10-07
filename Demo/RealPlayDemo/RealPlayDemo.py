# coding=utf-8
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from ctypes import *

from Demo.RealPlayDemo.RealPlayUI import Ui_MainWindow
from NetSDK.NetSDK import NetClient
from NetSDK.SDK_Callback import fDisConnect, fHaveReConnect
from NetSDK.SDK_Enum import SDK_RealPlayType, EM_LOGIN_SPAC_CAP_TYPE
from NetSDK.SDK_Struct import C_LLONG, NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY, NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)

        # 界面初始化
        self._init_ui()

        # NetSDK用到的相关变量和回调
        self.loginID = C_LLONG()
        self.playID = C_LLONG()
        self.m_DisConnectCallBack = fDisConnect(self.DisConnectCallBack)
        self.m_ReConnectCallBack = fHaveReConnect(self.ReConnectCallBack)

        # 获取NetSDK对象并初始化
        self.sdk = NetClient()
        self.sdk.InitEx(self.m_DisConnectCallBack)
        self.sdk.SetAutoReconnect(self.m_ReConnectCallBack)

    # 初始化界面
    def _init_ui(self):
        self.login_btn.setText('登录(Login)')
        self.play_btn.setText('监视(Play)')
        self.play_btn.setEnabled(False)

        self.IP_lineEdit.setText('172.23.8.94')
        self.Port_lineEdit.setText('37777')
        self.Name_lineEdit.setText('admin')
        self.Pwd_lineEdit.setText('admin123')

        self.setWindowFlag(Qt.WindowMinimizeButtonHint)
        self.setWindowFlag(Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())

        self.login_btn.clicked.connect(self.login_btn_onclick)
        self.play_btn.clicked.connect(self.play_btn_onclick)

    def login_btn_onclick(self):
        if not self.loginID:
            ip = self.IP_lineEdit.text()
            port = int(self.Port_lineEdit.text())
            username = self.Name_lineEdit.text()
            password = self.Pwd_lineEdit.text()

            stuInParam = NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY()
            stuInParam.dwSize = sizeof(NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY)
            stuInParam.szIP = ip.encode()
            stuInParam.nPort = port
            stuInParam.szUserName = username.encode()
            stuInParam.szPassword = password.encode()
            stuInParam.emSpecCap = EM_LOGIN_SPAC_CAP_TYPE.TCP
            stuInParam.pCapParam = None

            stuOutParam = NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY()
            stuOutParam.dwSize = sizeof(NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY)

            self.loginID, device_info, error_msg = self.sdk.LoginWithHighLevelSecurity(stuInParam, stuOutParam)
            if self.loginID != 0:
                self.setWindowTitle('实时监视(RealPlay)-在线(OnLine)')
                self.login_btn.setText('登出(Logout)')
                self.play_btn.setEnabled(True)
                self.play_btn.setText("监视(Play)")
                for i in range(int(device_info.nChanNum)):
                    self.Channel_comboBox.addItem(str(i))
                self.StreamTyp_comboBox.setEnabled(True)
            else:
                QMessageBox.about(self, '提示(prompt)', error_msg)
        else:
            if self.playID:
                self.sdk.StopRealPlayEx(self.playID)
                self.play_btn.setText("监视(Play)")
                self.playID = 0
                self.PlayWnd.repaint()

            result = self.sdk.Logout(self.loginID)
            if result:
                self.setWindowTitle("实时监视(RealPlay)-离线(OffLine)")
                self.login_btn.setText("登录(Login)")
                self.loginID = 0
                self.play_btn.setEnabled(False)
                self.StreamTyp_comboBox.setEnabled(False)
                self.Channel_comboBox.clear()

    def play_btn_onclick(self):
        if not self.playID:
            channel = self.Channel_comboBox.currentIndex()
            if self.StreamTyp_comboBox.currentIndex() == 0:
                stream_type = SDK_RealPlayType.Realplay
            else:
                stream_type = SDK_RealPlayType.Realplay_1
            self.playID = self.sdk.RealPlayEx(self.loginID, channel, self.PlayWnd.winId(), stream_type)
            if self.playID != 0:
                self.play_btn.setText("停止(Stop)")
                self.StreamTyp_comboBox.setEnabled(False)
            else:
                QMessageBox.about(self, '提示(prompt)', self.sdk.GetLastErrorMessage())
                pass
        else:
            result = self.sdk.StopRealPlayEx(self.playID)
            if result:
                self.play_btn.setText("监视(Play)")
                self.StreamTyp_comboBox.setEnabled(True)
                self.playID = 0
                self.PlayWnd.repaint()

    # 实现断线回调函数功能
    def DisConnectCallBack(self, lLoginID, pchDVRIP, nDVRPort, dwUser):
        self.setWindowTitle("实时监视(RealPlay)-离线(OffLine)")

    # 实现断线重连回调函数功能
    def ReConnectCallBack(self, lLoginID, pchDVRIP, nDVRPort, dwUser):
        self.setWindowTitle('实时监视(RealPlay)-在线(OnLine)')

    # 关闭主窗口时清理资源
    def closeEvent(self, event):
        event.accept()
        if  self.loginID:
            self.sdk.Logout(self.loginID)
        self.sdk.Cleanup()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_wnd = MyMainWindow()
    my_wnd.show()
    sys.exit(app.exec_())
