import socket
from SeaBattle import *


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 5000))
server.listen(1)


def show_pole(client):
    battle.show_poles()  # тут идет запись состояния поля в message.txt
    with open('message.txt', 'r') as file:
        data = ''.join(file.readlines()).encode()  # чтение из message.txt и формирование кодированной строки на отправку
        client.send(data)


battle = SeaBattle(10)
client, addr = server.accept()
try:
    show_pole(client)  # стартовая отправка поля
    client.recv(1024).decode('utf-8')  # прием отчета о принятии поля
    while not battle.win:
        if battle.human_turn:
            client.send('1'.encode())  # отправка кода чей ход
            client.recv(1024).decode('utf-8')  # прием результата получения кода
            coords = tuple(map(int, client.recv(1024).decode('utf-8').split()))  # прием координат хода человека
            right_coords = battle.human_move(coords)
            if not right_coords:
                client.send('0'.encode())  # отправка результата хода -
                client.recv(1024).decode('utf-8')  # прием отчета по результату -
                continue
            else:
                client.send('1'.encode())  # отправка результата хода +
                client.recv(1024).decode('utf-8')  # прием отчета по результату +
        else:
            client.send('0'.encode())  # отправка кода чей ход
            client.recv(1024).decode('utf-8')  # прием результата получения кода
            battle.computer_move()
        show_pole(client)
        client.recv(1024).decode('utf-8')  # прием отчета о принятии поля



except AttributeError as A:
    print(A)
    print(f'around = {battle.around}, along = {battle.along}, front = {battle.front}', sep='\n')
except KeyboardInterrupt:
    client.close()
    server.close()
