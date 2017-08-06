import sys

from PyQt5 import uic, QtWidgets, QtCore, QtGui

import wiimote
from helper.gesturerecognition import GestureRecognition
from helper.mapwiimotedata import MapWiiMoteData
from helper.fileoperations import FileOperations
from model.Ticket import Ticket


class ScrumBoard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.wiimote = None

        self.config = None
        self.current_cursor_point = None
        self.b_is_pressed = False
        self.a_is_pressed = False
        self.mouse_is_released = False
        self.current_moving_ticket = None
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

    def init_ui(self):
        self.ui = uic.loadUi("scrum_board_interface.ui", self)
        self.ui.connection_button.clicked.connect(self.wiimote_check_connection_status)
        self.ui.connection_input.setText("18:2A:7B:F4:AC:23")
        self.config = self.file_operation.parse_setup()
        self.append_tickets_to_ui()
        self.ui.create_new_ticket.clicked.connect(lambda: self.make_new_ticket("ticket"))
        self.show()

    # ---------------------- WIIMOTE METHODS ----------------------

    # COMMENT
    def wiimote_check_connection_status(self):
        if self.wiimote is not None:
            self.wiimote_disconnect()
            return
        self.wiimote_connect()

    # COMMENT
    def wiimote_connect(self):
        address_to_connect = self.ui.connection_input.text()
        if address_to_connect is not "":
            self.wiimote = wiimote.connect(address_to_connect)

            if self.wiimote is not None:
                self.ui.connection_status.setStyleSheet('background-color:rgb(0, 170, 0); border-radius: 3px')
                self.ui.ir_1.setStyleSheet('background-color:rgb(0, 170, 0); border-radius: 3px')
                self.ui.connection_status_label.setText("WII MOTE CONNECTED")
                self.wiimote.buttons.register_callback(self.wiimote_button)
                self.wiimote.ir.register_callback(self.wiimote_infra_red_data)

    # COMMENT
    def wiimote_disconnect(self):
        self.wiimote.disconnect()
        self.wiimote = None
        self.ui.connection_button.setText("Connect")
        self.ui.connection_status.setStyleSheet('background-color:rgb(255, 0, 0); border-radius: 3px')
        self.ui.connection_status_label.setText("NO WII MOTE CONNECTED")

    # COMMENT
    def wiimote_button(self, event):
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
                        self.wiimote.rumble()
                    self.gesture_point_path = []

    # COMMENT
    def wiimote_infra_red_data(self, event):
        self.ui.ir_label.setText(str(len(event)))
        if len(event) is 4:
            vector_array = []
            for current_led in event:
                vector_array.append((current_led["x"], current_led["y"]))
            x, y = self.map_wii_mote_data.convert_vectors(vector_array, self.size().width(), self.size().height())
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

            if self.a_is_pressed:
                self.gesture_point_path.append((x, y))

    # ---------------------- MOUSE EVENT METHODS -------------------

    # COMMENT
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.ui.create_new_ticket.underMouse():
                self.make_new_ticket("ticket")

    # COMMENT
    def mouseMoveEvent(self, event):
        pos_x = event.pos().x()
        pos_y = event.pos().y()

        if event.buttons() & QtCore.Qt.LeftButton:
            ticket_under_mouse = self.get_ticket_under_mouse()
            if ticket_under_mouse is not None:
                ticket_under_mouse.setGeometry(pos_x, pos_y,
                                             ticket_under_mouse.size().width(), ticket_under_mouse.size().height())
                self.current_moving_ticket = ticket_under_mouse
                self.current_cursor_point = [pos_x, pos_y]

        if self.order_to_execute:
            self.order_to_execute
            self.execute_order()

        if self.move_ticket_left:
            self.move_ticket_left_method()

        if self.move_ticket_right:
            self.move_ticket_right_method()

        if self.wii_order_delete_ticket:
            self.wii_order_delete_ticket = False
            ticket_under_mouse = self.get_ticket_under_mouse()
            if ticket_under_mouse is not None:
                self.current_moving_ticket = ticket_under_mouse
                self.release_ticket(650, 100)

        if self.undo_last_order:
            self.undo_last_order = False
            self.undo_order_method()

        if self.save_current_state:
            self.save_current_state = False
            self.file_operation.save_setup(self.collect_data())

    # COMMENT
    def mouseReleaseEvent(self, event):
        self.release_ticket(event.pos().x(), event.pos().y())
        self.update()

    # ---------------------- PAINTING METHODS ----------------------

    # COMMENT
    def execute_order(self):
        if(self.order_to_execute == 1):
            self.make_new_ticket("ticket")
        if(self.order_to_execute == 2):
            self.make_new_ticket("bug")
        self.order_to_execute = None

    # COMMENT
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

    # COMMENT
    def get_distance_x_status(self, ticket_status):
        if(ticket_status == 0):
            return 0
        if(ticket_status == 1):
            return 435
        if(ticket_status == 2):
            return 880

    # COMMENT
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

    # COMMENT
    def move_ticket_left_method(self):
        ticket_under_mouse = self.get_ticket_under_mouse()
        if ticket_under_mouse is not None:
            if(ticket_under_mouse.status > 0):
                self.current_moving_ticket = ticket_under_mouse
                self.set_status(ticket_under_mouse.status - 1)

    # COMMENT
    def move_ticket_right_method(self):
        ticket_under_mouse = self.get_ticket_under_mouse()
        if ticket_under_mouse is not None:
            if (ticket_under_mouse.status < 2):
                self.current_moving_ticket = ticket_under_mouse
                self.set_status(ticket_under_mouse.status + 1)

    # COMMENT
    def get_ticket_under_mouse(self):
        for ticket in self.all_tickets:
            if ticket.underMouse() is True:
                return ticket
        return None

    # COMMENT
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

    # COMMENT
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

    # COMMENT
    def set_status(self, status_id):
        if self.current_moving_ticket:
            old_status = self.current_moving_ticket.status
            for element in self.config:
                if (element["id"] == self.current_moving_ticket.id):
                    element["status"] = status_id
                    self.current_moving_ticket.status = status_id
            self.set_y_index()
            self.move_ticket(status_id)
            self.update_old_row(old_status)

    # COMMENT
    def move_ticket(self, status):
        pos_y = 230 + ((self.y_index[status]-1)*150)
        pos_x = 20 + self.get_distance_x_status(status)
        self.current_moving_ticket.x = pos_x
        self.current_moving_ticket.y = pos_y
        self.current_moving_ticket.setGeometry(pos_x, pos_y,
                                             self.current_moving_ticket.size().width(), self.current_moving_ticket.size().height())
        self.update()
        self.move_ticket_left = False
        self.move_ticket_right = False

    # COMMENT
    def set_y_index(self):
        self.y_index = [0, 0, 0]
        for element in self.config:
            self.y_index[int(element["status"])] = self.y_index[int(element["status"])] + 1

    # COMMENT
    def update_old_row(self, status):
        counter = 0
        for ticket in self.all_tickets:
            if ticket.status == status:
                pos_y = 230 + (counter * 150)
                ticket.y = pos_y
                ticket.setGeometry(ticket.x, pos_y, self.current_moving_ticket.size().width(),
                                 self.current_moving_ticket.size().height())
                counter = counter + 1
        self.update()

    # COMMENT
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
        self.history_object.append({"order": "create", "obj": ticket})

    # COMMENT
    def delete_ticket(self):
        self.all_tickets.remove(self.current_moving_ticket)
        for element in self.config:
            if element["id"] == self.current_moving_ticket.id:
                self.config.remove(element)
        self.update_old_row(self.current_moving_ticket.status)
        self.current_moving_ticket.setParent(None)
        self.update()
        self.set_y_index()
        self.current_moving_ticket.setTitleText(self.current_moving_ticket.title_edit.toPlainText())
        self.current_moving_ticket.setAssignedToText(self.current_moving_ticket.assigned_to_edit.text())
        self.history_object.append({"order": "delete", "obj": self.current_moving_ticket})


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    scrum_board = ScrumBoard()
    sys.exit(app.exec_())
