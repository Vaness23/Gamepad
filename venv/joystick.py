import pygame

pygame.init()
size = [500, 700]
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

done = False

while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # pygame.joystick.init()  # инициализация джойстика
    # pygame.joystick.get_init()  # возвращает 1, если джойстик инициализирован
    # pygame.joystick.get_count()  # возвращает количество джойстиков
    # pygame.joystick.quit()  # отключает джойстик (uninitialize)

    pygame.joystick.init()

    if pygame.joystick.get_init() == 1 and pygame.joystick.get_count() > 0:
        print("Number of connected joysticks:", pygame.joystick.get_count())
    else:
        print("Joystick is uninitialized or not connected")
        exit(1)

    joystick = pygame.joystick.Joystick(0)  # создаем новый объект joystick с id = 0
    joystick.init()  # инициализация джойстика
    print("Joystick system name:", joystick.get_name())  # имя джойстика
    print("Number of axes:", joystick.get_numaxes())  # количество осей

    # <-- ОСИ ДЖОЙСТИКА -->
    # 0 - вправо / влево
    # 1 - вперед / назад
    # 2 - ???
    # 3 - throttle
    # 4 - поворот

    print("X axis:{:>6.3f}".format(joystick.get_axis(0)))
    print("Y axis:{:>6.3f}".format(joystick.get_axis(1)))
    print("??? axis:{:>6.3f}".format(joystick.get_axis(2)))
    print("Throttle:{:>6.3f}".format(joystick.get_axis(3)))
    print("Z axis:{:>6.3f}".format(joystick.get_axis(4)))

    print("Number of buttons:", joystick.get_numbuttons())
    for i in range(joystick.get_numbuttons()):
        print("Button ", i+1, ": ", joystick.get_button(i), sep='')

    print("Number of hats:", joystick.get_numhats())
    print("Hat value:", joystick.get_hat(0))

    pygame.display.flip()

    clock.tick(20)

    # done = True

pygame.quit()
