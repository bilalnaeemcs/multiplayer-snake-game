import socket
import json
from gameSnake import *
import curses
import sys

WIDTH = 100
HEIGHT = 20
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 5
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 100
def connectionHandler(snake):
    pass


def main():
    name = ""
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
    s = socket.socket()
    port = int(sys.argv[2])
    address = sys.argv[1]
    result = '   You Have Lost   '

    #connecting for identifying the name of the player
    s.connect((address, port))
    gameStart = {
        "purpose" : "StartCon"
    }
    s.send(json.dumps(gameStart).encode())
    data = s.recv(1024)
    dataJson = json.loads(data)
    if dataJson['server'] == 'full':
        curses.endwin()
        return
    if 'name' in dataJson:
        name = dataJson['name']
    s.close()

    #connecting for getting the coordinates of the snake playes
    s=socket.socket()
    s.connect((address, port))
    getSnake = {
        "purpose": 'ScreenInit',
        "name": name
    }    
    s.send(json.dumps(getSnake).encode())
    dataInit = s.recv(1024)
    while True:
        data = s.recv(1024)
        dataInit = dataInit + data
        if(not data):
            break
    coorJson = json.loads(dataInit)
    s.close()
    window.clear()
    window.border(0)
    window.addstr(0, 0, f"Player ID : {name}",curses.A_REVERSE)
    snakes = {} #list of all the current snakes
    for i in coorJson.keys():
        snakes[i] = Snake(3,3,window)
        snakes[i].setBodyList(coorJson[i])
        snakes[i].render()
    event = window.getch()
    while True:
        s=socket.socket()
        #connection for continuosly sending the directions to the server
        s.connect((address, port))
        giveDir = {
            'purpose' : 'SnakeDir',
            'name' : name,
            'event' : event,
        }
        s.send(json.dumps(giveDir).encode()) 
        dataInit = s.recv(1024)
        while True:
            data = s.recv(1024)
            dataInit = dataInit + data
            if(not data):
                break
        coorJson = json.loads(dataInit)
        if(coorJson['game'] == 'end'):
            break
        elif coorJson['game'] == 'win' :
            result = '    You Have Won    '
            break
        coorJson.pop('game')
        s.close()
        window.clear()
        window.border(0)
        window.addstr(0, 0, f"Player ID : {name}",curses.A_REVERSE)
        snakes = {} #list of all the current snakes
        for i in coorJson.keys():
            snakes[i] = Snake(3,3,window)
            snakes[i].setBodyList(coorJson[i])
            snakes[i].render()
        event = window.getch()

    window.clear()
    window.border(0)
    window.addstr(0, 0, f"Player ID : {name}",curses.A_REVERSE)
    window.addstr(int(HEIGHT/2),int(WIDTH/2), result,curses.A_STANDOUT)
    window.addstr(int(HEIGHT/2 + 1),int(WIDTH/2-2), "Press Space to Continue!",curses.A_BLINK)    
    key = 0
    while key != 32:
        key = window.getch()       
    curses.endwin()
    


if __name__ == "__main__":
    main()