from tkinter import *
from math import *
import tksvg
from svgwrite import *


class Vector:
    x, y = 0, 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def len2(self):
        return self.x ** 2 + self.y ** 2

    def len(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def norm(self, length):
        return Vector(self.x * length / self.len(), self.y * length / self.len())

    def turn(self, angle):
        cs = cos(angle)
        sn = sin(angle)
        return Vector(self.x * cs - self.y * sn, self.x * sn + self.y * cs)


def get_new_sizes(w, h):    # масштабирование к новым размерам, если вы изменили размер экрана
    return int(w * window_w / 1920), int(h * window_h / 1080)


window_w, window_h = 1920, 1080         # размеры экрана устройства
cnt_arrows = 10        # количество линий, исходящих из положительных зарядов
list_plus = []         # координаты положительных зарядов
list_minus = []        # координаты отрицательных зарядов
step_arrows = 40       # количество шагов построителя линий между двумя стрелками
canvas_size = get_new_sizes(1920 // 2, 1080 // 2)    # размеры поля с рисунком
circle_size = get_new_sizes(10, 10)[0]    # размеры изображений зарядов
dwg = Drawing(width=canvas_size[0], height=canvas_size[1])


def do_line(list_coords):
    for i in range(len(list_coords) - 5):   # каждый маленький участок рисуется как кубическая функция
        dwg.add(dwg.path(d='M{},{} C{},{}, {},{}, {},{}'.format(list_coords[i][0], list_coords[i][1],
                                                                list_coords[i + 1][0], list_coords[i + 1][1],
                                                                list_coords[i + 2][0], list_coords[i + 2][1],
                                                                list_coords[i + 3][0], list_coords[i + 3][1]),
                         stroke='black', stroke_width=2))


def draw_arrow(x, y):    # от точки рисую линию, пока она не выйдет за пределы экрана или войдёт в отрицательный заряд
    global dwg
    flag_in_circle = False
    list_coords = [(x, y)]
    while 0 < x < canvas_size[0] and 0 < y < canvas_size[1] and not flag_in_circle:
        v = Vector(0, 0)
        for el in list_plus:
            v = v + Vector(x - el[0], y - el[1]).norm(1 / Vector(x - el[0], y - el[1]).len2())
        for el in list_minus:
            if abs(x - el[0]) + abs(y - el[1]) <= circle_size * 1.5:
                flag_in_circle = True
            v = v + Vector(el[0] - x, el[1] - y).norm(1 / Vector(el[0] - x, el[1] - y).len2())
        v = v.norm(2)                # погрешность в пикселях при рисовании
        x += v.x
        y += v.y
        list_coords.append((x, y))
    do_line(list_coords)
    line_size = get_new_sizes(10, 10)[0]
    for i in range(step_arrows, len(list_coords) - step_arrows, step_arrows):    # рисование стрелок
        v = Vector(list_coords[i - 2][0] - list_coords[i][0], list_coords[i - 2][1] - list_coords[i][1])
        v1 = v.turn(pi / 4)
        v1 = v1.norm(line_size)
        dwg.add(dwg.path(d='M{},{} L{},{} Z'.format(int(list_coords[i][0]), int(list_coords[i][1]),
                                                    int(list_coords[i][0] + v1.x), int(list_coords[i][1] + v1.y)),
                         stroke='black', stroke_width=2))
        v2 = v.turn(-pi / 4)
        v2 = v2.norm(line_size)
        dwg.add(dwg.path(d='M{},{} L{},{} Z'.format(int(list_coords[i][0]), int(list_coords[i][1]),
                                                    int(list_coords[i][0] + v2.x), int(list_coords[i][1] + v2.y)),
                         stroke='black', stroke_width=2))


def draw():
    global dwg
    dwg = Drawing(width=canvas_size[0], height=canvas_size[1])
    dwg.add(dwg.path(d='M{},{} L{},{} Z'.format(0, 0,
                                                canvas_size[0], 0),
                     stroke='black', stroke_width=2))
    dwg.add(dwg.path(d='M{},{} L{},{} Z'.format(canvas_size[0], 0,
                                                canvas_size[0], canvas_size[1]),
                     stroke='black', stroke_width=2))
    dwg.add(dwg.path(d='M{},{} L{},{} Z'.format(canvas_size[0], canvas_size[1],
                                                0, canvas_size[1]),
                     stroke='black', stroke_width=2))
    dwg.add(dwg.path(d='M{},{} L{},{} Z'.format(0, canvas_size[1],
                                                0, 0),
                     stroke='black', stroke_width=2))
    for el in list_plus:
        angle = 0
        while angle < 2 * pi:    # нахожу все точки, от которых надо рисовать линии
            draw_arrow(el[0] + cos(angle) * circle_size, el[1] + sin(angle) * circle_size)
            angle += 2 * pi / cnt_arrows
    for el in list_plus:
        dwg.add(dwg.circle((el[0], el[1]), circle_size, fill='red'))
    for el in list_minus:
        dwg.add(dwg.circle((el[0], el[1]), circle_size, fill='blue'))
    dwg.saveas("pic.svg")

    svg_image = tksvg.SvgImage(file="pic.svg")
    global picture
    picture.configure(image=svg_image)
    picture.image = svg_image


def cnt_change(event):
    global cnt_arrows
    cnt_arrows = scale.get()
    draw()


def stop():
    list_plus.clear()
    list_minus.clear()
    draw()


def click_plus(event):
    list_plus.append((event.x, event.y))
    draw()


def click_minus(event):
    list_minus.append((event.x, event.y))
    draw()


def close_window(event):
    window.destroy()


window = Tk()
window.attributes('-fullscreen', True)

Label(window, text='Свет в конце тоннеля выключили из-за нехватки электричества.', font='Courier 30').pack()

button_size = get_new_sizes(30, 5)

pixelVirtual = PhotoImage(width=1, height=1)  # костыль, чтобы у кнопки размер можно было указать в пикселях, иначе никак

button_draw_size = get_new_sizes(1920 // 2, 50)
button_draw = Button(window,
                     text="Очистить",
                     font='Courier 30',
                     image=pixelVirtual,
                     width=button_draw_size[0],
                     height=button_draw_size[1],
                     compound="c",
                     command=stop)
button_draw.place(relx=0.2, rely=0.9)

scale_size = get_new_sizes(1920 // 2, 1080 // 2)
scale = Scale(window,
              from_=5,
              to=15,
              length=scale_size[1],
              font='Courier 30',
              command=cnt_change)
scale.place(relx=0.1, rely=0.1)

picture = Label(window,
                image=pixelVirtual,
                width=canvas_size[0],
                height=canvas_size[1])
picture.place(relx=0.2, rely=0.1)

picture.bind('<Button-1>', click_plus)
picture.bind('<Button-3>', click_minus)
window.bind('<Escape>', close_window)

window.mainloop()
