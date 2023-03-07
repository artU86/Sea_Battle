import socket
from SeaBattle import *


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 5000))
server.listen(1)

battle = SeaBattle(10)
try:
    battle.show_poles()
    # TODO дописать чтение из файла и отправку на клиент
    while not battle.win:

        if battle.human_turn:
            battle.human_move()

        else:
            battle.computer_move()

        battle.show_poles()
except AttributeError:
    print(f'around = {battle.around}, along = {battle.along}, front = {battle.front}', sep='\n')
