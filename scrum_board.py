# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import os
import json
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget

import wiimote
from vectortransform import VectorTransform
from card import Card


class ScrumBoard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.CONNECTIONS_FILE = "wii.motes"
        self.wiimote = None
        self.my_vector_transform = VectorTransform()
        self.setMouseTracking(True)
        self.config = None
        self.all_cards = []
        self.bg_colors = ['background-color: rgb(85, 170, 255)', 'background-color: red', 'background-color: green']
        self.init_ui()

#------------------------------------------------------------------------

    def toggle_wiimote_connection(self):
        if self.wiimote is not None:
            self.disconnect_wiimote()
            return
        self.connect_wiimote()

    def connect_wiimote(self):
        address = self.ui.connection_input.text()
        if address is not "":
            try:
                self.wiimote = wiimote.connect(address)
            except Exception:
                QtWidgets.QMessageBox.critical(self, "Error", "Could not connect to " + address + "!")
                self.ui.btn_connect_wiimote.setText("Connect")
                return

            if self.wiimote is None:
                self.ui.btn_connect_wiimote.setText("Connect")
            else:
                self.ui.connection_button.setText("Disconnect")
                self.ui.connection_status.setStyleSheet('background-color:rgb(0, 170, 0)')
                self.ui.connection_status_label.setText("WII MOTE CONNECTED")
                self.wiimote.buttons.register_callback(self.on_wiimote_button)
                self.wiimote.ir.register_callback(self.on_wiimote_ir)
                self.wiimote.rumble()

    def disconnect_wiimote(self):
        self.wiimote.disconnect()
        self.wiimote = None
        self.ui.connection_button.setText("Connect")
        self.ui.connection_status.setStyleSheet('background-color:rgb(255, 0, 0)')
        self.ui.connection_status_label.setText("NO WII MOTE CONNECTED")

    def toggle_connection_frame(self, event):
        self.ui.fr_connection.setVisible(not self.ui.fr_connection.isVisible())

    def scan_for_wiimotes(self, event):
        self.ui.btn_scan_wiimotes.setText("Scanning...")
        self.ui.list_available_wiimotes.clear()
        results = wiimote.find()
        for mote in results:
            address, name = mote
            self.ui.list_available_wiimotes.addItem(address)
        if len(results) > 0:
            self.ui.list_available_wiimotes.setCurrentRow(0)
        self.ui.btn_scan_wiimotes.setText("Scan")

    def on_wiimote_button(self, event):
        if len(event) is not 0:
            button, is_pressed = event[0]
            if is_pressed:
                print("Button " + button + " is pressed")
            else:
                print("Button " + button + " is released")

    def on_wiimote_ir(self, event):

        if len(event) is 4:
            vectors = []
            for e in event:
                vectors.append((e["x"], e["y"]))
            x, y = self.my_vector_transform.transform(vectors, self.size().width(), self.size().height())
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))


#------------------------------------------------------------------------

    def init_ui(self):
        self.ui = uic.loadUi("scrum_board_interface.ui", self)
        self.ui.connection_button.clicked.connect(self.toggle_wiimote_connection)
        self.ui.connection_input.setText("18:2A:7B:F4:AC:23")

        #self.ui.delete_card.setVisible(True)
        self.config = self.parse_setup("data_structure.json")
        self.append_cards_to_ui()
        #self.all_cards.append(self.ui.scrumCard)

        self.show()

    def parse_setup(self, filename):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(os.path.join(location, filename)) as config_file:
                return json.load(config_file)
        except Exception as e:
            print("Exception: " + e)
            pass

    def append_cards_to_ui(self):
        for card_element in self.all_cards:
            card_element.setParent(None)
            self.all_cards.remove(card_element)
        y_index = [0, 0, 0]
        for card_in_config in self.config["stored_elements"]:
            card = Card(self, card_in_config["id"], card_in_config["title"], card_in_config["type"], card_in_config["assigned_to"])
            x_pos = 15 + self.get_distance_x_status(card_in_config["status"])
            y_pos = 230 + (y_index[card_in_config["status"]]*150)
            y_index[card_in_config["status"]] = y_index[card_in_config["status"]] + 1

            card.setGeometry(x_pos, y_pos, card.size().width(), card.size().height())
            self.all_cards.append(card)

    def get_distance_x_status(self, card_status):
        if(card_status == 0):
            return 0
        if(card_status == 1):
            return 500
        if(card_status == 2):
            return 930

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            pos = QtGui.QCursor.pos()
            widget_at = QApplication.widgetAt(pos)
            style = str(widget_at.styleSheet())
            print(style)
            if 'rgb(85, 170, 255)' in style:
                self.fr_card.setStyleSheet(self.bg_colors[1])
            elif 'red' in style:
                self.fr_card.setStyleSheet(self.bg_colors[2])
            else:
                self.fr_card.setStyleSheet(self.bg_colors[0])

        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
            if self.ui.create_new_card.underMouse():
                self.make_new_card(event)
        # super(IPlanPy, self).mousePressEvent(event)
        # print("mousePressEvent" + str(self.__mousePressPos) + ' ' + str(self.__mouseMovePos))

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            print("mouse move")
            print(len(self.all_cards))
            card_under_mouse = self.get_card_under_mouse()
            if card_under_mouse is not None:
                card_under_mouse.setGeometry(event.pos().x(), event.pos().y(),
                                             card_under_mouse.size().width(), card_under_mouse.size().height())
                self.current_moving_card = card_under_mouse

        if event.buttons() == QtCore.Qt.LeftButton:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.__mouseMovePos = globalPos

    def get_card_under_mouse(self):
        for c in self.all_cards:
            if c.underMouse() is True:
                return c
        return None

    def mouseReleaseEvent(self, event):
        print(self.current_moving_card.id)
        if(event.pos().x() <= 500):
            print("BACKLOG")
        if ((event.pos().x() >= 500) and (event.pos().x())):
            print("TODO")
        if (event.pos().x() >= 930):
            print("DONE")
        self.append_cards_to_ui()
        # if self.__mousePressPos is not None:
        #     moved = event.globalPos() - self.__mousePressPos
        #     self.register_if_deleted(event.pos().x(), event.pos().y())
        #     if moved.manhattanLength() > 3:
        #         event.ignore()
        #         return

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_B:
            print("Key B")
        if event.key() == QtCore.Qt.Key_A:
            print("Key A")

        if event.type() == QtCore.QEvent.HoverMove:
            print('hover' + str(event))
            self.lbl_new_card.setStyleSheet('background-color: blue')

    def make_new_card(self, event):
        card = Card(self)
        card.setGeometry(event.pos().x() - 10, event.pos().y() - 10, card.size().width(), card.size().height())
        self.all_cards.append(card)
        print("make new card")

    def register_if_deleted(self, posX, posY):
        delete_button_pos_x1 = self.delete_card.x()
        delete_button_pos_x2 = delete_button_pos_x1 + self.delete_card.width()
        delete_button_pos_y1 = self.delete_card.y()
        delete_button_pos_y2 = delete_button_pos_y1 + self.delete_card.height()
        if delete_button_pos_x2 >= posX >= delete_button_pos_x1 and delete_button_pos_y1 <= posY <= delete_button_pos_y2:
            card = self.get_card_under_mouse()
            card.setParent(None)
            self.all_cards.remove(card)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    scrum_board = ScrumBoard()
    sys.exit(app.exec_())
