import rpyc
import rpyc.utils.server as server
import pymysql
import random
import smtplib
import traceback
import socket
import threading
online_users = []
socket_list = []

def listen(client_socket):
    index = socket_list.index(client_socket)
    user = online_users[index]
    while True:
        data = client_socket.recv(1024)
        data = data.decode()
        data = 'm:<b>' + user + ":</b> "+data
        data = data.encode()
        for client in socket_list:
            client.send(data)


def send_online_users():
    data = str(online_users)
    data = 'u:'+data
    data = data.encode()
    for client in socket_list:
        client.send(data)

def start_server_socket():
    server_socket = socket.socket()
    server_socket.bind(('localhost', 5051))
    server_socket.listen(50)
    while True:
        client_socket, ip = server_socket.accept()
        socket_list.append(client_socket)
        send_online_users()
        st = threading.Thread(target=listen, args=(client_socket,))
        st.start()
class ServerService(rpyc.Service):

    def exposed_register(self, name, username, password, email):
        sql = "insert into users values(%s, %s, %s, %s, 0)"
        sql2 = "insert into tokens values(%s, %s)"
        try:
            # TODO check username before registration
            cursor.execute(sql, (name, username, password, email))
            verification_code = random.randint(1000, 9999)
            cursor.execute(sql2, (username, str(verification_code)))
            self.send_mail(email, verification_code)
            connection.commit()
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            connection.rollback()
            return False
        else:
            return True

    def exposed_verify(self, username, code):
        sql = "select verificationcode from tokens where username=%s"
        sql2 = "update users set enabled=1 where username=%s"
        try:
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if len(result)>0 and result[0] == code:
                cursor.execute(sql2, (username,))
                connection.commit()
                return True
            else:
                return False
        except:
            connection.rollback()
            return False

    def exposed_login(self, username, password):
        sql = "select * from users where username=%s and password=%s and enabled=1"
        try:
            cursor.execute(sql, (username,password))
            result = cursor.fetchall()
            if len(result) >0:
                online_users.append(username)
                return True
        except:
            pass
        return False

    def send_mail(self, email, verification_code):
        mail_server.sendmail("hamed.developer666@gmail.com", email, 'your verification code is {}'.format(verification_code))

if __name__ == '__main__':
    connection = pymysql.connect(host="localhost", user="homauon", password="12345", db="masenjer")
    cursor = connection.cursor()

    mail_server = smtplib.SMTP('smtp.gmail.com', 587)
    mail_server.starttls()
    mail_server.login('hamed.developer666@gmail.com', '12qwaszx!@')
    t1 = threading.Thread(target=start_server_socket)
    t1.start()
    server = server.ThreadedServer(ServerService, port=5050)
    server.start()
