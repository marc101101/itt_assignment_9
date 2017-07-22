import lib.wiimote as wiimote
import lib.gestures as gestures
import time
import sys

from functools import partial

import numpy as np

from PyQt5 import Qt, QtGui, QtCore, QtWidgets

class Mapping:
    def __init__(self, dest_w, dest_h):
        self.SRC_W = 1024
        self.SRC_H = 768
        self.DEST_W = dest_w
        self.DEST_H = dest_h

        self.source_to_dest = None
        self.dx1, self.dy1 = 0, 0
        self.dx2, self.dy2 = self.DEST_W, 0
        self.dx3, self.dy3 = self.DEST_W, self.DEST_H
        self.dx4, self.dy4 = 0, self.DEST_H

    def calculate_source_to_dest(self, ir_markers):
        if len(ir_markers) == 4:
            x1, y1 = ir_markers[0]
            x2, y2 = ir_markers[1]
            x3, y3 = ir_markers[2]
            x4, y4 = ir_markers[3]

            # links oben in ir cam: x=0 y=786
            # rechts oben in ir cam: x=1023 y=786
            # links unten in ir cam: x=0 y=0
            # rechts unten in ir cam: x=1023 y=0

            ir_markers_sorted = sorted(ir_markers)

            if ir_markers_sorted[0][1] < ir_markers_sorted[1][1]:
                x1, y1 = ir_markers_sorted[1]
                x4, y4 = ir_markers_sorted[0]
            else:
                x1, y1 = ir_markers_sorted[0]
                x4, y4 = ir_markers_sorted[1]

            if ir_markers_sorted[2][1] < ir_markers_sorted[3][1]:
                x2, y2 = ir_markers_sorted[3]
                x3, y3 = ir_markers_sorted[2]
            else:
                x2, y2 = ir_markers_sorted[2]
                x3, y3 = ir_markers_sorted[3]

            # Step 1
            source_points_123 = np.matrix([[x1, x2, x3],
                                           [y1, y2, y3],
                                           [1, 1, 1]])

            source_point_4 = [[x4],
                              [y4],
                              [1]]

            scale_to_source = np.linalg.solve(source_points_123, source_point_4)

            ls, ms, ts = [float(x) for x in scale_to_source]

            # Step 2
            unit_to_source = np.matrix([[ls * x1, ms * x2, ts * x3],
                                        [ls * y1, ms * y2, ts * y3],
                                        [ls * 1, ms * 1, ts * 1]])

            # Step 3
            dest_points_123 = np.matrix([[self.dx1, self.dx2, self.dx3],
                                         [self.dy1, self.dy2, self.dy3],
                                         [1, 1, 1]])

            dest_point_4 = np.matrix([[self.dx4],
                                      [self.dy4],
                                      [1]])

            scale_to_dest = np.linalg.solve(dest_points_123, dest_point_4)

            ld, md, td = [float(x) for x in scale_to_dest]

            unit_to_dest = np.matrix([[ld * self.dx1, md * self.dx2, td * self.dx3],
                                      [ld * self.dy1, md * self.dy2, td * self.dy3],
                                      [ld * 1, md * 1, td * 1]])

            # Step 4
            source_to_unit = np.linalg.inv(unit_to_source)

            # Step 5
            self.source_to_dest = unit_to_dest @ source_to_unit
        else:
            print("NOT EXACTLY 4 IR MARKER COORDINATES GIVEN")
            return

    def get_pointing_point(self):
        # Mapping of center
        x, y, z = [float(w) for w in self.source_to_dest @ np.matrix([[self.SRC_W / 2],
                                                                      [self.SRC_H / 2],
                                                                      [1]])]

        # step 7: dehomogenization
        x = x / z
        y = y / z

        # if x < self.DEST_W/2:
        #     x = self.DEST_W/2 + (self.DEST_W/2 - x)
        # else:
        #     x = self.DEST_W/2 - (self.DEST_W/2 - x)

        return x, y


class Mapping_safe:
    SRC_W = 1024
    SRC_H = 768

    def __init__(self, dest_w, dest_h):
        self.DEST_W = dest_w
        self.DEST_H = dest_h
        self.sx1 = 0
        self.sy1 = 0
        self.sx2 = self.SRC_W
        self.sy2 = 0
        self.sx3 = self.SRC_H
        self.sy3 = self.SRC_W
        self.sx4 = 0
        self.sy4 = self.SRC_H

    def calc_source_to_dest_matrix(self, s1, s2, s3, s4):
        self.sx1 = s1[0]
        self.sy1 = s1[1]
        self.sx2 = s2[0]
        self.sy2 = s2[1]
        self.sx3 = s3[0]
        self.sy3 = s3[1]
        self.sx4 = s4[0]
        self.sy4 = s4[1]

        self.calc_scale_to_source()
        self.calc_source_to_dest()

    def calc_scale_to_source(self):
        source_points_123 = np.matrix([[self.sx1, self.sx2, self.sx3],
                                       [self.sy1, self.sy2, self.sy3],
                                       [1, 1, 1]])

        source_point_4 = [[self.sx4],
                          [self.sy4],
                          [1]]

        self.scale_to_source = np.linalg.solve(source_points_123, source_point_4)

        l, m, t = [float(x) for x in self.scale_to_source]

        self.unit_to_source = np.matrix([[l * self.sx1, m * self.sx2, t * self.sx3],
                                         [l * self.sy1, m * self.sy2, t * self.sy3],
                                         [l, m, t]])

    def calc_source_to_dest(self):
        dx1 = 0
        dy1 = 0
        dx2 = self.DEST_W
        dy2 = 0
        dx3 = self.DEST_W
        dy3 = self.DEST_H
        dx4 = 0
        dy4 = self.DEST_H

        dest_points_123 = np.matrix([[dx1, dx2, dx3],
                                     [dy1, dy2, dy3],
                                     [1, 1, 1]])

        dest_point_4 = np.matrix([[dx4],
                                  [dy4],
                                  [1]])

        self.scale_to_dest = np.linalg.solve(dest_points_123, dest_point_4)
        l, m, t = [float(x) for x in self.scale_to_dest]

        self.unit_to_dest = np.matrix([[l * dx1, m * dx2, t * dx3],
                                       [l * dy1, m * dy2, t * dy3],
                                       [l, m, t]])

        self.source_to_unit = np.linalg.inv(self.unit_to_source)

        self.source_to_dest = self.unit_to_dest @ self.source_to_unit

    def process_ir_data(self, x=512, y=384):
        x, y, z = [float(w) for w in (self.source_to_dest @ np.matrix([[x],
                                                                       [y],
                                                                       [1]]))]

        return self.dehomogenize(x, y, z)

    def dehomogenize(self, x, y, z):
        return x / z, y / z


class ScrumArea(QtWidgets.QWidget):

    def __init__(self, width, height, window_scope):
        super().__init__()
        self.resize(width, height)
        print("SIZE OF PAINT AREA: ", self.size())
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.recognition_mode = False
        self.points = []
        self.current_mode = 'LINE'
        self.window = window_scope

        self.scrum_board_layout = QtWidgets.QGridLayout()

        self.setMouseTracking(True)  # only get events when button is pressed
        self.init_ui()

        self.current_cursor_point = None

        self.active_color = QtGui.QColor(255, 255, 255)
        self.active_size = 20
        self.active_shape = 'LINE'

    def init_ui(self):
        self.setWindowTitle('SCRUM BOARD')
        scrum_board_layout_column = QtWidgets.QHBoxLayout()

        backlog_area = QtWidgets.QLabel("backlog")
        backlog_area.setStyleSheet("border: 1px solid black; margin-top: -950px")
        backlog_area.setAlignment(Qt.Qt.AlignCenter)
        scrum_board_layout_column.addWidget(backlog_area)

        backlog_area = QtWidgets.QLabel("toDo")
        backlog_area.setStyleSheet("border: 1px solid black; margin-top: -950px")
        backlog_area.setAlignment(Qt.Qt.AlignCenter)
        scrum_board_layout_column.addWidget(backlog_area)

        backlog_area = QtWidgets.QLabel("done")
        backlog_area.setStyleSheet("border: 1px solid black; margin-top: -950px")
        backlog_area.setAlignment(Qt.Qt.AlignCenter)
        scrum_board_layout_column.addWidget(backlog_area)

        self.window.addLayout(scrum_board_layout_column, 0, 2, 12, 15)


    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.update()
        elif ev.button() == QtCore.Qt.RightButton:
            self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            self.update()

    def mouseMoveEvent(self, ev):
        self.current_cursor_point = [ev.x(), ev.y()]
        self.update()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawRect(ev.rect())

        if self.current_cursor_point:
            qp.setBrush(QtGui.QColor(0, 0, 0))
            qp.drawEllipse(self.current_cursor_point[0] - 10, self.current_cursor_point[1] - 10, 20, 20)
            qp.drawEllipse(self.current_cursor_point[0] - 10, self.current_cursor_point[1] - 10, 20, 20)
        qp.end()

    def add_point(self, x, y):
        if self.drawing:
            self.points.append((x, y))
            self.update()

    def start_drawing(self):
        print("Started drawing")
        self.drawing = True

    def stop_drawing(self):
        print("Stopped drawing")
        self.drawing = False

    def increase_pen_size(self):
        self.active_size += 1

    def decrease_pen_size(self):
        if self.active_size > 1:
            self.active_size -= 1


class TileSet(QtWidgets.QWidget):

    def __init__(self, width=150, height=100):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.init_ui()

        self.active_color = QtGui.QColor(255, 255, 255)
        self.active_size = 20

    def init_ui(self):
        self.setWindowTitle('tile')
        scrum_board_layout = QtWidgets.QHBoxLayout()

        self.tile_headline = QtWidgets.QLabel("Tile")
        self.tile_assignment = QtWidgets.QLabel("Assigned to: Markus")

        scrum_board_layout.addWidget(self.tile_headline)
        scrum_board_layout.addWidget(self.tile_assignment)


class PaintApplication:

    WINDOW_WIDTH = 1700
    WINDOW_HEIGHT = 1300

    name_hard = 'Nintendo RVL-CNT-01-TR'

    RED = QtGui.QColor(255, 0, 0)
    GREEN = QtGui.QColor(0, 255, 0)
    YELLOW = QtGui.QColor(255, 255, 0)
    GRAY = QtGui.QColor(100, 100, 100)
    BLACK = QtGui.QColor(0, 0, 0)
    current_recording = []
    recognition_mode = False

    def __init__(self):

        self.wm = None

        self.dOne = gestures.DollarRecognizer()

        self.setup_ui()

        self.mapping = Mapping(1920, 1080)
        print("ASSERTED: (99.44448537537721, 847.1789582258892)")
        testdata = [(500, 300), (950, 300), (900, 700), (450, 690)]
        self.mapping.calculate_source_to_dest(testdata)
        print("RESULT: ", self.mapping.get_pointing_point())

        #self.mapping = Mapping(self.paint_area.width(), self.paint_area.height())

        self.window.show()

    def set_recognition_mode(self, value):
        # catch some wrong paramaters
        if value is True:
            self.current_recording = []
            self.recognition_mode = True
        else:
            self.recognition_mode = False
            print(self.current_recording)
            # self.dOne.AddTemplate(self.current_recording, "ColorGesture")
            print(self.dOne.dollar_recognize(self.current_recording))

    def setup_ui(self):
        self.window = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QGridLayout()
        self.window.setLayout(self.main_layout)

        print("WINDOWS SIZE BEFORE MAX: ", self.window.size())

        print("WINDOWS SIZE AFTER MAX: ", self.window.size())
        self.window.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self.init_connection_properties() #inits the basic connection ui properties
        self.init_scrum_board() #inits the actual scrum board

    def init_connection_properties(self):
        connection_properties_layout = QtWidgets.QVBoxLayout()

        self.num_ir_objects = QtWidgets.QLabel("0")
        fo = QtGui.QFont("Times", 128)
        self.num_ir_objects.setFont(fo)
        self.num_ir_objects.setFixedHeight(300)
        connection_properties_layout.addWidget(self.num_ir_objects)

        connection_properties_layout.addWidget(QtWidgets.QLabel("WiiMote connection status"))
        self.label_wm_connection_status = QtWidgets.QLabel("Not connected")
        self.label_wm_connection_status.setAlignment(Qt.Qt.AlignCenter)
        self.label_wm_connection_status.setFixedHeight(100)
        self.fill_label_background(self.label_wm_connection_status, self.RED)
        connection_properties_layout.addWidget(self.label_wm_connection_status)

        connection_properties_layout.addWidget(QtWidgets.QLabel("Mac Address Wii Mote Controller:"))
        self.line_edit_br_addr = QtWidgets.QLineEdit()
        self.line_edit_br_addr.setText('18:2A:7B:F4:AC:23')
        connection_properties_layout.addWidget(self.line_edit_br_addr)
        self.button_connect = QtWidgets.QPushButton("Connect")
        self.connection_established = True
        self.button_connect.clicked.connect(self.connect_wm)
        connection_properties_layout.addWidget(self.button_connect)

        # layout.addSpacerItem(QtWidgets.QSpacerItem(0, 300))

        self.main_layout.addLayout(connection_properties_layout, 0, 0, 12, 2, Qt.Qt.AlignCenter)

    def init_scrum_board(self):
        scrum_board_layout = QtWidgets.QVBoxLayout()

        self.scrum_area = ScrumArea(width=(11 * self.WINDOW_WIDTH / 12), height=(11 * self.WINDOW_HEIGHT / 12), window_scope=self.main_layout)
        scrum_board_layout.addWidget(self.scrum_area)
        self.main_layout.addLayout(scrum_board_layout, 0, 2, 12, 15)

    #passt soweit
    def connect_wm(self):
        addr = self.line_edit_br_addr.text()
        print("Connecting to %s (%s)" % (self.name_hard, addr))
        self.wm = wiimote.connect(addr, self.name_hard)
        self.button_connect.setText("Disconnect")
        print("Connected")

        self.fill_label_background(self.label_wm_connection_status, self.GREEN)
        self.label_wm_connection_status.setText("Connected to %s" % addr)

        self.wm.buttons.register_callback(self.handle_buttons)
        self.wm.ir.register_callback(self.handle_ir_data)

    #TODO: anpassen an Bedürnisse
    def handle_buttons(self, buttons):
        for button in buttons:
            if button[0] == 'A':
                if button[1]:
                    print("A pressed")
                elif not button[1]:
                    print("A released")
            elif button[0] == 'B':
                if button[1]:
                    print("B pressed")
                elif not button[1]:
                    print("B released")

    def handle_ir_data(self, ir_data):

        # links oben in ir cam: x=0 y=786
        # rechts oben in ir cam: x=1023 y=786
        # links unten in ir cam: x=0 y=0
        # rechts unten in ir cam: x=1023 y=0

        self.num_ir_objects.setText("%d" % len(ir_data))

        # for ir in ir_data:
        #     print("x: %d\ty: %d\tid: %d" %(ir['x'], ir['y'], ir['id']))

        # there needto be the four markers for the corners
        if len(ir_data) == 4:

            x = [ir_object['x'] for ir_object in ir_data]
            y = [ir_object['y'] for ir_object in ir_data]

            # calc matrix
            if x[0] < 1023:
                sensor_coords = []
                for ir_object in ir_data:
                    sensor_coords.append((ir_object['x'], ir_object['y']))
                # print(sensor_coords)

                self.mapping.calculate_source_to_dest(sensor_coords)

                # map data
                mapped_data = self.mapping.get_pointing_point()

                # print("MAPPED_DATA:", mapped_data)
                # print()

                # if self.paint_area.drawing:
                #     # rechts links vertauscht
                #     # self.paint_area.paint_objects.append(Pixel(mapped_data[1], mapped_data[0], self.paint_area.active_color, self.paint_area.active_size))
                #
                #     self.paint_area.paint_objects.append(
                #         Pixel(mapped_data[0], mapped_data[1], self.paint_area.active_color, 30))

                self.scrum_area.current_cursor_point = mapped_data

                self.scrum_area.update()

        if self.recognition_mode:
            test = self.scrum_area.current_cursor_point
            coord = self.scrum_area.current_cursor_point
            self.current_recording.append(coord)
            # # print(ir_data)
            #     self.paint_area.points.append(Pixel(mapped_data[0], mapped_data[1], self.paint_area.active_color, self.paint_area.active_size))
            #
            #     self.paint_area.current_cursor_point = (mapped_data[0], mapped_data[1])
            #
            #     self.paint_area.points.append(Pixel(100, 100, self.paint_area.active_color, self.paint_area.active_size))
            #     self.paint_area.points.append(Pixel(200, 100, self.paint_area.active_color, self.paint_area.active_size))
            #     self.paint_area.points.append(Pixel(300, 100, self.paint_area.active_color, self.paint_area.active_size))
            #     self.paint_area.points.append(Pixel(400, 100, self.paint_area.active_color, self.paint_area.active_size))
            #     self.paint_area.points.append(Pixel(500, 100, self.paint_area.active_color, self.paint_area.active_size))
            #     self.paint_area.points.append(Pixel(600, 100, self.paint_area.active_color, self.paint_area.active_size))
            #     self.paint_area.points.append(Pixel(700, 100, self.paint_area.active_color, self.paint_area.active_size))
            #     self.paint_area.points.append(Pixel(800, 100, self.paint_area.active_color, self.paint_area.active_size))
            #     self.paint_area.points.append(Pixel(900, 100, self.paint_area.active_color, self.paint_area.active_size))
            #
            #     self.paint_area.update()

    #Füllt grünen hintergrund beim connecten
    def fill_label_background(self, label, color):
        label.setAutoFillBackground(True)
        palette = label.palette()
        palette.setColor(label.backgroundRole(), color)
        label.setPalette(palette)


def main():
    app = QtWidgets.QApplication([])
    paint_app = PaintApplication()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
