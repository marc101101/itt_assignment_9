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
from helper.mapwiimotedata import MapWiiMoteData
from model.task import Task


class ScrumBoard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.wiimote = None

        self.config = None
        self.current_cursor_point = None
        self.b_is_pressed = False
        self.a_is_pressed = False
        self.mouse_is_released = False
        self.current_moving_task = None
        self.task_moved_by_wii = False
        self.order_to_execute = None
        self.undo_last_order = False
        self.move_task_right = False
        self.move_task_left = False
        self.save_current_state = False
        self.wii_order_delete_task = False

        self.history_index = 0
        self.gesture_point_path = []
        self.all_tasks = []
        self.history_object = []
        self.filename = "data/data_structure.json"
        self.bg_colors = ['background-color: rgb(85, 170, 255)', 'background-color: red', 'background-color: green']

        self.map_wii_mote_data = MapWiiMoteData()
        self.gesture_recognition = GestureRecognition()
        self.setMouseTracking(True)
        self.init_ui()

    def toggle_wiimote_connection(self):
        if self.wiimote is not None:
            self.wiimote_disconnect()
            return
        self.wiimote_connect()

    def wiimote_connect(self):
        address_to_connect = self.ui.connection_input.text()
        if address_to_connect is not "":
            self.wiimote = wiimote.connect(address_to_connect)

            if self.wiimote is not None:
                self.ui.connection_status.setStyleSheet('background-color:rgb(0, 170, 0); border-radius: 3px')
                self.ui.ir_1.setStyleSheet('background-color:rgb(0, 170, 0); border-radius: 3px')
                self.ui.connection_status_label.setText("WII MOTE CONNECTED")
                self.wiimote.buttons.register_callback(self.on_wiimote_button)
                self.wiimote.ir.register_callback(self.on_wiimote_ir)

    def wiimote_disconnect(self):
        self.wiimote.disconnect()
        self.wiimote = None
        self.ui.connection_button.setText("Connect")
        self.ui.connection_status.setStyleSheet('background-color:rgb(255, 0, 0); border-radius: 3px')
        self.ui.connection_status_label.setText("NO WII MOTE CONNECTED")

    def on_wiimote_button(self, event):
        if len(event) is not 0:
            button, is_pressed = event[0]
            if is_pressed:
                if(button is "B"):
                    self.b_is_pressed = True
                if(button is "A"):
                    self.a_is_pressed = True
                if (button is "Left") and (self.move_task_left == False):
                    self.move_task_left = True
                if (button is "Right") and (self.move_task_right == False):
                    self.move_task_right = True
                if (button is "Down"):
                    self.save_current_state = True
                if (button is "Up"):
                    self.wii_order_delete_task = True
                if (button is "Minus"):
                    self.undo_last_order = True
            else:
                if(button is "B"):
                    self.b_is_pressed = False
                if (button is "A"):
                    self.a_is_pressed = False
                    self.gesture_was_pressed = True
                    self.order_to_execute = self.gesture_recognition.get_current_gesture(self.gesture_point_path)
                    if(self.order_to_execute == 3):
                        self.wiimote.rumble()
                    self.gesture_point_path = []

    def on_wiimote_ir(self, event):
        self.ui.ir_label.setText(str(len(event)))
        if len(event) is 4:
            vector_array = []
            for current_led in event:
                vector_array.append((current_led["x"], current_led["y"]))
            x, y = self.map_wii_mote_data.convert_vectors(vector_array, self.size().width(), self.size().height())
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

            if self.a_is_pressed:
                self.gesture_point_path.append((x, y))

    def execute_order(self):
        if(self.order_to_execute == 1):
            self.make_new_task("task")
        if(self.order_to_execute == 2):
            self.make_new_task("bug")
        self.order_to_execute = None

    def init_ui(self):
        self.ui = uic.loadUi("scrum_board_interface.ui", self)
        self.ui.connection_button.clicked.connect(self.toggle_wiimote_connection)
        self.ui.connection_input.setText("18:2A:7B:F4:AC:23")
        self.config = self.parse_setup()
        self.append_tasks_to_ui()
        self.ui.create_new_task.clicked.connect(lambda: self.make_new_task("task"))
        self.show()

    def parse_setup(self):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(os.path.join(location, self.filename)) as config_file:
                return json.load(config_file)
        except Exception as e:
            print("Exception: " + e)
            pass

    def save_setup(self, elements_to_store):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(self.filename, 'w') as outfile:
                json.dump(elements_to_store, outfile)
        except Exception as e:
            print("Exception: " + e)
            pass

    def append_tasks_to_ui(self):
        for task_elements in self.all_tasks:
            task_elements.setParent(None)
            self.all_tasks.remove(task_elements)

        self.y_index = [0, 0, 0]
        self.all_tasks = []
        for task_in_config in self.config:
            x_pos = 20 + self.get_distance_x_status(task_in_config["status"])
            y_pos = 230 + (self.y_index[task_in_config["status"]]*150)
            task = Task(self, task_in_config["id"], task_in_config["title"], task_in_config["type"],
                        task_in_config["assigned_to"], x_pos, y_pos, task_in_config["status"])
            self.y_index[task_in_config["status"]] = self.y_index[task_in_config["status"]] + 1

            task.setGeometry(x_pos, y_pos, task.size().width(), task.size().height())
            self.all_tasks.append(task)

        self.update()

    def get_distance_x_status(self, task_status):
        if(task_status == 0):
            return 0
        if(task_status == 1):
            return 435
        if(task_status == 2):
            return 880

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.ui.create_new_task.underMouse():
                self.make_new_task("task")

    def mouseMoveEvent(self, event):
        pos_x = event.pos().x()
        pos_y = event.pos().y()

        if event.buttons() & QtCore.Qt.LeftButton:
            task_under_mouse = self.get_task_under_mouse()
            if task_under_mouse is not None:
                task_under_mouse.setGeometry(pos_x, pos_y,
                                             task_under_mouse.size().width(), task_under_mouse.size().height())
                self.current_moving_task = task_under_mouse
                self.current_cursor_point = [pos_x, pos_y]

        if self.order_to_execute:
            self.order_to_execute
            self.execute_order()

        if self.move_task_left:
            self.move_task_left_method()

        if self.move_task_right:
            self.move_task_right_method()

        if self.wii_order_delete_task:
            self.wii_order_delete_task = False
            task_under_mouse = self.get_task_under_mouse()
            if task_under_mouse is not None:
                self.current_moving_task = task_under_mouse
                self.release_task(650, 100)

        if self.undo_last_order:
            self.undo_last_order = False
            self.undo_order_method()

        if self.save_current_state:
            self.save_current_state = False
            self.save_setup(self.collect_data())

    def collect_data(self):
        elements_to_store = []
        for task in self.all_tasks:
            elements_to_store.append({
                "id": task.id,
                "title": task.title_edit.text(),
                "type": task.type_edit.text(),
                "assigned_to": task.assigned_to_edit.text(),
                "status": task.status
            })
        return elements_to_store

    def move_task_left_method(self):
        task_under_mouse = self.get_task_under_mouse()
        if task_under_mouse is not None:
            if(task_under_mouse.status > 0):
                self.current_moving_task = task_under_mouse
                self.setStatus(task_under_mouse.status - 1)

    def move_task_right_method(self):
        task_under_mouse = self.get_task_under_mouse()
        if task_under_mouse is not None:
            if (task_under_mouse.status < 2):
                self.current_moving_task = task_under_mouse
                self.setStatus(task_under_mouse.status + 1)

    def get_task_under_mouse(self):
        for task in self.all_tasks:
            if task.underMouse() is True:
                return task
        return None

    def mouseReleaseEvent(self, event):
        self.release_task(event.pos().x(), event.pos().y())
        self.update()

    def release_task(self, x, y):
        if y < 110 and x > 645:
            self.delteTask()
        else:
            if (x <= 440):
                self.setStatus(0)
            if ((x >= 440) and (x <= 870)):
                self.setStatus(1)
            if (x >= 870):
                self.setStatus(2)

    def undo_order_method(self):
        if len(self.history_object) != 0:
            last_order = self.history_object[len(self.history_object) - (self.history_index + 1)]
            self.history_index = self.history_index + 1
            if last_order["order"] == "delete":
                self.set_y_index()
                new_task_element = {
                    "id": last_order["obj"].id,
                    "title": last_order["obj"].title_text,
                    "type": last_order["obj"].type_text,
                    "assigned_to": last_order["obj"].assigned_to_text,
                    "status": last_order["obj"].status
                }
                x_pos = 20 + self.get_distance_x_status(0)
                y_pos = 230 + (self.y_index[0] * 150)
                task = Task(self, last_order["obj"].id, last_order["obj"].title_text, last_order["obj"].type_text,
                            last_order["obj"].assigned_to_text, x_pos, y_pos, last_order["obj"].status)
                self.y_index[0] = self.y_index[0] + 1
                task.setGeometry(x_pos, y_pos, task.size().width(), task.size().height())
                self.all_tasks.append(task)
                self.config.append(new_task_element)

                self.history_object[len(self.history_object) - 1]["order"] = "create"
                self.history_object[len(self.history_object) - 1]["obj"] = task

            self.update()

    def setStatus(self, status_id):
        if self.current_moving_task:
            old_status = self.current_moving_task.status
            for element in self.config:
                if (element["id"] == self.current_moving_task.id):
                    element["status"] = status_id
                    self.current_moving_task.status = status_id
            self.set_y_index()
            self.moveTask(status_id)
            self.updateOldRow(old_status)

    def moveTask(self, status):
        pos_y = 230 + ((self.y_index[status]-1)*150)
        pos_x = 20 + self.get_distance_x_status(status)
        self.current_moving_task.x = pos_x
        self.current_moving_task.y = pos_y
        self.current_moving_task.setGeometry(pos_x, pos_y,
                                             self.current_moving_task.size().width(), self.current_moving_task.size().height())
        self.update()
        self.move_task_left = False
        self.move_task_right = False


    def set_y_index(self):
        self.y_index = [0, 0, 0]
        for element in self.config:
            self.y_index[int(element["status"])] = self.y_index[int(element["status"])] + 1

    def updateOldRow(self, status):
        counter = 0
        for task in self.all_tasks:
            if task.status == status:
                pos_y = 230 + (counter * 150)
                task.y = pos_y
                task.setGeometry(task.x, pos_y, self.current_moving_task.size().width(),
                                 self.current_moving_task.size().height())
                counter = counter + 1
        self.update()

    def make_new_task(self, type_element):
        new_id = len(self.config) + 1
        new_task_element = {
          "id": new_id,
          "title": "",
          "type": type_element,
          "assigned_to": "",
          "status": 0
        }
        x_pos = 20 + self.get_distance_x_status(0)
        y_pos = 230 + (self.y_index[0] * 150)
        task = Task(self, new_id, "", type_element, "", x_pos, y_pos, 0)
        self.y_index[0] = self.y_index[0] + 1
        task.setGeometry(x_pos, y_pos, task.size().width(), task.size().height())
        self.all_tasks.append(task)
        self.config.append(new_task_element)
        self.history_object.append({"order": "create", "obj": task})

    def delteTask(self):
        self.all_tasks.remove(self.current_moving_task)
        for element in self.config:
            if element["id"] == self.current_moving_task.id:
                self.config.remove(element)
        self.updateOldRow(self.current_moving_task.status)
        self.current_moving_task.setParent(None)
        self.update()
        self.set_y_index()
        self.history_object.append({"order": "delete", "obj": self.current_moving_task})


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    scrum_board = ScrumBoard()
    sys.exit(app.exec_())
