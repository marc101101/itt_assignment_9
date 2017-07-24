# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import json
import os
import sys

from PyQt5 import uic, QtWidgets, QtCore, QtGui

import wiimote
from helper.gesturerecognition import GestureRecognition
from helper.vectortransform import VectorTransform
from model.card import Card


class ScrumBoard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.wiimote = None
        self.my_vector_transform = VectorTransform()
        self.gesturerecognition = GestureRecognition()
        self.setMouseTracking(True)
        self.config = None
        self.current_cursor_point = None
        self.b_is_pressed = False
        self.a_is_pressed = False
        self.order_to_execute = None
        self.gesture_point_path = []
        self.all_cards = []
        self.bg_colors = ['background-color: rgb(85, 170, 255)', 'background-color: red', 'background-color: green']
        self.init_ui()

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
                self.ui.ir_1.setStyleSheet('background-color:rgb(0, 170, 0)')
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
                if(button is "B"):
                    self.b_is_pressed = True
                if(button is "A"):
                    print("A pressed")
                    self.a_is_pressed = True
            else:
                if(button is "B"):
                    self.b_is_pressed = False
                if (button is "A"):
                    print("A release")
                    self.a_is_pressed = False
                    self.gesture_was_pressed = True
                    self.order_to_execute = self.gesturerecognition.get_current_gesture(self.gesture_point_path)
                    if(self.order_to_execute == 3):
                        print("Could not find fitting gesture")
                        self.wiimote.rumble()
                    self.gesture_point_path = []

    def on_wiimote_ir(self, event):
        self.ui.ir_label.setText(str(len(event)))
        if len(event) is 4:
            vectors = []
            for e in event:
                vectors.append((e["x"], e["y"]))
            x, y = self.my_vector_transform.transform(vectors, self.size().width(), self.size().height())
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))
            if self.b_is_pressed:
                card_under_mouse = self.get_card_under_mouse()
                if card_under_mouse is not None:
                    card_under_mouse.setGeometry(x, y, card_under_mouse.size().width(), card_under_mouse.size().height())
                    self.current_moving_card = card_under_mouse
                    self.current_cursor_point = [x, y]
            if self.a_is_pressed:
                self.gesture_point_path.append((x, y))

    def execute_order(self):
        if(self.order_to_execute == 0):
            print("Create BUG")
            self.make_new_card("bug")
        if(self.order_to_execute == 1):
            print("Create TASK")
            self.make_new_card("task")
        if(self.order_to_execute == 2):
            print("Create Epic")
            self.make_new_card("epic")
        self.order_to_execute = None

    def init_ui(self):
        self.ui = uic.loadUi("scrum_board_interface.ui", self)
        self.ui.connection_button.clicked.connect(self.toggle_wiimote_connection)
        self.ui.connection_input.setText("18:2A:7B:F4:AC:23")
        #self.ui.delete_card.setVisible(True)
        self.config = self.parse_setup("data_structure.json")
        self.append_cards_to_ui()
        self.ui.create_new_card.clicked.connect(lambda: self.make_new_card("task"))

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
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
            if self.ui.create_new_card.underMouse():
                self.make_new_card("task")

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            card_under_mouse = self.get_card_under_mouse()
            if card_under_mouse is not None:
                card_under_mouse.setGeometry(event.pos().x(), event.pos().y(),
                                             card_under_mouse.size().width(), card_under_mouse.size().height())
                self.current_moving_card = card_under_mouse
                self.current_cursor_point = [event.pos().x(), event.pos().y()]
        if(self.order_to_execute):
            self.execute_order()

    # def paintEvent(self, QPaintEvent):
        #print("paint")

    def get_card_under_mouse(self):
        for c in self.all_cards:
            if c.underMouse() is True:
                return c
        return None

    def mouseReleaseEvent(self, event):
        self.release_card(event.pos().x(), event.pos().y())

    def release_card(self, x, y):
        if (x <= 500):
            self.setStatus(0)
        if ((x >= 500) and (x <= 930)):
            self.setStatus(1)
        if (x >= 930):
            self.setStatus(2)
        self.append_cards_to_ui()
        self.current_moving_card = None

    def setStatus(self, status_id):
        for element in self.config["stored_elements"]:
            if (element["id"] == self.current_moving_card.id):
                element["status"] = status_id

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_B:
            print("Key B")
        if event.key() == QtCore.Qt.Key_A:
            print("Key A")

        if event.type() == QtCore.QEvent.HoverMove:
            print('hover' + str(event))
            self.lbl_new_card.setStyleSheet('background-color: blue')

    def make_new_card(self, type_element):
        new_id = len(self.config["stored_elements"]) + 1
        new_card_element = {
          "id": new_id,
          "title": "",
          "type": type_element,
          "assigned_to": "",
          "status": 0
        }
        self.config["stored_elements"].append(new_card_element)
        self.append_cards_to_ui()
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
