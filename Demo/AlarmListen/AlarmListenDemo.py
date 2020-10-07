# import sys 
# sys.path.append("../../..") 
import os
os.chdir("C:\\Users\\Administrator\\Desktop\\General_NetSDK_ChnEng_Python_Win64_IS_V3.052.0000001.0.R.200514")

import sys
sys.path.append("C:\\Users\\Administrator\\Desktop\\General_NetSDK_ChnEng_Python_Win64_IS_V3.052.0000001.0.R.200514")
# os.chdir()
# os.chdir("C:\Users\Administrator\Desktop\General_NetSDK_ChnEng_Python_Win64_IS_V3.052.0000001.0.R.200514")
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QHeaderView, QAbstractItemView, QApplication, QGroupBox, QMenu,QTableWidgetItem
from PyQt5.QtCore import Qt
import types
from AlarmListenUI import Ui_MainWindow

from NetSDK.NetSDK import NetClient
from NetSDK.SDK_Struct import *
from NetSDK.SDK_Enum import *
from NetSDK.SDK_Callback import fDisConnect, fHaveReConnect,fMessCallBackEx1

global hwnd
@WINFUNCTYPE(None, c_long, C_LLONG, POINTER(c_char), C_DWORD, POINTER(c_char), c_long, c_int, c_long, C_LDWORD)
def MessCallback(lCommand, lLoginID, pBuf, dwBufLen ,pchDVRIP, nDVRPort, bAlarmAckFlag, nEventID, dwUser):
    if(lLoginID != hwnd.loginID):
        return
    if(lCommand == SDK_ALARM_TYPE.EVENT_MOTIONDETECT):
        print('Enter MessCallback')
        buf = cast(pBuf, POINTER(ALARM_MOTIONDETECT_INFO)).contents
        hwnd.update_buf(buf)
        hwnd.update_ui()

class StartListenWnd(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(StartListenWnd, self).__init__()
        self.setupUi(self)
        # 界面初始化
        self.init_ui()

        # NetSDK用到的相关变量和回调
        self.loginID = C_LLONG()
        self.m_DisConnectCallBack = fDisConnect(self.DisConnectCallBack)
        self.m_ReConnectCallBack = fHaveReConnect(self.ReConnectCallBack)

        # 获取NetSDK对象并初始化
        self.sdk = NetClient()
        self.sdk.InitEx(self.m_DisConnectCallBack)
        self.sdk.SetAutoReconnect(self.m_ReConnectCallBack)

        #设置报警回调函数
        self.sdk.SetDVRMessCallBackEx1(MessCallback,0)


    def init_ui(self):
        self.IP_lineEdit.setText('192.168.12.108')
        self.Port_lineEdit.setText('37777')
        self.Username_lineEdit.setText('admin')
        self.Password_lineEdit.setText('smartCare108')
        self.Login_pushButton.clicked.connect(self.login_btn_onclick)
        self.Logout_pushButton.clicked.connect(self.logout_btn_onclick)

        self.Alarmlisten_pushButton.clicked.connect(self.attach_btn_onclick)
        self.Stopalarmlisten_pushButton.clicked.connect(self.detach_btn_onclick)
        self.Login_pushButton.setEnabled(True)
        self.Logout_pushButton.setEnabled(False)
        self.Alarmlisten_pushButton.setEnabled(False)
        self.Stopalarmlisten_pushButton.setEnabled(False)
        self.row = 0
        self.column = 0

    def login_btn_onclick(self):
        self.Alarmlisten_tableWidget.setHorizontalHeaderLabels(['序号(No.)', '时间（Time)', '通道(Channel)', '报警类型(Alarm Type)', '状态(Status)'])
        ip = self.IP_lineEdit.text()
        port = int(self.Port_lineEdit.text())
        username = self.Username_lineEdit.text()
        password = self.Password_lineEdit.text()
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
            self.setWindowTitle('报警监听(AlarmListen)-在线(OnLine)')
            self.Login_pushButton.setEnabled(False)
            self.Logout_pushButton.setEnabled(True)
            if (int(device_info.nChanNum) > 0):
                self.Alarmlisten_pushButton.setEnabled(True)
        else:
            QMessageBox.about(self, '提示(prompt)', error_msg)

    def logout_btn_onclick(self):
        # 登出
        if (self.loginID == 0):
            return
        # 停止报警监听
        self.sdk.StopListen(self.loginID)
        #登出
        result = self.sdk.Logout(self.loginID)
        self.Login_pushButton.setEnabled(True)
        self.Logout_pushButton.setEnabled(False)
        self.Alarmlisten_pushButton.setEnabled(False)
        self.Stopalarmlisten_pushButton.setEnabled(False)
        self.setWindowTitle("报警监听(AlarmListen)-离线(OffLine)")
        self.loginID = 0
        self.row = 0
        self.column = 0
        self.Alarmlisten_tableWidget.clear()
        self.Alarmlisten_tableWidget.setHorizontalHeaderLabels(['序号(No.)', '时间（Time)', '通道(Channel)', '报警类型(Alarm Type)', '状态(Status)'])

    def attach_btn_onclick(self):
        self.row = 0
        self.column = 0
        self.Alarmlisten_tableWidget.clear()
        self.Alarmlisten_tableWidget.setHorizontalHeaderLabels(['序号(No.)', '时间（Time)', '通道(Channel)', '报警类型(Alarm Type)', '状态(Status)'])
        result = self.sdk.StartListenEx(self.loginID)
        if result:
            QMessageBox.about(self, '提示(prompt)', "报警监听成功(Subscribe alarm success)")
            self.Stopalarmlisten_pushButton.setEnabled(True)
            self.Alarmlisten_pushButton.setEnabled(False)
        else:
            QMessageBox.about(self, '提示(prompt)', 'error:' + str(self.sdk.GetLastError()))

    def detach_btn_onclick(self):
        if (self.loginID > 0):
            self.sdk.StopListen(self.loginID)
        self.Stopalarmlisten_pushButton.setEnabled(False)
        self.Alarmlisten_pushButton.setEnabled(True)

    # 关闭主窗口时清理资源
    def closeEvent(self, event):
        event.accept()
        if self.loginID:
            self.sdk.StopListen(self.loginID)
            self.sdk.Logout(self.loginID)
            self.loginID = 0
        self.sdk.Cleanup()

    def update_buf(self, buf):
        self.buf = buf

    def update_ui(self):
        self.Alarmlisten_tableWidget.setRowCount(self.row + 1)
        item = QTableWidgetItem(str(self.row + 1))
        self.Alarmlisten_tableWidget.setItem(self.row, self.column, item)
        item1 = QTableWidgetItem('{0}-{1}-{2} {3}:{4}:{5}'.format(str(self.buf.UTC.dwYear), str(self.buf.UTC.dwMonth),
                                                                  str(self.buf.UTC.dwDay),
                                                                  str(self.buf.UTC.dwHour), str(self.buf.UTC.dwMinute),
                                                                  str(self.buf.UTC.dwSecond)))
        self.Alarmlisten_tableWidget.setItem(self.row, self.column + 1, item1)
        item2 = QTableWidgetItem(str(self.buf.nChannelID))
        self.Alarmlisten_tableWidget.setItem(self.row, self.column + 2, item2)
        item3 = QTableWidgetItem('动检事件（VideoMotion event)')
        self.Alarmlisten_tableWidget.setItem(self.row, self.column + 3, item3)
        if(self.buf.nEventAction == 0):
            item4 = QTableWidgetItem('脉冲(Pulse)')
            self.Alarmlisten_tableWidget.setItem(self.row, self.column + 4, item4)
        elif(self.buf.nEventAction == 1):
            item4 = QTableWidgetItem('开始(Start)')
            self.Alarmlisten_tableWidget.setItem(self.row, self.column + 4, item4)
        elif(self.buf.nEventAction == 2):
            item4 = QTableWidgetItem('结束(Stop)')
            self.Alarmlisten_tableWidget.setItem(self.row, self.column + 4, item4)
        self.row += 1
        self.Alarmlisten_tableWidget.update()
        self.Alarmlisten_tableWidget.viewport().update()

    # 实现断线回调函数功能
    def DisConnectCallBack(self, lLoginID, pchDVRIP, nDVRPort, dwUser):
        self.setWindowTitle("报警监听(AlarmListen)-离线(OffLine)")

    # 实现断线重连回调函数功能
    def ReConnectCallBack(self, lLoginID, pchDVRIP, nDVRPort, dwUser):
        self.setWindowTitle('报警监听(AlarmListen)-在线(OnLine)')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = StartListenWnd()
    hwnd = wnd
    wnd.show()
    sys.exit(app.exec_())
