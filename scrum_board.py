# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import json
import os
import sys
import atexit

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
        self.mouse_is_released = False
        self.current_moving_card = None
        self.card_moved_by_wii = False
        self.order_to_execute = None
        self.undo_last_order = False
        self.move_card_right = False
        self.move_card_left = False
        self.wii_order_delete_card = False
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
                self.ui.connection_status.setStyleSheet('background-color:rgb(0, 170, 0); border-radius: 3px')
                self.ui.ir_1.setStyleSheet('background-color:rgb(0, 170, 0); border-radius: 3px')
                self.ui.connection_status_label.setText("WII MOTE CONNECTED")
                self.wiimote.buttons.register_callback(self.on_wiimote_button)
                self.wiimote.ir.register_callback(self.on_wiimote_ir)
                self.wiimote.rumble()

    def disconnect_wiimote(self):
        self.wiimote.disconnect()
        self.wiimote = None
        self.ui.connection_button.setText("Connect")
        self.ui.connection_status.setStyleSheet('background-color:rgb(255, 0, 0); border-radius: 3px')
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
                    #self.card_moved_by_wii = True
                if(button is "A"):
                    print("A pressed")
                    self.a_is_pressed = True
                if (button is "Left"):
                    self.move_card_left = True
                if (button is "Right"):
                    self.move_card_right = True
                if (button is "Down"):
                    print("SAVE")
                if (button is "Up"):
                    self.wii_order_delete_card = True
                    print("DELETE")
                if (button is "Plus"):
                    print("REDO")
                if (button is "Minus"):
                    print("UNDO")
            else:
                if(button is "B"):
                    self.b_is_pressed = False
                if (button is "A"):
                    print("A release")
                    self.a_is_pressed = False
                    self.gesture_was_pressed = True
                    self.order_to_execute = self.gesturerecognition.get_current_gesture(self.gesture_point_path)
                    if(self.order_to_execute == 0):
                        self.order_to_execute = 4
                    if(self.order_to_execute == 3):
                        print("Could not find fitting gesture")
                        self.wiimote.rumble()
                    self.gesture_point_path = []
                if (button is "Left"):
                    self.move_card_left = False
                if (button is "Right"):
                    self.move_card_right = False

    def on_wiimote_ir(self, event):
        self.ui.ir_label.setText(str(len(event)))
        if len(event) is 4:
            vector_array = []
            for current_led in event:
                vector_array.append((current_led["x"], current_led["y"]))
            x, y = self.my_vector_transform.transform(vector_array, self.size().width(), self.size().height())
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

            if self.a_is_pressed:
                print("appended")
                self.gesture_point_path.append((x, y))

    def execute_order(self):
        print("ORDER")
        if(self.order_to_execute == 4):
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
        self.config = self.parse_setup("data/data_structure.json")
        self.append_cards_to_ui()
        self.ui.create_new_card.clicked.connect(lambda: self.make_new_card("task"))

        self.show()

    def parse_setup(self, filename):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(os.path.join(location, filename)) as config_file:
                return json.load(config_file)
        except Exception as e:
            print("Exception: " + e)
            pass

    def save_setup(self, filename):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(filename, 'w') as outfile:
                json.dump(self.config, outfile)
        except Exception as e:
            print("Exception: " + e)
            pass

    def append_cards_to_ui(self):
        print(self.config)
        for card_element in self.all_cards:
            card_element.setParent(None)
            self.all_cards.remove(card_element)

        self.y_index = [0, 0, 0]
        self.all_cards = []
        for card_in_config in self.config["stored_elements"]:
            x_pos = 20 + self.get_distance_x_status(card_in_config["status"])
            y_pos = 230 + (self.y_index[card_in_config["status"]]*150)
            card = Card(self, card_in_config["id"], card_in_config["title"], card_in_config["type"],
                        card_in_config["assigned_to"], x_pos, y_pos, card_in_config["status"])
            self.y_index[card_in_config["status"]] = self.y_index[card_in_config["status"]] + 1

            card.setGeometry(x_pos, y_pos, card.size().width(), card.size().height())
            self.all_cards.append(card)

        print(self.y_index)

        self.update()

    def get_distance_x_status(self, card_status):
        if(card_status == 0):
            return 0
        if(card_status == 1):
            return 430
        if(card_status == 2):
            return 865

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.ui.create_new_card.underMouse():
                self.make_new_card("task")

    def mouseMoveEvent(self, event):
        pos_x = event.pos().x()
        pos_y = event.pos().y()

        if event.buttons() & QtCore.Qt.LeftButton:
            card_under_mouse = self.get_card_under_mouse()
            if card_under_mouse is not None:
                card_under_mouse.setGeometry(pos_x, pos_y,
                                             card_under_mouse.size().width(), card_under_mouse.size().height())
                self.current_moving_card = card_under_mouse
                self.current_cursor_point = [pos_x, pos_y]

        if self.order_to_execute:
            self.order_to_execute
            self.execute_order()

        if self.move_card_left:
            self.move_card_left_method()

        if self.move_card_right:
            self.move_card_right_method()

        if self.wii_order_delete_card:
            self.wii_order_delete_card = False
            card_under_mouse = self.get_card_under_mouse()
            if card_under_mouse is not None:
                self.current_moving_card = card_under_mouse
                self.release_card(650, 100)


    def move_card_left_method(self):
        print("LEFT")
        card_under_mouse = self.get_card_under_mouse()
        if card_under_mouse is not None:
            if(card_under_mouse.status > 0):
                self.current_moving_card = card_under_mouse
                self.setStatus(card_under_mouse.status - 1)

    def move_card_right_method(self):
        print("RIGHT")
        card_under_mouse = self.get_card_under_mouse()
        if card_under_mouse is not None:
            if (card_under_mouse.status < 2):
                self.current_moving_card = card_under_mouse
                self.setStatus(card_under_mouse.status + 1)

    def get_card_under_mouse(self):
        for card in self.all_cards:
            if card.underMouse() is True:
                return card
        return None

    def mouseReleaseEvent(self, event):
        self.release_card(event.pos().x(), event.pos().y())
        self.update()

    def release_card(self, x, y):
        if y < 110 and x > 645:
            self.delteCard()
        else:
            if (x <= 440):
                self.setStatus(0)
            if ((x >= 440) and (x <= 870)):
                self.setStatus(1)
            if (x >= 870):
                self.setStatus(2)

    def undo_last_order_method(self):
        print("undooo")

    def setStatus(self, status_id):
        if self.current_moving_card:
            old_status = self.current_moving_card.status
            for element in self.config["stored_elements"]:
                if (element["id"] == self.current_moving_card.id):
                    element["status"] = status_id
                    self.current_moving_card.status = status_id
            self.set_y_index()
            self.moveCard(status_id)
            self.updateOldRow(old_status)

    def moveCard(self, status):
        pos_y = 230 + ((self.y_index[status]-1)*150)
        pos_x = 20 + self.get_distance_x_status(status)
        self.current_moving_card.x = pos_x
        self.current_moving_card.y = pos_y
        self.current_moving_card.setGeometry(pos_x, pos_y,
                                             self.current_moving_card.size().width(), self.current_moving_card.size().height())
        self.update()

    def set_y_index(self):
        self.y_index = [0, 0, 0]
        for element in self.config["stored_elements"]:
            self.y_index[int(element["status"])] = self.y_index[int(element["status"])] + 1

    def updateOldRow(self, status):
        counter = 0
        for card in self.all_cards:
            if card.status == status:
                pos_y = 230 + (counter * 150)
                card.y = pos_y
                card.setGeometry(card.x, pos_y, self.current_moving_card.size().width(),
                                                self.current_moving_card.size().height())
                counter = counter + 1
        self.update()
        print(self.y_index)


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.LeftArrow:
            print("LEFT")
        if event.key() == QtCore.Qt.RightArrow:
            print("RIGHT")

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
        x_pos = 20 + self.get_distance_x_status(0)
        y_pos = 230 + (self.y_index[0] * 150)
        card = Card(self, new_id, "", type_element, "", x_pos, y_pos, 0)
        self.y_index[0] = self.y_index[0] + 1
        card.setGeometry(x_pos, y_pos, card.size().width(), card.size().height())
        self.all_cards.append(card)
        self.config["stored_elements"].append(new_card_element)

        print("make new card")

    def delteCard(self):
        self.all_cards.remove(self.current_moving_card)
        for element in self.config["stored_elements"]:
            if element["id"] == self.current_moving_card.id:
                self.config["stored_elements"].remove(element)
        self.updateOldRow(self.current_moving_card.status)
        self.current_moving_card.setParent(None)
        self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    scrum_board = ScrumBoard()
    #atexit.register(scrum_board.save_setup("data/data_structure.json"))
    sys.exit(app.exec_())
