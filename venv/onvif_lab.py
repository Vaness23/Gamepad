from onvif import ONVIFCamera
from time import sleep
import zeep


def zeep_pythonvalue(self, xmlvalue):  # нужно для корректной отправки запросов
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue  # нужно для корректной отправки запросов

# подключение к камере
ip = '192.168.15.42'
port = 80
login = 'admin'
password = 'Supervisor'
mycam = ONVIFCamera(ip, port, login, password)  # инициализация камеры

# создание сервисов
ptz = mycam.create_ptz_service()
media = mycam.create_media_service()
image = mycam.create_imaging_service()

# получение токенов сервисов
media_profile = media.GetProfiles()[0]
media_token = media_profile.token
ptz_token = media_profile.PTZConfiguration.token
video_token = media.GetVideoSourceConfigurationOptions().VideoSourceTokensAvailable[0]  # для imaging

# получение пределов координат PTZ
XMAX = media_profile.PTZConfiguration.PanTiltLimits.Range.XRange.Max
XMIN = media_profile.PTZConfiguration.PanTiltLimits.Range.XRange.Min
YMAX = media_profile.PTZConfiguration.PanTiltLimits.Range.YRange.Max
YMIN = media_profile.PTZConfiguration.PanTiltLimits.Range.YRange.Min
ZMAX = media_profile.PTZConfiguration.ZoomLimits.Range.XRange.Max
ZMIN = media_profile.PTZConfiguration.ZoomLimits.Range.XRange.Min

# создание запроса absolute move
arequest = ptz.create_type('AbsoluteMove')
arequest.ProfileToken = media_token  # назначение токена
grequest = ptz.create_type('GetPresets')  # создание запроса GetPresets
grequest.ProfileToken = media_token  # назначение токена
preset = ptz.GetPresets(grequest)[0]  # достаем структуру Position из пресетов
arequest.Position = preset.PTZPosition  # присваиваем структуру
arequest.Speed = media_profile.PTZConfiguration.DefaultPTZSpeed  # достаем структуру Speed


# создание запроса continuous move
crequest = ptz.create_type('ContinuousMove')
crequest.ProfileToken = media_token  # назначение токена
# настройка свойства Velocity
crequest.Velocity = media_profile.PTZConfiguration.DefaultPTZSpeed
crequest.Velocity.PanTilt.space = ''
crequest.Velocity.Zoom.space = ''

# создание запроса set imaging settings
irequest = image.create_type('SetImagingSettings')
img_settings = image.GetImagingSettings(video_token)  # достаем настройки изображения
irequest.VideoSourceToken = video_token  # присваивание токена
irequest.ImagingSettings = img_settings  # присваивание настроек изображения
irequest.ForcePersistence = False  # после выключения камеры настройки будут сохранены

# создание запроса get move options для доступа к структуре Focus
mrequest = image.create_type('GetMoveOptions')
mrequest.VideoSourceToken = video_token  # присваивание токена
move_options = image.GetMoveOptions(mrequest)  # достаем структуру Focus

# создание запроса move (регулировка фокуса)
move_request = image.create_type('Move')
move_request.VideoSourceToken = video_token  # присваивание токена
move_request.Focus = move_options  # присваивание структуры Focus
move_request.Focus.Continuous.Speed = 0.0  # обнуление скорости движения фокуса


# переход в абсолютные координаты
def abs_move(request, ptz, x, y, z):
    # присваивание координат
    request.Position.PanTilt.x = x
    request.Position.PanTilt.y = y
    request.Position.Zoom.x = z
    ptz.AbsoluteMove(request)  # отправка запроса


# continuous move по горизонтали
def move_horizontal(request, ptz, speed, timeout):
    # присваивание скорости осям
    request.Velocity.PanTilt.x = speed
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = 0
    ptz.ContinuousMove(request)  # отпавка запроса
    sleep(timeout)  # движение длится timeout секунд
    ptz.Stop({'ProfileToken': media_profile.token})  # остановка камеры


# continuous move по вертикали
def move_vertical(request, ptz, speed, timeout):
    # присваивание скорости осям
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = speed
    request.Velocity.Zoom.x = 0
    ptz.ContinuousMove(request)  # отпавка запроса
    sleep(timeout)  # движение длится timeout секунд
    ptz.Stop({'ProfileToken': media_profile.token})  # остановка камеры


# continuous move (зумирование)
def zoom(request, ptz, speed, timeout):
    # присваивание скорости осям
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = speed
    ptz.ContinuousMove(request)  # отпавка запроса
    sleep(timeout)  # движение длится timeout секунд
    ptz.Stop({'ProfileToken': media_profile.token})  # остановка камеры


# регулировка фокуса
def focus(irequest, img_settings, image, move_request, speed):
    img_settings.Focus.AutoFocusMode = 'MANUAL'  # отключение автофокуса
    irequest.ImagingSettings = img_settings  # обновление настроек
    image.SetImagingSettings(irequest)  # отправка запроса на отключение автофокуса
    move_request.Focus.Continuous.Speed = speed  # присваивание скорости движению фокуса
    image.Move(move_request)  # отправка запроса


# # пример использования функций
img_settings.Focus.AutoFocusMode = 'AUTO'  # включение автофокуса
irequest.ImagingSettings = img_settings  # обновление настроек
image.SetImagingSettings(irequest)  # отправка запроса на отключение автофокуса
abs_move(arequest, ptz, 0.2, -0.5, 0.3)  # absolute move в точку (x = 0.2, y = -0.5, z = 0.3)
sleep(3)  # ожидание - 3 секунды
move_horizontal(crequest, ptz, 0.3, 3)  # continuous move вправо со скоростью 0.6 в течение 3 секунд
move_vertical(crequest, ptz, 0.4, 2)  # continuous move вверх со скоростью 0.4 в течение 2 секунд
zoom(crequest, ptz, 1, 4)  # приближение в течение 4 секунд
sleep(3)
zoom(crequest, ptz, -1, 2)  # отдаление в течение 2 секунд
sleep(3)
focus(irequest, img_settings, image, move_request, -5.0)  # изменение фокуса на -5.0
sleep(3)  # ожидание - 3 секунды
