#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# This file was edited by Gina Maria Wolf and Markus Guder

import json
import os


class FileOperations:

    def __init__(self, filename):
        self.filename = filename

    # Saves data to data_structure.json
    def save_setup(self, elements_to_store):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(self.filename, 'w') as outfile:
                json.dump(elements_to_store, outfile)
        except Exception as e:
            print("Exception: " + e)
            pass

    # Reads data from data_structure.json
    def parse_setup(self):
        try:
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(os.path.join(location, self.filename)) as config_file:
                return json.load(config_file)
        except Exception as e:
            print("Exception: " + e)
            pass
