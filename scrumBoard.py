#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# This file was edited by Gina Maria Wolf and Markus Guder

import sys

from PyQt5 import QtWidgets, QtCore, uic, QtGui

import wiimote
from helper.gesturerecognition import GestureRecognition
from helper.mapwiimotedata import MapWiiMoteData
from helper.fileoperations import FileOperations
from model.Ticket import Ticket


class ScrumBoard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.wiimote_controller = None

        self.config = None
        self.current_cursor_point = None
        self.b_is_pressed = False
        self.a_is_pressed = False
        self.mouse_is_released = False
        self.moving_ticket = None
        self.ticket_moved_by_wii = False
        self.order_to_execute = None
        self.undo_last_order = False
        self.move_ticket_right = False
        self.move_ticket_left = False
        self.save_current_state = False
        self.wii_order_delete_ticket = False

        self.history_index = 0
        self.gesture_point_path = []
        self.all_tickets = []
        self.history_object = []
        self.filename = "../data/data_structure.json"
        self.bg_colors = ['background-color: rgb(85, 170, 255)', 'background-color: red', 'background-color: green']

        self.map_wii_mote_data = MapWiiMoteData()
        self.gesture_recognition = GestureRecognition()
        self.file_operation = FileOperations(self.filename)

        self.setMouseTracking(True)

        self.init_ui()

    # Inits the basic ui elements by loading the .ui file
    def init_ui(self):
        self.ui = uic.loadUi("scrum_board_interface.ui", self)
        self.ui.connection_button.clicked.connect(self.wiimote_check_connection_status)
        self.ui.connection_input.setText("18:2A:7B:F4:AC:23")
        self.config = self.file_operation.parse_setup()

        self.append_tickets_to_ui()
        self.ui.create_new_ticket.clicked.connect(lambda: self.make_new_ticket("ticket"))
        self.show()

    # ---------------------- WIIMOTE METHODS ----------------------

    # Checks if a the wiimote controller is connected or not
    def wiimote_check_connection_status(self):
        if self.wiimote_controller is None:
            self.wiimote_connect()

        if self.wiimote_controller is not None:
            self.wiimote_disconnect()
            return


    # Connects to wiimote controller and updates ui elements which should a successful connection
    def wiimote_connect(self):
        address_to_connect = self.ui.connection_input.text()
        if address_to_connect is not "":
            self.wiimote_controller = wiimote.connect(address_to_connect)

            if self.wiimote_controller is not None:
                self.ui.connection_status.setStyleSheet('background-color:rgb(0, 170, 0); border-radius: 3px')
                self.ui.ir_1.setStyleSheet('background-color:rgb(0, 170, 0); border-radius: 3px')
                self.ui.connection_status_label.setText("WII MOTE CONNECTED")
                self.wiimote_controller.buttons.register_callback(self.wiimote_button_pressed)
                self.wiimote_controller.ir.register_callback(self.wiimote_infra_red_data)

    # Disconnects wii controller
    def wiimote_disconnect(self):
        self.wiimote_controller.disconnect()
        self.ui.connection_button.setText("Connect")
        self.ui.connection_status.setStyleSheet('background-color:rgb(255, 0, 0); border-radius: 3px')
        self.ui.connection_status_label.setText("NO WII MOTE CONNECTED")
        self.wiimote_controller = None

    # Handels any pressed button event
    def wiimote_button_pressed(self, event):
        if len(event) is not 0:
            button, is_pressed = event[0]
            if is_pressed:
                if(button is "B"):
                    self.b_is_pressed = True
                if(button is "A"):
                    self.a_is_pressed = True
                if (button is "Left") and (self.move_ticket_left == False):
                    self.move_ticket_left = True
                if (button is "Right") and (self.move_ticket_right == False):
                    self.move_ticket_right = True
                if (button is "Down"):
                    self.save_current_state = True
                if (button is "Up"):
                    self.wii_order_delete_ticket = True
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
                        self.wiimote_controller.rumble()
                    self.gesture_point_path = []

    # Handels the received infra red data to the map_wii_mote_data class
    # Receives x and y position for cursor
    # If A is pressed all points are added to the gesture recognition array
    def wiimote_infra_red_data(self, event):
        self.ui.ir_label.setText(str(len(event)))
        if len(event) is 4:
            led_array = []
            for received_led in event:
                led_array.append((received_led["x"], received_led["y"]))
            x, y = self.map_wii_mote_data.convert_vectors(led_array, self.size().width(), self.size().height())
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

            if self.a_is_pressed:
                self.gesture_point_path.append((x, y))

    # ---------------------- MOUSE EVENT METHODS -------------------

    # Receives mouse move events
    # Handels the movement of tiles by mouse by binding their position to the mouse
    def mouseMoveEvent(self, event):
        pos_x = event.pos().x()
        pos_y = event.pos().y()

        if event.buttons() & QtCore.Qt.LeftButton:
            ticket_selected_by_mouse = self.get_ticket_selected_by_mouse()
            if ticket_selected_by_mouse is not None:
                ticket_selected_by_mouse.setGeometry(pos_x, pos_y,
                                             ticket_selected_by_mouse.size().width(), ticket_selected_by_mouse.size().height())
                self.moving_ticket = ticket_selected_by_mouse
                self.current_cursor_point = [pos_x, pos_y]

        self.handle_event_data()

    # Handels every event by checking the values which where set by wiimote thread
    def handle_event_data(self):
        if self.order_to_execute:
            self.order_to_execute
            self.execute_order()
        if self.move_ticket_left:
            self.move_ticket_left_method()
        if self.move_ticket_right:
            self.move_ticket_right_method()
        if self.wii_order_delete_ticket:
            self.wii_order_delete_ticket = False
            ticket_selected_by_mouse = self.get_ticket_selected_by_mouse()
            if ticket_selected_by_mouse is not None:
                self.moving_ticket = ticket_selected_by_mouse
                self.release_ticket(650, 100)
        if self.undo_last_order:
            self.undo_last_order = False
            self.undo_order_method()
        if self.save_current_state:
            self.save_current_state = False
            self.file_operation.save_setup(self.collect_data())

    # Event that is thrown if the mouse releases a ticket
    def mouseReleaseEvent(self, event):
        self.release_ticket(event.pos().x(), event.pos().y())
        self.update()

    # ---------------------- PAINTING METHODS ----------------------

    # Executes order by processing the status code returned from the gesture recognition class
    def execute_order(self):
        if(self.order_to_execute == 1):
            self.make_new_ticket("ticket")
        if(self.order_to_execute == 2):
            self.make_new_ticket("bug")
        self.order_to_execute = None

    # Initaly adds all tickets from datastructure.json to the ui
    def append_tickets_to_ui(self):
        for ticket_elements in self.all_tickets:
            ticket_elements.setParent(None)
            self.all_tickets.remove(ticket_elements)

        self.y_index = [0, 0, 0]
        self.all_tickets = []
        for ticket_in_config in self.config:
            x_pos = 20 + self.get_distance_x_status(ticket_in_config["status"])
            y_pos = 230 + (self.y_index[ticket_in_config["status"]]*150)
            ticket = Ticket(self, ticket_in_config["id"], ticket_in_config["title"], ticket_in_config["type"],
                        ticket_in_config["assigned_to"], x_pos, y_pos, ticket_in_config["status"])
            self.y_index[ticket_in_config["status"]] = self.y_index[ticket_in_config["status"]] + 1

            ticket.setGeometry(x_pos, y_pos, ticket.size().width(), ticket.size().height())
            self.all_tickets.append(ticket)

        self.update()

    # Calculates x distance for the drawing methods
    def get_distance_x_status(self, ticket_status):
        if(ticket_status == 0):
            return 0
        if(ticket_status == 1):
            return 435
        if(ticket_status == 2):
            return 880

    # Collects all data / new data from all tickets before they got saved
    def collect_data(self):
        elements_to_store = []
        for ticket in self.all_tickets:
            elements_to_store.append({
                "id": ticket.id,
                "title": ticket.title_edit.text(),
                "type": ticket.type_edit.text(),
                "assigned_to": ticket.assigned_to_edit.text(),
                "status": ticket.status
            })
        return elements_to_store

    # Checks if ticket is selected by mouse and moves the ticket left
    # if possible depending on its current position
    def move_ticket_left_method(self):
        ticket_selected_by_mouse = self.get_ticket_selected_by_mouse()
        if ticket_selected_by_mouse is not None:
            if(ticket_selected_by_mouse.status > 0):
                self.moving_ticket = ticket_selected_by_mouse
                self.set_status(ticket_selected_by_mouse.status - 1)

    # Checks if ticket is selected by mouse and moves the ticket right
    # if possible depending on its current position
    def move_ticket_right_method(self):
        ticket_selected_by_mouse = self.get_ticket_selected_by_mouse()
        if ticket_selected_by_mouse is not None:
            if (ticket_selected_by_mouse.status < 2):
                self.moving_ticket = ticket_selected_by_mouse
                self.set_status(ticket_selected_by_mouse.status + 1)

    # Checks every ticket in all_tickets array
    # and returns the selected by mouse ticket
    # else it returns none and nothing happens
    def get_ticket_selected_by_mouse(self):
        ticket_in_list = None
        for ticket in self.all_tickets:
            if ticket.underMouse() is True:
                ticket_in_list = ticket
        return ticket_in_list

    # If a ticket got released by the mouse
    # The method checks if the ticket is over the delete area
    # if not it checks in which board area it is by checking its x position
    # and updates its status
    def release_ticket(self, x, y):
        if y < 110 and x > 645:
            self.delete_ticket()
        else:
            if (x <= 440):
                self.set_status(0)
            if ((x >= 440) and (x <= 870)):
                self.set_status(1)
            if (x >= 870):
                self.set_status(2)

    # Recreates deletet ticket by creating a new ticket based on the stored ticket in the history_object
    def undo_order_method(self):
        if len(self.history_object) != 0:
            last_order = self.history_object[len(self.history_object) - (self.history_index + 1)]
            self.history_index = self.history_index + 1
            if last_order["order"] == "delete":
                self.set_y_index()
                new_ticket_element = {
                    "id": last_order["obj"].id,
                    "title": last_order["obj"].title_text,
                    "type": last_order["obj"].type_text,
                    "assigned_to": last_order["obj"].assigned_to_text,
                    "status": last_order["obj"].status
                }
                x_pos = 20 + self.get_distance_x_status(0)
                y_pos = 230 + (self.y_index[0] * 150)
                ticket = Ticket(self, last_order["obj"].id, last_order["obj"].title_text, last_order["obj"].type_text,
                            last_order["obj"].assigned_to_text, x_pos, y_pos, last_order["obj"].status)
                self.y_index[0] = self.y_index[0] + 1
                ticket.setGeometry(x_pos, y_pos, ticket.size().width(), ticket.size().height())
                self.all_tickets.append(ticket)
                self.config.append(new_ticket_element)

                self.history_object[len(self.history_object) - 1]["order"] = "create"
                self.history_object[len(self.history_object) - 1]["obj"] = ticket

            self.update()

    # Updates the status of the moved card
    # and orders to update the old row, to move the card and the y_index
    def set_status(self, status_id):
        if self.moving_ticket:
            old_status = self.moving_ticket.status
            for element in self.config:
                if (element["id"] == self.moving_ticket.id):
                    element["status"] = status_id
                    self.moving_ticket.status = status_id
            self.set_y_index()
            self.move_ticket(status_id)
            self.update_old_row(old_status)

    # Drawing method which draws the moved card on its new position
    def move_ticket(self, status):
        pos_y = 230 + ((self.y_index[status]-1)*150)
        pos_x = 20 + self.get_distance_x_status(status)
        self.moving_ticket.x = pos_x
        self.moving_ticket.y = pos_y
        self.moving_ticket.setGeometry(pos_x, pos_y,
                                       self.moving_ticket.size().width(), self.moving_ticket.size().height())
        self.update()
        self.move_ticket_left = False
        self.move_ticket_right = False

    # Updates the y_index which describes how many card there are in an area
    def set_y_index(self):
        self.y_index = [0, 0, 0]
        for element in self.config:
            self.y_index[int(element["status"])] = self.y_index[int(element["status"])] + 1

    # Updates the row from which a card is moved away by resetting the y positions
    def update_old_row(self, status):
        counter = 0
        for ticket in self.all_tickets:
            if ticket.status == status:
                pos_y = 230 + (counter * 150)
                ticket.y = pos_y
                ticket.setGeometry(ticket.x, pos_y, self.moving_ticket.size().width(),
                                   self.moving_ticket.size().height())
                counter = counter + 1
        self.update()

    # Creates new card by adding a new element to the config array and to the all_tickets array
    def make_new_ticket(self, type_element):
        new_id = len(self.config) + 1
        new_ticket_element = {
          "id": new_id,
          "title": "",
          "type": type_element,
          "assigned_to": "",
          "status": 0
        }
        x_pos = 20 + self.get_distance_x_status(0)
        y_pos = 230 + (self.y_index[0] * 150)
        ticket = Ticket(self, new_id, "", type_element, "", x_pos, y_pos, 0)
        self.y_index[0] = self.y_index[0] + 1
        ticket.setGeometry(x_pos, y_pos, ticket.size().width(), ticket.size().height())
        self.all_tickets.append(ticket)
        self.config.append(new_ticket_element)

    # Deletes moved ticket
    # but stores the element in the history_object to enable the undo methdo to recreate it
    def delete_ticket(self):
        self.all_tickets.remove(self.moving_ticket)
        for element in self.config:
            if element["id"] == self.moving_ticket.id:
                self.config.remove(element)
        self.update_old_row(self.moving_ticket.status)
        self.moving_ticket.setParent(None)
        self.update()
        self.set_y_index()
        self.moving_ticket.setTitleText(self.moving_ticket.title_edit.toPlainText())
        self.moving_ticket.setAssignedToText(self.moving_ticket.assigned_to_edit.text())
        self.history_object.append({"order": "delete", "obj": self.moving_ticket})


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    scrum_board = ScrumBoard()
    sys.exit(app.exec_())
