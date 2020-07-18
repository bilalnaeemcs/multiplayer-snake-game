import socket
import time
import sys
import _thread
import json
from gameSnake import * 


WIDTH = 100
HEIGHT = 20
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 5
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 100


countWin = 0
address = sys.argv[1]
s = socket.socket()
port = int(sys.argv[2])
start = time.time()
s.bind((address, port))
s.listen()
numberOfPlayers = int(sys.argv[3])
canWin = False

snakes = {}

def dealWithConnection(connection, address, window, count):
    global countWin
    global snakes
    global numberOfPlayers
    lost = False
    counter = 0
    data = connection.recv(1024)
    dataJson = json.loads(data)
    for i in snakes:
        counter = counter+1
    if 'purpose' in dataJson:
        if dataJson['purpose'] == 'StartCon' and counter < numberOfPlayers:
            if 'name' not in dataJson:
                response = {
                    "name": count,
                    'server' : 'not_full'
                }
                countWin = countWin + 1;
                connection.send(json.dumps(response).encode())
                snakes[count] = Snake(randint(SNAKE_LENGTH+1,MAX_X),randint(1,MAX_Y),window)
            else: 
                connection.send("\{\"error\":\"Protocol Error: Unkown Message\"\}")
        elif counter>=numberOfPlayers:
            response = {
                'server': 'full'
            }
            connection.send(json.dumps(response).encode())
        elif dataJson['purpose'] == 'ScreenInit':
            clientName = dataJson['name']
            response = {}
            for i in snakes.keys():
                response[i] = snakes[i].bodyCoor
            connection.send(json.dumps(response).encode())
            window.clear()
            window.border(0)
            for i in snakes.keys():
                snakes[i].render()
            eventServ = window.getch()
        elif dataJson['purpose'] == 'SnakeDir':
            event = dataJson['event']
            clientName = dataJson['name']
            if clientName not in snakes.keys():
                response = {
                    'game' : 'end'
                }
                connection.send(json.dumps(response).encode())
                connection.close()
                window.clear()
                window.border(0)
                window.getch()
                return
            if event in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
                snakes[clientName].change_direction(event)
            marker = False
            marked  = False
            keyList = []
            for i in snakes.keys():
                marker = False
                snakes[i].update()
                if snakes[i].overloaded() or snakes[i].collided:
                    marker = True
                if marker and i not in keyList:
                    keyList.append(i)
                if marker and counter == 1:
                    marked = True
            for i in keyList:
                snakes.pop(i)
            if marked:
                countWin = 0
                response = {
                    'game' : 'end'
                }
                connection.send(json.dumps(response).encode())
                connection.close()
                window.clear()
                window.border(0)
                window.getch()
                return

            keyList = []
            marker = False
            if clientName in snakes:
                tempName = clientName
                for j in snakes.keys():
                    clientHeadCoor = snakes[j].coor
                    for i in snakes.keys():
                        Coor = snakes[j].bodyCoor
                        if snakes[i].coor[0]==clientHeadCoor[0] and snakes[i].coor[1]==clientHeadCoor[1] and snakes[i].bodyCoor[:-1] != Coor[:-1] :
                            if i not in keyList:
                                keyList.append(i)
                            if j not in keyList:
                                keyList.append(j)
                        elif clientHeadCoor in snakes[i].bodyCoor[:-1]:
                            if i not in keyList:
                                keyList.append(i)
                for i in keyList:
                    snakes.pop(i)
            response = {}
            for i in snakes.keys():
                response[i] = snakes[i].bodyCoor
            if counter == 1 and countWin > 1: 
                response['game'] = 'win'
                snakes = {}
                countWin = 0
            else:
                response['game'] = 'continue'
            connection.send(json.dumps(response).encode())
            window.clear()
            window.border(0)
            window.addstr(0, 0, "Server::> ",curses.A_REVERSE)
            for i in snakes.keys():
                snakes[i].render()
            eventServ = window.getch()
            
    connection.close()
def main():
    curses.initscr()
    curses.start_color()
    curses.init_pair(1, 1, 7)
    curses.beep() 
    curses.beep()
    window = curses.newwin(HEIGHT, WIDTH, 0, 0)
    window.timeout(TIMEOUT)
    window.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    window.border(0)
    window.addstr(0, 0, "Server::> ",curses.A_REVERSE)
    count = 0
    while True:
        gap = time.time() - start
        c, addr = s.accept()
        _thread.start_new_thread(dealWithConnection,(c,addr,window,count))
        count = count +1 
    curses.endwin()

if __name__ == "__main__":
    main()  
