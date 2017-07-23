# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QFrame, QLineEdit, QPlainTextEdit, QLabel


class Card(QFrame):
    def __init__(self, parent, id, title_text, type_text, assigned_to_text):
        super(Card, self).__init__()
        self.id = id
        self.title_text = title_text
        self.type_text = type_text
        self.assigned_to_text = assigned_to_text

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

    def setup_frame(self):
        self.setStyleSheet('background-color: white')
        self.resize(390, 130)
        self.setVisible(True)

    def setup_title(self):
        self.title.resize(68, 21)
        self.title.move(10, 10)
        self.title.setText("TITLE:")
        self.title.setParent(self)
        self.title.setStyleSheet('background-color: white')
        self.title.setVisible(True)

        self.title_edit.resize(260, 21)
        self.title_edit.move(110, 10)
        self.title_edit.setText(self.title_text)
        self.title_edit.setParent(self)
        self.title_edit.setStyleSheet('background-color: white')
        self.title_edit.setVisible(True)

    def setup_type(self):
        self.type.resize(68, 21)
        self.type.move(10, 50)
        self.type.setText("TYPE:")
        self.type.setParent(self)
        self.type.setStyleSheet('background-color: white')
        self.type.setVisible(True)

        self.type_edit.resize(260, 21)
        self.type_edit.move(110, 50)
        self.type_edit.setText(self.type_text)
        self.type_edit.setParent(self)
        self.type_edit.setStyleSheet('background-color: white')
        self.type_edit.setVisible(True)

    def setup_assigned_to(self):
        self.assigned_to.resize(68, 21)
        self.assigned_to.move(10, 80)
        self.assigned_to.setText("ASSIGN:")
        self.assigned_to.setParent(self)
        self.assigned_to.setStyleSheet('background-color: white')
        self.assigned_to.setVisible(True)

        self.assigned_to_edit.resize(260, 21)
        self.assigned_to_edit.move(110, 80)
        self.assigned_to_edit.setText(self.assigned_to_text)
        self.assigned_to_edit.setParent(self)
        self.assigned_to_edit.setStyleSheet('background-color: white')
        self.assigned_to_edit.setVisible(True)

