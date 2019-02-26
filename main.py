import sys  # нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
import design
import pygame
from onvif import ONVIFCamera, ONVIFService, ONVIFError
from time import sleep
import datetime
import zeep
X_AXIS = 0
Y_AXIS = 1
THR_AXIS = 2
Z_AXIS = 3


def zeep_pythonvalue(self, xmlvalue):  # нужно для корректной работы камеры
    return xmlvalue


class Application(QtWidgets.QMainWindow, design.Ui_MainWindow):

    connected = True
    focusMode = False

    def __init__(self):
        # для доступа к переменным, методам и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # для инициализации дизайна
        self.done = False
        self.connectBtn.clicked.connect(self.connect)
        self.disconnectBtn.clicked.connect(self.disconnect_camera)

    def disconnect_camera(self):
        self.done = True
        self.add_log("Camera is disconnected")

    def add_log(self, log):
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        now = str(now)
        self.listWidget.addItem(now + " - " + log)

    def connect(self):
        self.add_log("Connecting...")
        ip, port, login, password, length = open_config()
        num = self.comboBox.currentIndex()
        self.add_log("IP: " + ip[num])
        self.add_log("Port: " + str(port[num]))
        self.add_log("Login: " + login[num])
        self.add_log("Password: " + password[num])

        # подключение джойстика
        pygame.init()
        if pygame.joystick.get_init() == 1 and pygame.joystick.get_count() > 0:
            self.add_log("Joystick is connected")
            self.add_log("Number of connected joysticks: " + str(pygame.joystick.get_count()))
        else:
            self.add_log("Joystick is uninitialized or not connected")
            return

        try:
            joystick = pygame.joystick.Joystick(0)  # создаем новый объект joystick с id = 0
        except pygame.error:
            self.add_log("Joystick is uninitialized or not connected")
            pygame.close()
            return

        joystick.init()  # инициализация джойстика
        self.add_log("Joystick system name: " + joystick.get_name())  # вывод имени джойстика

        mycam = None
        attempts = 3
        while mycam is None:
            self.add_log("Connecting to the camera...")
            try:
                mycam = ONVIFCamera(ip[num], port[num], login[num], password[num])  # инициализация камеры
            except ONVIFError:
                self.add_log("Connection failed")
            attempts -= 1
            if attempts == 0:
                del mycam
                pygame.quit()
                return

        self.add_log("Camera is connected")
        self.connectBtn.setDisabled(True)
        self.disconnectBtn.setEnabled(True)

        media = mycam.create_media_service()  # создание media service
        ptz = mycam.create_ptz_service()  # создание ptz service
        image = mycam.create_imaging_service()  # создание imaging service

        media_profile = media.GetProfiles()[0]  # достаем медиа-профиль камеры

        # достаем ptz configuration options
        request = ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = ptz.GetConfigurationOptions(request)
        ptz_configurations_list = ptz.GetConfigurations()
        ptz_configuration = ptz_configurations_list[0]

        # создание запроса continuous move для настройки движения камеры
        request = ptz.create_type('ContinuousMove')
        request.ProfileToken = media_profile.token
        request.Velocity = media_profile.PTZConfiguration.DefaultPTZSpeed  # поиск структуры Velocity
        # преобразование структуры Velocity
        request.Velocity.Zoom.x = 0.0
        request.Velocity.PanTilt.space = ''
        request.Velocity.Zoom.space = ''
        ptz.Stop({'ProfileToken': media_profile.token})  # остановка камеры на случай, если она двигалась

        # создание запроса set preset для сохранения пресетов камеры
        prequest = ptz.create_type('SetPreset')
        prequest.ProfileToken = media_profile.token

        # создание запроса go to preset для перехода между пресетами камеры
        grequest = ptz.create_type('GotoPreset')
        grequest.ProfileToken = media_profile.token

        # создание запроса set configuration для настройки скорости движения камеры
        srequest = ptz.create_type('SetConfiguration')

        # создание запроса set imaging settings для настройки изображения с камеры
        irequest = image.create_type('SetImagingSettings')
        video_token = media.GetVideoSourceConfigurationOptions().VideoSourceTokensAvailable[0]
        img_settings = image.GetImagingSettings(video_token)

        global XMAX, XMIN, YMAX, YMIN, ZMAX, ZMIN

        # получение числового диапазона осей X, Y, Z
        XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
        ZMAX = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Max
        ZMIN = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Min

        # self.add_log("XMAX: " + str(XMAX))
        # self.add_log("XMIN: " + str(XMIN))
        # self.add_log("YMAX: " + str(YMAX))
        # self.add_log("YMIN: " + str(YMIN))
        # self.add_log("ZMAX: " + str(ZMAX))
        # self.add_log("ZMIN: " + str(ZMIN))

        s = -1
        while s < 1:
        	print("%2g maps to %g" % (s, maprange((-1, 1), (XMIN, XMAX), s)))
        	s += 0.1

        global throttle

        isMoving = False
        OX = False
        OY = False
        OZ = False

        self.done = False

        while not self.done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True

            throttle = (-(joystick.get_axis(THR_AXIS))) / 2 + 0.5

            ptz_configuration.DefaultPTZSpeed.PanTilt.x = throttle * XMAX
            ptz_configuration.DefaultPTZSpeed.PanTilt.y = throttle * YMAX
            ptz_configuration.DefaultPTZSpeed.Zoom.x = throttle * ZMAX

            srequest.PTZConfiguration = ptz_configuration
            srequest.ForcePersistence = False

            ptz.SetConfiguration(srequest)

            grequest.Speed = ptz_configuration.DefaultPTZSpeed
            grequest.Speed.PanTilt.x = throttle
            grequest.Speed.PanTilt.y = throttle
            grequest.Speed.Zoom.x = throttle

            irequest.VideoSourceToken = video_token
            irequest.ImagingSettings = img_settings
            irequest.ForcePersistence = False

            if joystick.get_axis(X_AXIS) > 0.1 or joystick.get_axis(X_AXIS) < -0.1:
                move_horizontal(ptz, request, joystick)
                print(str(maprange((-1, 1), (XMIN, XMAX), joystick.get_axis(X_AXIS))))
                isMoving = True
                OX = True

            if joystick.get_axis(Y_AXIS) > 0.2 or joystick.get_axis(Y_AXIS) < -0.2:
                move_vertical(ptz, request, joystick)
                print(str(maprange((-1, 1), (YMIN, YMAX), joystick.get_axis(Y_AXIS))))
                isMoving = True
                OY = True

            if joystick.get_axis(Z_AXIS) > 0.3 or joystick.get_axis(Z_AXIS) < -0.3:
                zoom(ptz, request, joystick)
                print(str(maprange((-1, 1), (ZMIN, ZMAX), joystick.get_axis(Z_AXIS))))
                isMoving = True
                OZ = True

            if isMoving:

                if -0.1 <= joystick.get_axis(X_AXIS) <= 0.1 and OX:
                    ptz.Stop({'ProfileToken': request.ProfileToken})
                    isMoving = False
                    OX = False

                if -0.1 <= joystick.get_axis(Y_AXIS) <= 0.2 and OY:
                    ptz.Stop({'ProfileToken': request.ProfileToken})
                    isMoving = False
                    OY = False

                if -0.1 <= joystick.get_axis(Z_AXIS) <= 0.3 and OZ:
                    ptz.Stop({'ProfileToken': request.ProfileToken})
                    isMoving = False
                    OZ = False

            ptz = mycam.create_ptz_service()

            if joystick.get_button(1) == 1:
                if self.focusMode:
                    self.focusMode = False
                    self.add_log("Entering Brightness / Contrast mode...")
                else:
                    self.focusMode = True
                    self.add_log("Entering Focus mode...")

            if joystick.get_button(1) == 1:

                if joystick.get_button(6) == 1:
                    prequest.PresetName = "7"
                    prequest.PresetToken = '7'
                    preset = ptz.SetPreset(prequest)
                    self.add_log("Setting preset #7...")

                if joystick.get_button(7) == 1:
                    prequest.PresetName = "8"
                    prequest.PresetToken = '8'
                    preset = ptz.SetPreset(prequest)
                    self.add_log("Setting preset #8...")

                if joystick.get_button(8) == 1:
                    prequest.PresetName = "9"
                    prequest.PresetToken = '9'
                    preset = ptz.SetPreset(prequest)
                    self.add_log("Setting preset #9...")

                if joystick.get_button(9) == 1:
                    prequest.PresetName = "10"
                    prequest.PresetToken = '10'
                    preset = ptz.SetPreset(prequest)
                    self.add_log("Setting preset #10...")

                if joystick.get_button(10) == 1:
                    prequest.PresetName = "11"
                    prequest.PresetToken = '11'
                    preset = ptz.SetPreset(prequest)
                    self.add_log("Setting preset #11...")

                if joystick.get_button(11) == 1:
                    prequest.PresetName = "12"
                    prequest.PresetToken = '12'
                    preset = ptz.SetPreset(prequest)
                    self.add_log("Setting preset #12...")

            if joystick.get_button(6) == 1:
                grequest.PresetToken = '7'
                ptz.GotoPreset(grequest)
                self.add_log("Going to preset #7...")

            if joystick.get_button(7) == 1:
                grequest.PresetToken = '8'
                ptz.GotoPreset(grequest)
                self.add_log("Going to preset #8...")

            if joystick.get_button(8) == 1:
                grequest.PresetToken = '9'
                ptz.GotoPreset(grequest)
                self.add_log("Going to preset #9...")

            if joystick.get_button(9) == 1:
                grequest.PresetToken = '10'
                ptz.GotoPreset(grequest)
                self.add_log("Going to preset #10...")

            if joystick.get_button(10) == 1:
                grequest.PresetToken = '11'
                ptz.GotoPreset(grequest)
                self.add_log("Going to preset #11...")

            if joystick.get_button(11) == 1:
                grequest.PresetToken = '12'
                ptz.GotoPreset(grequest)
                self.add_log("Going to preset #12...")

            # настройка изображения

            if not self.focusMode:
                # увеличение яркости (6 кнопка)
                if joystick.get_button(5) == 1:
                    if img_settings.Brightness < 10:
                        img_settings.Brightness += 1
                        if img_settings.Brightness > 10:
                            img_settings.Brightness = 10
                    image.SetImagingSettings(irequest)
                    self.add_log("Increasing brightness to " + str(img_settings.Brightness) + "...")

                # уменьшение яркости (4 кнопка)
                if joystick.get_button(3) == 1:
                    if img_settings.Brightness > 0:
                        img_settings.Brightness -= 1
                        if img_settings.Brightness < 0:
                            img_settings.Brightness = 0
                    image.SetImagingSettings(irequest)
                    self.add_log("Reducing brightness to " + str(img_settings.Brightness) + "...")

                # увеличение контрастности (5 кнопка)
                if joystick.get_button(4) == 1:
                    if img_settings.Contrast < 10:
                        img_settings.Contrast += 1
                        if img_settings.Contrast > 10:
                            img_settings.Contrast = 10
                    image.SetImagingSettings(irequest)
                    self.add_log("Increasing contrast to " + str(img_settings.Contrast) + "...")

                # уменьшение контрастности (3 кнопка)
                if joystick.get_button(2) == 1:
                    if img_settings.Contrast > 0:
                        img_settings.Contrast -= 1
                        if img_settings.Contrast < 0:
                            img_settings.Contrast = 0
                    image.SetImagingSettings(irequest)
                    self.add_log("Reducing contrast to " + str(img_settings.Contrast) + "...")
            else:
                # включение автофокуса (6 кнопка)
                if joystick.get_button(5) == 1:
                    img_settings.Focus.AutoFocusMode = 'AUTO'
                    self.add_log("Turning on AUTO focus...")

                # включение ручного фокуса (4 кнопка)
                if joystick.get_button(3) == 1:
                    img_settings.Focus.AutoFocusMode = 'MANUAL'
                    self.add_log("Turning on MANUAL focus...")
                irequest.ImagingSettings = img_settings
                image.SetImagingSettings(irequest)

            # переключение режима цветового баланса
            if joystick.get_button(0) == 1:
                img_settings = image.GetImagingSettings(video_token)
                if img_settings.WhiteBalance.Mode == 'AUTO':
                    img_settings.WhiteBalance.Mode = 'MANUAL'
                    self.add_log("Switching to MANUAL white balance mode...")
                    img_settings.WhiteBalance.CbGain = 80  # оптимальные настройки CbGain
                    img_settings.WhiteBalance.CrGain = 30  # оптимальные настройки CrGain
                else:
                    img_settings.WhiteBalance.Mode = 'AUTO'
                    self.add_log("Switching to AUTO white balance mode...")
                irequest.ImagingSettings = img_settings
                image.SetImagingSettings(irequest)
                img_settings = image.GetImagingSettings(video_token)

            if img_settings.WhiteBalance.Mode == 'MANUAL':

                # увеличение CbGain
                if joystick.get_hat(0) == (1, 0):
                    if img_settings.WhiteBalance.CbGain < 100:
                        img_settings.WhiteBalance.CbGain += 5
                        if img_settings.WhiteBalance.CbGain > 100:
                            img_settings.WhiteBalance.CbGain = 100
                    image.SetImagingSettings(irequest)
                    self.add_log("Increasing CbGain to " + str(img_settings.WhiteBalance.CbGain) + "...")

                # уменьшение CbGain
                if joystick.get_hat(0) == (-1, 0):
                    if img_settings.WhiteBalance.CbGain > 0:
                        img_settings.WhiteBalance.CbGain -= 5
                        if img_settings.WhiteBalance.CbGain < 0:
                            img_settings.WhiteBalance.CbGain = 0
                    image.SetImagingSettings(irequest)
                    self.add_log("Reducing CbGain to " + str(img_settings.WhiteBalance.CbGain) + "...")

                # увеличение CrGain
                if joystick.get_hat(0) == (0, 1):
                    if img_settings.WhiteBalance.CrGain < 100:
                        img_settings.WhiteBalance.CrGain += 5
                        if img_settings.WhiteBalance.CrGain > 100:
                            img_settings.WhiteBalance.CrGain = 100
                    image.SetImagingSettings(irequest)
                    self.add_log("Increasing CrGain to " + str(img_settings.WhiteBalance.CrGain) + "...")

                # уменьшение CrGain
                if joystick.get_hat(0) == (0, -1):
                    if img_settings.WhiteBalance.CrGain > 0:
                        img_settings.WhiteBalance.CrGain -= 5
                        if img_settings.WhiteBalance.CrGain < 0:
                            img_settings.WhiteBalance.CrGain = 0
                    image.SetImagingSettings(irequest)
                    self.add_log("Reducing CrGain to " + str(img_settings.WhiteBalance.CrGain) + "...")

            self.listWidget.scrollToBottom()

        del mycam
        self.connectBtn.setEnabled(True)
        self.disconnectBtn.setDisabled(True)
        pygame.quit()


def maprange(a, b, s):
	(a1, a2), (b1, b2) = a, b
	return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def open_config():
    file = open("config.txt", "r")
    length = file_length(file)
    length /= 4
    file = open("config.txt", "r")
    num = 0
    ip = {}
    port = {}
    login = {}
    password = {}
    while num < length:
        temp = file.readline().split("\n")
        ip[num] = temp[0]

        temp = (file.readline().split("\n"))
        port[num] = int(temp[0])

        temp = file.readline().split("\n")
        login[num] = temp[0]

        temp = file.readline().split("\n")
        password[num] = temp[0]

        num += 1

    file.close()

    return ip, port, login, password, length


def file_length(file):
    lines = 0
    for line in file:
        lines += 1
    file.close()
    return lines


def find_key(dict, value):
    return [k for k, v in dict.iteritems() if v == value][0]


def move_horizontal(ptz, request, joystick):
    request.Velocity.PanTilt.x = maprange((-1, 1), (XMIN, XMAX), joystick.get_axis(X_AXIS))
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = 0
    ptz.ContinuousMove(request)


def move_vertical(ptz, request, joystick):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = maprange((-1, 1), (YMIN, YMAX), joystick.get_axis(Y_AXIS))
    request.Velocity.Zoom.x = 0
    ptz.ContinuousMove(request)


def zoom(ptz, request, joystick):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = maprange((-1, 1), (ZMIN, ZMAX), joystick.get_axis(Z_AXIS))
    ptz.ContinuousMove(request)


def main():
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue  # нужно для корректной работы камеры

    # import os
    # cwd = os.getcwd()  # Get the current working directory (cwd)
    # files = os.listdir(cwd)  # Get all the files in that directory
    # print("Files in '%s': %s" % (cwd, files))

    qt_app = QtWidgets.QApplication(sys.argv)  # новый экземпляр QApplication
    window = Application()  # создаём объект класса Application
    window.show()  # показываем окно
    window.disconnectBtn.setDisabled(True)
    ip, port, login, password, length = open_config()
    num = 0
    while num < length:
        window.comboBox.addItem(ip[num])
        num += 1
    # window.listWidget.addItem(str("Files in '%s': %s" % (cwd, files)))
    qt_app.exec_()  # запускаем приложение


if __name__ == '__main__':  # если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
