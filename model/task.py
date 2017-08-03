# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QFrame, QLineEdit, QPlainTextEdit, QLabel


class Task(QFrame):
    def __init__(self, parent, id, title_text, type_text, assigned_to_text, x, y, status):
        super(Task, self).__init__()
        self.id = id
        self.title_text = title_text
        self.type_text = type_text
        self.assigned_to_text = assigned_to_text
        self.x = x
        self.y = y
        self.status = status

        self.tpye_frame = QLabel()
        self.setParent(parent)
        self.title = QLabel()
        self.title_edit = QLineEdit()
        self.type = QLabel()
        self.type_edit = QLineEdit()
        self.assigned_to = QLabel()
        self.assigned_to_edit = QLineEdit()

        self.setup_frame()
        self.setup_title()
        self.setup_type()
        self.setup_assigned_to()
        self.setMouseTracking(True)

    def getColor(self):
        print(self.type_text)
        if self.type_text == "task":
            return "#388e3c"
        if self.type_text == "epic":
            return "#7c4dff"
        if self.type_text == "bug":
            return "#ff5252"

    def setup_frame(self):
        self.setStyleSheet('background-color: white; border-radius: 3px')
        self.resize(390, 130)
        self.setVisible(True)

    def setup_title(self):
        self.tpye_frame.setParent(self)
        self.tpye_frame.resize(5, 140)
        self.tpye_frame.move(0, 0)
        self.tpye_frame.setStyleSheet('background-color: ' + str(self.getColor()) + '; border-radius: 3px')
        self.tpye_frame.setVisible(True)

        self.title.resize(68, 21)
        self.title.move(20, 10)
        self.title.setText("TITLE:")
        self.title.setParent(self)
        self.title.setStyleSheet('background-color: white')
        self.title.setVisible(True)

        self.title_edit.resize(260, 21)
        self.title_edit.move(120, 10)
        self.title_edit.setText(self.title_text)
        self.title_edit.setParent(self)
        self.title_edit.setStyleSheet('background-color: white;')
        self.title_edit.setVisible(True)

    def setup_type(self):
        self.type.resize(68, 21)
        self.type.move(20, 50)
        self.type.setText("TYPE:")
        self.type.setParent(self)
        self.type.setStyleSheet('background-color: white')
        self.type.setVisible(True)

        self.type_edit.resize(260, 21)
        self.type_edit.move(120, 50)
        self.type_edit.setText(self.type_text)
        self.type_edit.setParent(self)
        self.type_edit.setStyleSheet('background-color: white')
        self.type_edit.setVisible(True)

    def setup_assigned_to(self):
        self.assigned_to.resize(68, 21)
        self.assigned_to.move(20, 90)
        self.assigned_to.setText("ASSIGN:")
        self.assigned_to.setParent(self)
        self.assigned_to.setStyleSheet('background-color: white')
        self.assigned_to.setVisible(True)

        self.assigned_to_edit.resize(260, 21)
        self.assigned_to_edit.move(120, 90)
        self.assigned_to_edit.setText(self.assigned_to_text)
        self.assigned_to_edit.setParent(self)
        self.assigned_to_edit.setStyleSheet('background-color: white')
        self.assigned_to_edit.setVisible(True)

