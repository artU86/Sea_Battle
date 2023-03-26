import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5000))

pole = client.recv(1024).decode('utf-8')  # стартовый прием поля и вывод на печать
client.send('pole accepted'.encode())  # отчет о принятии поля
print('                    Start Game', end='\n\n')
print(pole)

mtx = (' '.join((str(i), str(j))) for i in range(10) for j in range(10))

try:
    while True:
        code = int(client.recv(1024).decode('utf-8'))  # прием кода чей ход
        client.send('code accepted on client'.encode())  # отчет о приеме кода
        if code:
            #coords = input().encode()
            coords = next(mtx).encode()  #мок для тестов, не всегда корректно работает
            client.send(coords)  # отправка координат хода человека
            answer = int(client.recv(1024).decode('utf-8'))  # прием результата хода человека
            if not answer:
                client.send('not right coords'.encode())  # отчет о приеме результата хода -
                print("В эту клетку нельзя бить, выберите другую")
                continue  # возврат к приему кода чей ход
            client.send('right coords'.encode())  # отчет о приеме результата хода +
        pole = client.recv(1024).decode('utf-8')  # прием состояния поля
        client.send('pole accepted'.encode())  # отчет о принятии поля
        print(pole)
except KeyboardInterrupt:
    client.close()
except ValueError:
    print('                    game over')
    client.close()


#TODO при работе функции find_along когда доходит до края поля и разворачивается назад - на 15 строке обрабатывается пустая строка и прерывается исполнение кода