#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# This file was edited by Gina Maria Wolf and Markus Guder
# Class is based on Jupiter Notebook
# https://elearning.uni-regensburg.de/mod/resource/view.php?id=851289
# Source - 1: https://stackoverflow.com/questions/30636014/how-to-order-a-list-of-points-by-distance-to-a-given-point

from pylab import *

class MapWiiMoteData:
    def __init__(self):
        super().__init__()

    def convert_vectors(self, ir_sensors, width, height):
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height

        # We sort the ir_data by the y position
        # depending on the that we can set which ir_data points are on which position
        # at least depending on the every x position of each point the element have to be rearranged
        # Source 1
        arranged_by_y = sorted(ir_sensors, key=lambda led: [led[1], led[0]])

        position_x_1, position_y_1 = arranged_by_y[0]
        positon_x_2, position_y_2 = arranged_by_y[1]

        if position_x_1 > positon_x_2:
            arranged_by_y[1] = (position_x_1, position_y_1)
            arranged_by_y[0] = (positon_x_2, position_y_2)

        position_x_1, position_y_1 = arranged_by_y[2]
        positon_x_2, position_y_2 = arranged_by_y[3]

        if position_x_1 < positon_x_2:
            arranged_by_y[3] = position_x_1, position_y_1
            arranged_by_y[2] = positon_x_2, position_y_2

        ir_sensors = arranged_by_y

        # Four IR markers indicating the corners of the display with which we interact
        sx1, sy1 = ir_sensors[0]
        sx2, sy2 = ir_sensors[1]
        sx3, sy3 = ir_sensors[2]
        sx4, sy4 = ir_sensors[3]
        # Scale the columns by the coefficients you just computed:
        unit_to_source = self.ir_data_transfrom(sx1, sx2, sx3, sx4, sy1, sy2, sy3, sy4)

        dx1, dy1 = 0, self.SCREEN_HEIGHT
        dx2, dy2 = self.SCREEN_WIDTH, self.SCREEN_HEIGHT
        dx3, dy3 = self.SCREEN_WIDTH, 0
        dx4, dy4 = 0, 0
        unit_to_dest = self.ir_data_transfrom(dx1, dx2, dx3, dx4, dy1, dy2, dy3, dy4)

        try:
            ir_data_source = inv(unit_to_source)
        except Exception:
            return 0, 0
        # To map a location  (x,y)(x,y) from the source image
        # to its corresponding location in the destination image, compute the product
        source_to_destination = unit_to_dest @ ir_data_source
        x, y, z = [float(w) for w in (source_to_destination @ matrix([[512], [384], [1]]))]

        return x / z, y / z

    def ir_data_transfrom(self, sx1, sx2, sx3, sx4, sy1, sy2, sy3, sy4):
        l, m, t = self.linear_equation(sx1, sx2, sx3, sx4, sy1, sy2, sy3, sy4)
        unit_to_source = matrix([[l * sx1, m * sx2, t * sx3],
                                 [l * sy1, m * sy2, t * sy3],
                                 [l, m, t]])
        return unit_to_source

    # Starting with the 4 positions in the source image,
    # (x1,y1)(x1,y1) through (x4,y4)(x4,y4), you solve the following system of linear equations
    def linear_equation(self, x1, x2, x3, x4, y1, y2, y3, y4):
        source_points_123 = matrix([[x1, x2, x3],
                                    [y1, y2, y3],
                                    [1, 1, 1]])
        source_point_4 = [[x4], [y4], [ 1 ]]
        try:
            returnValue = [float(x) for x in solve(source_points_123, source_point_4)]
            return returnValue
        except Exception as e:
            print(e)
            return 0, 0, 0
