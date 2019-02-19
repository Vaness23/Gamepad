import pygame

pygame.init()
# size = [500, 700]
# screen = pygame.display.set_mode(size)
#
# clock = pygame.time.Clock()

done = False


import zeep
from onvif import ONVIFCamera, ONVIFService


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

from time import sleep
from onvif import ONVIFCamera

# rtsp://192.168.15.52/live/av0

ip = '192.168.15.42'
port = 80
#login = 'ivanbobkov77'
login = 'admin'
password = 'Supervisor'
#password = 'kmfj4XhUtQyMuC6G'

#login = 'student'
#password = 'Student.2019'

global XMAX, XMIN, YMAX, YMIN, ZMAX, ZMIN
# XMAX = 1
# XMIN = -1
# YMAX = 1
# YMIN = -1
# ZMAX = 1
# ZMIN = -1


def perform_move(ptz, request, timeout):
    # Start continuous move
    # print(request)
    ptz.ContinuousMove(request)
    # Wait a certain time
    sleep(timeout)
    # Stop continuous move
    # ptz.Stop({'ProfileToken': request.ProfileToken})


def move_up(ptz, request, timeout=0):
    # print('move up...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = throttle
    request.Velocity.Zoom.x = 0
    perform_move(ptz, request, timeout)


def move_down(ptz, request, timeout=0):
    # print('move down...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = -throttle
    request.Velocity.Zoom.x = 0
    perform_move(ptz, request, timeout)


def move_right(ptz, request, timeout=0):
    # print('move right...')
    request.Velocity.PanTilt.x = throttle
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = 0
    perform_move(ptz, request, timeout)


def move_left(ptz, request, timeout=0):
    # print('move left...')
    request.Velocity.PanTilt.x = -throttle
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = 0
    perform_move(ptz, request, timeout)


def zoom_in(ptz, request, timeout=0):
    # print('zoom in...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = throttle
    perform_move(ptz, request, timeout)


def zoom_out(ptz, request, timeout=0):
    # print('zoom out...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = -throttle
    perform_move(ptz, request, timeout)


mycam = ONVIFCamera(ip, port, login, password)
# Create media service object
media = mycam.create_media_service()
# Create ptz service object
ptz = mycam.create_ptz_service()

image = mycam.create_imaging_service()

# Get target profile
media_profile = media.GetProfiles()[0]

# Get PTZ configuration options for getting continuous move range
request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = media_profile.PTZConfiguration.token
ptz_configuration_options = ptz.GetConfigurationOptions(request)

ptz_configurations_list = ptz.GetConfigurations()
ptz_configuration = ptz_configurations_list[0]

request = ptz.create_type('ContinuousMove')
request.ProfileToken = media_profile.token

prequest = ptz.create_type('SetPreset')
prequest.ProfileToken = media_profile.token

grequest = ptz.create_type('GotoPreset')
grequest.ProfileToken = media_profile.token

srequest = ptz.create_type('SetConfiguration')

irequest = image.create_type('SetImagingSettings')
video_token = media.GetVideoSourceConfigurationOptions().VideoSourceTokensAvailable[0]
img_settings = image.GetImagingSettings(video_token)

request.Velocity = media_profile.PTZConfiguration.DefaultPTZSpeed
#    request.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
request.Velocity.Zoom.x = 0.0
request.Velocity.PanTilt.space = ''
request.Velocity.Zoom.space = ''
ptz.Stop({'ProfileToken': media_profile.token})

# Get range of pan and tilt
# NOTE: X and Y are velocity vector

XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
ZMAX = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Max
ZMIN = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Min

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

global throttle

isMoving = False
OX = False
OY = False
OZ = False

while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # <-- ОСИ ДЖОЙСТИКА -->
    # 0 - вправо / влево
    # 1 - вперед / назад
    # 2 - ???
    # 3 - throttle
    # 4 - поворот

    # print("X axis:{:>6.3f}".format(joystick.get_axis(0)))
    # print("Y axis:{:>6.3f}".format(joystick.get_axis(1)))
    # print("??? axis:{:>6.3f}".format(joystick.get_axis(2)))
    # print("Throttle:{:>6.3f}".format(joystick.get_axis(3)))
    # print("Z axis:{:>6.3f}".format(joystick.get_axis(4)))
    #

    throttle = (-(joystick.get_axis(3))) / 2 + 0.5
    # print("THROTTLE:{:>6.3f}".format(throttle))
    #
    # print("Number of buttons:", joystick.get_numbuttons())
    # for i in range(joystick.get_numbuttons()):
    #     print("Button ", i+1, ": ", joystick.get_button(i), sep='')
    #
    # print("Number of hats:", joystick.get_numhats())
    # print("Hat value:", joystick.get_hat(0))
    #
    # pygame.display.flip()
    #
    # clock.tick(20)

    # done = True

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

    # print(grequest)

    if joystick.get_axis(0) > 0.3:
        move_right(ptz, request)
        isMoving = True
        OX = True

    if joystick.get_axis(0) < -0.3:
        move_left(ptz, request)
        isMoving = True
        OX = True

    if joystick.get_axis(1) > 0.3:
        move_up(ptz, request)
        isMoving = True
        OY = True

    if joystick.get_axis(1) < -0.3:
        move_down(ptz, request)
        isMoving = True
        OY = True

    if joystick.get_axis(4) > 0.3:
        zoom_in(ptz, request)
        isMoving = True
        OZ = True

    if joystick.get_axis(4) < -0.3:
        zoom_out(ptz, request)
        isMoving = True
        OZ = True

    if isMoving:

        print(joystick.get_axis(0))

        if -0.3 < joystick.get_axis(0) < 0.3 and OX:
            ptz.Stop({'ProfileToken': request.ProfileToken})
            print(request.ProfileToken)
            isMoving = False
            OX = False

        if joystick.get_axis(1) <= 0.3 and joystick.get_axis(1) >= -0.3 and OY:
            ptz.Stop({'ProfileToken': request.ProfileToken})
            isMoving = False
            OY = False

        if joystick.get_axis(4) <= 0.3 and joystick.get_axis(4) >= -0.3 and OZ:
            ptz.Stop({'ProfileToken': request.ProfileToken})
            isMoving = False
            OZ = False

    ptz = mycam.create_ptz_service()

    if joystick.get_button(1) == 1:

        if joystick.get_button(6) == 1:
            prequest.PresetName = "7"
            prequest.PresetToken = '7'
            preset = ptz.SetPreset(prequest)

        if joystick.get_button(7) == 1:
            prequest.PresetName = "8"
            prequest.PresetToken = '8'
            preset = ptz.SetPreset(prequest)

        if joystick.get_button(8) == 1:
            prequest.PresetName = "9"
            prequest.PresetToken = '9'
            preset = ptz.SetPreset(prequest)

        if joystick.get_button(9) == 1:
            prequest.PresetName = "10"
            prequest.PresetToken = '10'
            preset = ptz.SetPreset(prequest)

        if joystick.get_button(10) == 1:
            prequest.PresetName = "11"
            prequest.PresetToken = '11'
            preset = ptz.SetPreset(prequest)

        if joystick.get_button(11) == 1:
            prequest.PresetName = "12"
            prequest.PresetToken = '12'
            preset = ptz.SetPreset(prequest)

    if joystick.get_button(6) == 1:
        grequest.PresetToken = '7'
        ptz.GotoPreset(grequest)

    if joystick.get_button(7) == 1:
        grequest.PresetToken = '8'
        ptz.GotoPreset(grequest)

    if joystick.get_button(8) == 1:
        grequest.PresetToken = '9'
        ptz.GotoPreset(grequest)

    if joystick.get_button(9) == 1:
        grequest.PresetToken = '10'
        ptz.GotoPreset(grequest)

    if joystick.get_button(10) == 1:
        grequest.PresetToken = '11'
        ptz.GotoPreset(grequest)

    if joystick.get_button(11) == 1:
        grequest.PresetToken = '12'
        ptz.GotoPreset(grequest)

    # настройка изображения

    # увеличение яркости (6 кнопка)
    if joystick.get_button(5) == 1:
        if img_settings.Brightness < 100:
            img_settings.Brightness += 5
        image.SetImagingSettings(irequest)

    # уменьшение яркости (4 кнопка)
    if joystick.get_button(3) == 1:
        if img_settings.Brightness > 0:
            img_settings.Brightness -= 5
        image.SetImagingSettings(irequest)

    # увеличение контрастности (5 кнопка)
    if joystick.get_button(4) == 1:
        if img_settings.Contrast < 100:
            img_settings.Contrast += 5
        image.SetImagingSettings(irequest)

    # уменьшение контрастности (3 кнопка)
    if joystick.get_button(2) == 1:
        if img_settings.Contrast > 0:
            img_settings.Contrast -= 5
        image.SetImagingSettings(irequest)

    # переключение режима цветового баланса
    if joystick.get_button(0) == 1:
        img_settings = image.GetImagingSettings(video_token)
        if img_settings.WhiteBalance.Mode == 'AUTO':
            img_settings.WhiteBalance.Mode = 'MANUAL'
        else:
            img_settings.WhiteBalance.Mode = 'AUTO'
        image.SetImagingSettings(irequest)

    if img_settings.WhiteBalance.Mode == 'MANUAL':

        # увеличение CbGain
        if joystick.get_hat(0) == (1, 0):
            if img_settings.WhiteBalance.CbGain < 100:
                img_settings.WhiteBalance.CbGain += 5
            image.SetImagingSettings(irequest)

        # уменьшение CbGain
        if joystick.get_hat(0) == (-1, 0):
            if img_settings.WhiteBalance.CbGain > 0:
                img_settings.WhiteBalance.CbGain -= 5
            image.SetImagingSettings(irequest)

        # увеличение CrGain
        if joystick.get_hat(0) == (0, 1):
            if img_settings.WhiteBalance.CrGain < 100:
                img_settings.WhiteBalance.CrGain += 5
            image.SetImagingSettings(irequest)

        # уменьшение CrGain
        if joystick.get_hat(0) == (0, -1):
            if img_settings.WhiteBalance.CrGain > 0:
                img_settings.WhiteBalance.CrGain -= 5
            image.SetImagingSettings(irequest)

    irequest.VideoSourceToken = video_token
    irequest.ImagingSettings = img_settings
    irequest.ForcePersistence = False

pygame.quit()
