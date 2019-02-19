from time import sleep
from onvif import ONVIFCamera
exec(open("./fix.py").read())

ip = '192.168.15.42'
# login = 'ivanbobkov77'
# password = 'kmfj4XhUtQyMuC6G'

login = 'student'
password = 'Student.2019'

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1

def perform_move(ptz, request, timeout):
    # Start continuous move
    print(request)
    ptz.ContinuousMove(request)
    # Wait a certain time
    sleep(timeout)
    # Stop continuous move
    ptz.Stop({'ProfileToken': request.ProfileToken})


def move_up(ptz, request, timeout=1):
    print('move up...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMAX
    perform_move(ptz, request, timeout)


def move_down(ptz, request, timeout=1):
    print('move down...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMIN
    perform_move(ptz, request, timeout)


def move_right(ptz, request, timeout=1):
    print('move right...')
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = 0
    perform_move(ptz, request, timeout)


def move_left(ptz, request, timeout=1):
    print('move left...')
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = 0
    perform_move(ptz, request, timeout)


def continuous_move():
    mycam = ONVIFCamera(ip, 80, login, password)
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0]

    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = media_profile.token

    request.Velocity = media_profile.PTZConfiguration.DefaultPTZSpeed
    #    request.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    request.Velocity.Zoom.x = 0.0
    request.Velocity.PanTilt.space = ''
    request.Velocity.Zoom.space = ''
    ptz.Stop({'ProfileToken': media_profile.token})

    # Get range of pan and tilt
    # NOTE: X and Y are velocity vector
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

    # move right
    move_right(ptz, request)
    sleep(2)

    # move left
    move_left(ptz, request)
    sleep(2)

    # move up
    move_up(ptz, request)
    sleep(2)

    # move down
    move_down(ptz, request)


if __name__ == '__main__':
    continuous_move()