import subprocess
import os


class Player():
    def __init__(self, url, atX, atY, width, height, audio_mode, player_id):
        self.atX = atX
        self.atY = atY
        self.width = width
        self.height = height
        self.audio_mode = audio_mode
        self.player_id = player_id
        self.position = str(atX) + ' ' + str(atY) + ' ' + str(
        atX + width) + ' ' + str(atY + height)
        self.player_id = player_id
        self.dbus_name = 'org.mpris.MediaPlayer2.omxplayer' + str(player_id)
        self.process = subprocess.Popen(['/usr/bin/omxplayer', '-o', audio_mode,
                '--no-osd', '--win', self.position, '--dbus_name',
                self.dbus_name, '--avdict', 'rtsp_transport:tcp', url], stdin=subprocess.PIPE)

    def resize(self, atX, atY, width, height):
        self.atX = atX
        self.atY = atY
        self.width = width
        self.height = height
        subprocess.call([os.path.abspath('dbuscontrol.sh'),
        'setvideopos', str(self.player_id),
        str(atX), str(atY), str(atX + width), str(atY + height)])

    def hide(self):
        subprocess.call([os.path.abspath('dbuscontrol.sh'),
        'hidevideo', str(self.player_id)])

    def unhide(self):
        subprocess.call([os.path.abspath('dbuscontrol.sh'),
        'unhidevideo', str(self.player_id)])

    def stop(self):
        subprocess.call([os.path.abspath('dbuscontrol.sh'),
        'stop', str(self.player_id)])
