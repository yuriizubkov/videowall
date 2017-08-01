from PyQt4 import QtCore, QtGui
from configparser import SafeConfigParser
from player import Player


class VideoWall(QtGui.QWidget):
    def __init__(self, app, parent):
        super(VideoWall, self).__init__()
        self.players = {}
        #reading config.ini
        self.config = SafeConfigParser()
        self.config.read('config.ini')
        self.number_of_cameras = self.config.getint('videowall',
        'number_of_cameras', fallback=6)
        if self.number_of_cameras > 6:
            self.number_of_cameras = 6
        self.window_aspect_ratio_coeff = self.config.getfloat('videowall',
        'window_aspect_ratio_coeff', fallback=1.77777777778)
        self.audio_mode = self.config.get('videowall', 'audio_mode',
        fallback='hdmi')
        self.rtsp_sleep_delay = self.config.getint('videowall',
        'rtsp_sleep_delay', fallback=1)
        self.hide_window_title = self.config.getint('videowall',
        'hide_window_title', fallback=0)
        if self.hide_window_title == 1:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timer = None
        self.use_sequence_view = self.config.getint('videowall',
            'use_sequence_view', fallback=0)
        if self.use_sequence_view == 1:
            self.sequence_view = {}
            self.sequence_current_index = 0
            sequence = self.config.get('videowall',
                'sequence_view', fallback='1').split(',')
            for s_ind in range(0, len(sequence)):
                self.sequence_view[s_ind] = int(sequence[s_ind])
            self.sequence_view_seconds = self.config.getint('videowall',
                'sequence_view_seconds', fallback=30000)
        #reading cameras settings
        self.cameras_settings = {}
        for cam_number in range(0, self.number_of_cameras):
            self.cameras_settings[cam_number] = {'preview_url':
            (self.config.get('camera-' + str(cam_number + 1), 'preview_url',
            fallback='')),
            'full_url': (self.config.get('camera-' + str(cam_number + 1),
            'full_url', fallback=''))
            }
        #setting window title
        window_title = self.config.get('videowall', 'window_title',
        fallback='Video Wall')
        self.setWindowTitle(window_title)
        #setting cameras viewports
        self.stylesheet = self.config.get('videowall', 'camera_stylesheet',
        fallback='background-color: black')
        self.viewports = {}
        for cam_number in range(0, self.number_of_cameras):
            self.viewports[cam_number] = QtGui.QLabel(self)
            self.viewports[cam_number].setStyleSheet(self.stylesheet)
            self.viewports[cam_number].setObjectName('camera-' + str(cam_number + 1))
            self.viewports[cam_number].setText(str(cam_number + 1))
            #self.viewports[cam_number].installEventFilter(self)
        app.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if type(source) == QtGui.QLabel:
                if source.objectName() != 'camera-1':
                    clicked_id = int(source.text()) - 1
                    self.changeMainCamera(clicked_id)

        if event.type() == QtCore.QEvent.KeyPress:
            current_player_id = int(self.viewports[0].text()) - 1
            next_player_id = 0

            if event.key() == 16777236:  # ->
                next_player_id = current_player_id + 1
                if next_player_id > (self.number_of_cameras - 1):
                    next_player_id = 0
            if event.key() == 16777234:  # <-
                next_player_id = current_player_id - 1
                if next_player_id < 0:
                    next_player_id = self.number_of_cameras - 1
            self.changeMainCamera(next_player_id)

        return super(VideoWall, self).eventFilter(source, event)

    def changeMainCamera(self, new_cam_id):
        cam_viewport = None
        for viewport_id in range(0, self.number_of_cameras):
            if self.viewports[viewport_id].text() == str(new_cam_id + 1):
                cam_viewport = self.viewports[viewport_id]

        current_player_id = int(self.viewports[0].text()) - 1
        current_player_atX = self.players[current_player_id].atX
        current_player_atY = self.players[current_player_id].atY
        current_player_width = self.players[current_player_id].width
        current_player_height = self.players[current_player_id].height
        current_player_audio_mode = self.players[current_player_id].audio_mode
        clicked_id = new_cam_id
        clicked_atX = self.players[clicked_id].atX
        clicked_atY = self.players[clicked_id].atY
        clicked_width = self.players[clicked_id].width
        clicked_height = self.players[clicked_id].height
        clicked_audio_mode = self.players[clicked_id].audio_mode
        #stop main screen player camera-1
        self.players[current_player_id].stop()
        self.players[current_player_id].process.stdin.write(b'q')
        self.players[current_player_id].process.terminate()
        #stop and kill clicked player
        self.players[clicked_id].stop()
        self.players[clicked_id].process.stdin.write(b'q')
        self.players[clicked_id].process.terminate()
        QtCore.QThread.sleep(self.rtsp_sleep_delay)
        #run preview from main camera-1 screen on this place
        cam_viewport.setText(str(current_player_id + 1))
        self.players[current_player_id] = Player(
            self.cameras_settings[current_player_id]['preview_url'],
            clicked_atX, clicked_atY, clicked_width, clicked_height,
            clicked_audio_mode, current_player_id)
        #run clicked on main screen in HD (full_url)
        self.viewports[0].setText(str(clicked_id + 1))
        self.players[clicked_id] = Player(
            self.cameras_settings[clicked_id]['full_url'],
            current_player_atX, current_player_atY,
            current_player_width, current_player_height,
            current_player_audio_mode, clicked_id)
        QtCore.QThread.sleep(self.rtsp_sleep_delay)

    def redrawViewPorts(self, width, height, width_difference):
        sc = 1 / 3
        lc = 2 / 3
        w_offset = width_difference / 2
        for cam_number in range(0, self.number_of_cameras):
            if cam_number == 0:
                self.viewports[cam_number].resize(
                    width * lc, height * lc)
                self.viewports[cam_number].move(w_offset, 0)
            else:
                if cam_number > 3:
                    self.viewports[cam_number].resize(width * sc,
                    height * sc)
                    self.viewports[cam_number].move(w_offset +
                    ((cam_number - 4) * width * sc), height * lc)
                else:
                    self.viewports[cam_number].resize(width * sc,
                    height * sc)
                    self.viewports[cam_number].move(w_offset +
                    (width * lc), (cam_number - 1) * height * sc)

    def redrawPlayers(self):
        for cam_number in range(0, self.number_of_cameras):
                pos = self.geometry().topLeft() + self.viewports[cam_number].pos()
                player_id = int(self.viewports[cam_number].text()) - 1
                quality = 'preview_url'
                if cam_number == 0:
                    quality = 'full_url'
                if cam_number in self.players:
                    self.players[player_id].resize(
                        pos.x(), pos.y(),
                        self.viewports[cam_number].geometry().width(), self.viewports[cam_number].geometry().height())
                else:
                    if len(self.cameras_settings[cam_number][quality]) is not 0:
                        self.players[cam_number] = Player(
                        self.cameras_settings[cam_number][quality],
                        pos.x(), pos.y(),
                        self.viewports[cam_number].geometry().width(), self.viewports[cam_number].geometry().height(),
                        self.audio_mode, cam_number)
                        QtCore.QThread.sleep(self.rtsp_sleep_delay)
                        #start sequence if needed
                        if self.timer is None and self.use_sequence_view == 1:
                            self.timer = QtCore.QTimer()
                            self.timer.timeout.connect(self.timerEvent)
                            self.timer.start(self.sequence_view_seconds)

    def resizeEvent(self, e):
        width = e.size().width()
        height = e.size().height()
        calc_width = height * self.window_aspect_ratio_coeff
        width_difference = 0
        if calc_width > width:
            height = width / self.window_aspect_ratio_coeff
        else:
            width_difference = width - calc_width
            width = calc_width
        self.redrawViewPorts(width, height, width_difference)
        self.redrawPlayers()

    def moveEvent(self, e):
        self.redrawPlayers()

    def closeEvent(self, e):
        for player in self.players:
            if self.players[player].process is not None and self.players[player].process.poll() is None:
                self.players[player].stop()
                self.players[player].process.stdin.write(b'q')
                self.players[player].process.terminate()
        e.accept()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                for player in self.players:
                    self.players[player].hide()
            elif event.oldState() & QtCore.Qt.WindowMinimized:
                for player in self.players:
                    self.players[player].unhide()
        QtGui.QWidget.changeEvent(self, event)

    def timerEvent(self):
        self.sequence_current_index = self.sequence_current_index + 1
        if self.sequence_current_index > len(self.sequence_view) - 1:
            self.sequence_current_index = 0
        self.changeMainCamera(self.sequence_view[self.sequence_current_index] - 1)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    vw = VideoWall(app, None)
    vw.move(0, 0)
    vw.resize(640, 480)
    vw.showMaximized()
    app.exec_()