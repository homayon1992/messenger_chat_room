from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
from PyQt5.uic import loadUi
import sys
import rpyc
import socket
import threading

client = socket.socket()

def connect():
    client.connect(('localhost', 5051))
    while True:
        data = client.recv(1024)
        data = data.decode()
        if data.startswith("m:"):
            data = data[2:]
            main_panel.messageView.append(data+"\n")
        else:
            data = data[2:]
            data = eval(data)
            main_panel.userList.clear()
            main_panel.userList.addItems(data)

def send():
    message = main_panel.inputField.text()
    client.send(message.encode())
    main_panel.inputField.clear()

def login():
    username = login_panel.usernameField.text()
    password = login_panel.passwordField.text()
    result = server.login(username, password)
    if result == False:
        messageBox = QMessageBox()
        messageBox.setText('user or pass is not correct')
        messageBox.exec()
    else:
        login_panel.hide()
        main_panel.show()
        t1 = threading.Thread(target=connect)
        t1.start()

def register():
    # Check fields format
    name = register_panel.nameField.text()
    username = register_panel.usernameField.text()
    password = register_panel.passwordField.text()
    email = register_panel.emailField.text()
    result = server.register(name, username, password, email)
    i, okPressed = QInputDialog.getText(register_panel, "verification code" , "enter verification code")
    if okPressed:
        result = server.verify(username, i)
        info = "You Registered Successfully" if result == True else "Get Away"
        messageBox = QMessageBox()
        messageBox.setText(info)
        messageBox.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = rpyc.connect("localhost", 5050).root

    login_panel = loadUi("GUI/login.ui")
    register_panel = loadUi("GUI/register.ui")
    main_panel = loadUi("GUI/panel.ui")
    login_panel.show()
    login_panel.registerb.clicked.connect(lambda: register_panel.show())
    login_panel.loginb.clicked.connect(login)
    register_panel.registerb.clicked.connect(register)
    main_panel.sendb.clicked.connect(send)
    app.exec()