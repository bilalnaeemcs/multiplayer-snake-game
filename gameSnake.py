import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP
from random import randint

WIDTH = 100
HEIGHT = 20
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 5
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 100

class Snake(object):
    REV_DIR_MAP = {
        KEY_UP: KEY_DOWN, KEY_DOWN: KEY_UP,
        KEY_LEFT: KEY_RIGHT, KEY_RIGHT: KEY_LEFT,
    }

    def __init__(self, x, y, window):
        self.overload = False
        self.body_list = []
        self.hit_score = 0
        self.timeout = TIMEOUT

        for i in range(SNAKE_LENGTH, 0, -1):
            self.body_list.append(Body(x - i, y))

        self.body_list.append(Body(x, y, '0'))
        self.window = window
        self.direction = KEY_RIGHT
        self.last_head_coor = (x, y)
        self.direction_map = {
            KEY_UP: self.move_up,
            KEY_DOWN: self.move_down,
            KEY_LEFT: self.move_left,
            KEY_RIGHT: self.move_right
        }
    def setHead(self, x,y):
        self.body_list = [(x,y)]
    
    def setBodyList(self,bodylist):
        BodyArr = []
        for i in bodylist[:-1]:
            BodyArr.append(Body(i[0],i[1],'='))
        BodyArr.append(Body(bodylist[-1][0], bodylist[-1][1], '0'))
        self.body_list = BodyArr
    @property
    def score(self):
        return 'Score : {}'.format(self.hit_score)

    def add_body(self, body_list):
        self.body_list.extend(body_list)

    def eat_food(self, food):
        food.reset()
        body = Body(self.last_head_coor[0], self.last_head_coor[1])
        self.body_list.insert(-1, body)
        self.hit_score += 1
        if self.hit_score % 3 == 0:
            self.timeout -= 5
            self.window.timeout(self.timeout)

    @property
    def collided(self):
        return any([body.coor == self.head.coor
                    for body in self.body_list[:-1]])
    

    def update(self):
        last_body = self.body_list.pop(0)
        last_body.x = self.body_list[-1].x
        last_body.y = self.body_list[-1].y
        self.body_list.insert(-1, last_body)
        self.last_head_coor = (self.head.x, self.head.y)
        self.direction_map[self.direction]()

    def change_direction(self, direction):
        if direction != Snake.REV_DIR_MAP[self.direction]:
            self.direction = direction

    def render(self):
        for body in self.body_list:
            self.window.addstr(body.y, body.x, body.char,curses.color_pair(1))

    @property
    def head(self):
        return self.body_list[-1]

    def overloaded(self):
        return self.overload

    @property
    def coor(self):
        return self.head.x, self.head.y

    def move_up(self):
        self.head.y -= 1
        if self.head.y < 1:
            self.overload = True

    def move_down(self):
        self.head.y += 1
        if self.head.y > MAX_Y:
            self.overload = True
    def move_left(self):
        self.head.x -= 1
        if self.head.x < 1:
            self.overload = True

    def move_right(self):
        self.head.x += 1
        if self.head.x > MAX_X:
            self.overload = True
    @property
    def bodyCoor(self):
        return list(map(lambda item: (item.x, item.y) , self.body_list[:]))    

class Body(object):
    def __init__(self, x, y, char='='):
        self.x = x
        self.y = y
        self.char = char

    @property
    def coor(self):
        return self.x, self.y

class Food(object):
    def __init__(self, window, char='&'):
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)
        self.char = char
        self.window = window

    def render(self):
        self.window.addstr(self.y, self.x, self.char)

    def reset(self):
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)
