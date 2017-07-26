# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QFrame, QLineEdit, QPlainTextEdit, QLabel
from math import sqrt, pi, sin, cos
import math
from numpy import matrix

class GestureRecognition:
    def __init__(self):
        super().__init__()
        #rechts oben links unten
        self.flash_bug = [(0.0, 55.407118059034154), (2.8513177758460166, 57.55006363855746), (2.8513177758460166, 57.55006363855746), (4.653799832736216, 54.37173480499108), (4.903292566054002, 56.31173808518636), (6.166883134167535, 61.237923950031025), (8.015179322657954, 66.10869268172056), (10.920452275017414, 68.33300175372399), (14.584937271209501, 68.34641269742502), (18.19513093981809, 70.29969783401536), (21.1650456918168, 73.8422862843316), (23.829911218621792, 77.9199683296712), (25.07573198853919, 83.84233821102008), (26.30451432793161, 89.6212222977199), (28.38287087257072, 94.7174669595329), (30.777358704320935, 99.40034047043866), (34.12501638119416, 100.0), (36.08985648629798, 98.66851329553764), (35.541373777352135, 97.94053689599711), (32.52339227720635, 96.06513089593822), (31.239183983209838, 90.85566194862348), (30.35959650497113, 84.73677759282798), (29.058609420406242, 78.883369193172), (26.795804579167957, 74.11658369700592), (24.641722285468553, 69.33544770052937), (23.557734652132538, 63.667846786757245), (23.607051147470187, 57.31913798589872), (23.523096984459603, 51.110565502766434), (22.606801645142536, 45.3578221134546), (20.742439885120103, 39.96414821577136), (19.417165863308746, 34.101189871866076), (18.633748290777916, 28.293109440777496), (17.46738871226806, 22.428173036280587), (16.102013641863575, 16.52565616203935), (15.934190273335851, 10.421860617211793), (15.058759642814804, 4.599713423794378), (16.384193387846512, 0.0), (17.24024694902944, 4.110325870265334), (19.166316011741877, 9.245555558699328), (21.250693895299843, 14.012150119649224), (24.04674603154275, 16.424377200856192), (27.268114186951184, 19.79963732881895), (30.436679474288066, 21.945287623550175), (33.6520226937904, 25.390625975349085), (36.77520205965974, 28.5490088830549), (40.1316580430931, 31.399255615162335), (43.713260381537054, 33.559895933325734), (47.32214237376778, 35.82227716291808), (50.42442917579248, 39.37312493728518), (53.45630087097722, 43.18151429570684), (56.39357379094121, 47.322202542929105), (59.52590941743277, 49.79644476264014), (62.20584612373188, 54.283641473266336), (65.27386867902132, 57.57967961391591), (68.40392682770029, 61.171785779982606), (71.82595944081078, 64.09065507210664), (75.27468045664067, 66.35494389364055), (78.38851604148786, 69.73183360706811), (81.96275460359708, 71.7682339455022), (85.35023142713679, 74.55077552564491), (88.99749439854747, 76.40518682328961), (92.75141742218439, 77.31150807959783), (96.3318012170199, 78.30840075124154), (100.0, 77.45885891003618)]
        self.check_task = [(4.3133630262927944, 58.24480489982202), (2.592411642468792, 58.81949196868346), (2.535438018216619, 61.590936312479464), (1.8531676599804232, 64.50797325760192), (0.8791699386779631, 67.13609244366835), (0.8394550344826804, 69.94741012594056), (1.5179185440076566, 72.9708077216639), (1.1111389506085072, 75.53624264750248), (0.0, 78.35136331214854), (0.6195361839655578, 81.12102839232726), (2.693164540609786, 82.4619164722067), (4.893617416909991, 84.30819547669286), (5.03124054224968, 86.66363315075644), (5.237221048782812, 90.14110602187156), (4.332432450965352, 93.56292734889304), (3.1286134256952365, 95.92089514200482), (4.421502479936178, 97.4779948201284), (6.439237880374046, 98.22245292947436), (8.881404581467145, 98.98376408412751), (10.833079724371222, 100.0), (13.03787705909482, 97.7293804512878), (15.1529785933468, 95.40327344356962), (17.516248767224322, 93.66308981653341), (19.22598958165474, 91.69115894939239), (21.01077593962643, 88.8711321294048), (23.318300963093957, 86.55218764782855), (25.586106284545792, 84.74207527058294), (27.96006199210154, 82.67133118374372), (30.19264005416549, 80.24301811195303), (32.80430632622513, 78.88586956707734), (34.71705900819417, 76.32567564624075), (36.1972868279696, 73.25444370910756), (38.766572179012314, 71.62796404075004), (41.56915922142075, 70.50191106515031), (43.250419526709095, 67.71342968477292), (45.543908412902326, 65.36211849313587), (47.788346500465806, 62.95031291465603), (48.86132118051543, 59.65862111812533), (50.855488740440876, 56.99974652200483), (53.37582591988395, 55.013380376022454), (55.416514146569604, 52.41677596209409), (57.405846166989825, 49.737512749596746), (59.64544934671042, 47.31335396198539), (61.26296262749688, 44.620849010359), (62.83419123992076, 41.72522199877249), (64.98629806414485, 39.190720665094645), (66.8986777805119, 36.432359628839095), (69.11201283833803, 34.09387247234916), (71.30165781645383, 31.906169047695276), (72.5413988238548, 28.839260343919175), (74.69696814866393, 26.335786946309817), (76.79803303676614, 23.773324526126505), (78.49496796793684, 20.809266090922733), (80.77128575051421, 18.47913774451399), (83.08025131045619, 16.181336311732213), (84.71084407451129, 13.71751259458278), (85.67498282823885, 10.725651889570122), (87.94082331608675, 8.591961618762994), (90.03527325335459, 7.386751757660952), (92.23918780184643, 6.473864931673873), (94.30008980334972, 6.742327241262995), (96.20352904441525, 4.089578562151055), (98.6375778803277, 2.2557608633015738), (100.0, 0.0)]
        self.circle_epic = [(15.047204168323084, 52.972100935415995), (12.327929323141245, 51.37827633154504), (9.42833704723349, 55.12905790251537), (6.566963780822021, 59.8320984623599), (2.482698718792662, 63.2236163773436), (0.0, 68.37415072728143), (1.8634208979041407, 74.12422547895899), (4.534286619304918, 79.27907304429172), (7.833677570809715, 83.87414898178487), (10.924603725244268, 88.57229159087876), (14.56942734810025, 92.62567661027028), (18.817580995645447, 95.65821095080716), (23.335327046063416, 97.75453312449243), (27.949722960748513, 99.51125783348674), (32.81476838472085, 100.0), (37.64224639063515, 98.95093653473045), (42.490734123339244, 98.0846007188859), (47.34539956529194, 97.26669858136026), (52.107858770816286, 95.85727576497949), (56.83388405684395, 94.22299155331511), (61.54192960571358, 92.67211806624542), (65.66968573104633, 89.32039983105916), (69.80732620735185, 85.98634673917451), (73.83175344392451, 82.4377484454765), (77.6284711036524, 78.58306979461962), (81.19345604911784, 74.48606259860372), (84.67735451018838, 70.12415269309292), (87.57903448210273, 65.15332323958525), (90.79358952894029, 60.537657762239064), (93.30102707387016, 55.21180413084714), (95.63521000436646, 49.79491011425899), (97.55871693135654, 44.07704224757038), (98.72521384855555, 38.02681887151119), (99.62221294555471, 31.954265894878997), (100.0, 25.961584926598185), (98.60856530070004, 20.00550281183492), (95.82367679327083, 14.921889715178732), (91.5959250998405, 11.86721250920426), (87.12343623017304, 9.342644231285737), (82.6540776436607, 6.794543562232559), (78.15117805261657, 4.357517760212358), (73.64067314396509, 1.9400632316485205), (68.82574827265141, 0.8030101207561813), (63.97689918041863, 0.0), (59.07966146040034, 0.05282234092101483), (54.19149641038312, 0.4272027534352626), (49.36812739008312, 1.4262230758263235), (44.6834128652501, 3.237844608548668), (40.04829384343712, 5.211782593544274), (35.56794636977296, 7.7195625908485495), (32.41087932188915, 11.930740752175346), (31.50686317266475, 17.984904851479257), (30.13058686391416, 23.965873922001386), (28.84138583913282, 29.97799340978095), (27.286648730802092, 35.88497125444739), (26.021426531595047, 41.89660227888984), (25.762785725783317, 48.08817297816658), (26.80857449226044, 54.1607042799572), (27.71707291211487, 60.273013217973215), (28.977289887121184, 66.27998453800028), (29.63405537614265, 72.45366307657974), (30.678065842580242, 78.51297395221636), (33.88041637461369, 82.69855584499835), (36.89513224098167, 86.97995674401686), (36.89513224098167, 86.97995674401686)]

    def get_current_gesture(self, recorded_path):
        if(len(recorded_path) >= 64):
            self.current_path = None
            self.compare_array = None
            print("WICHTIG: " + str(len(recorded_path)))
            try:
                self.current_path = self.custom_filter(recorded_path)
            except Exception as e:
                return 3
            self.compare_array = []
            self.compare_array.append(self.find_gesture(self.current_path, self.flash_bug))
            self.compare_array.append(self.find_gesture(self.current_path, self.check_task))
            self.compare_array.append(self.find_gesture(self.current_path, self.circle_epic))
        else:
            return 3 # status for error

        return self.compare_array.index(min(float(s) for s in self.compare_array))

    def find_gesture(self, current_path, compare_path):
        overall_distance = 0
        counter_index = 0
        for point_current in current_path:
            overall_distance = overall_distance + self.distance(point_current, compare_path[counter_index])
            counter_index = counter_index + 1
        return overall_distance


    def distance(self, p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return sqrt(dx*dx+dy*dy)

    def total_length(self, point_list):
        p1 = point_list[0]
        length = 0.0
        for i in range(1, len(point_list)):
            length += self.distance(p1, point_list[i])
            p1 = point_list[i]
        return length

    def resample(self, point_list,step_count=63):
        newpoints = []
        length = self.total_length(point_list)
        stepsize = length/step_count
        curpos = 0
        newpoints.append(point_list[0])
        i = 1
        while i < len(point_list):
            p1 = point_list[i-1]
            d = self.distance(p1,point_list[i])
            if curpos+d >= stepsize:
                nx = p1[0] + ((stepsize-curpos)/d)*(point_list[i][0]-p1[0])
                ny = p1[1] + ((stepsize-curpos)/d)*(point_list[i][1]-p1[1])
                newpoints.append([nx,ny])
                point_list.insert(i,[nx,ny])
                curpos = 0
            else:
                curpos += d
            i += 1
        return newpoints

    def rotate(self, points, center, angle_degree):
        new_points = []
        angle_rad = angle_degree * (pi / 180)# degrees multmat
        rot_matrix = matrix([[cos(angle_rad), -sin(angle_rad), 0], # clockwise
                             [sin(angle_rad), cos(angle_rad), 0],
                             [0, 0, 1]])
        t1 = matrix([[1, 0, -center[0]],
                     [0, 1, -center[1]],
                     [0, 0, 1]])
        t2 = matrix([[1, 0,  center[0]],
                     [0, 1, center[1]],
                     [0, 0, 1]])
        transform = t2  @ rot_matrix @ t1
        for point in points:
            hom_point = matrix([[point[0]], [point[1]], [1]])
            rotated_point = transform @ hom_point
            new_points.append((float(rotated_point[0]),float(rotated_point[1])))
        return new_points

    def centroid(self, points):
        xs, ys = zip(*points)
        return (sum(xs)/len(xs), sum(ys)/len(ys))

    def angle_between(self, point1, point2): # point2 is our centroid
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return math.atan2(dy, dx) * 180/ math.pi # degree

    #assert(angle_between((-10, -10),(0,0)) == 45.0)

    def scale(self, points):
        size = 100
        xs, ys = zip(*points)
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        x_range = x_max - x_min
        y_range = y_max - y_min
        points_new = []
        for p in points:
            p_new = ((p[0] - x_min) * size / x_range,
                     (p[1] - y_min) * size / y_range)
            points_new.append(p_new)
        return points_new

    def normalize(self, points): # put everything together
        points_new = self.resample(points)
        angle = -self.angle_between(points_new[0], self.centroid(points_new))
        points_new = self.rotate(points_new, self.centroid(points_new), angle)
        points_new = self.scale(points_new)
        return points_new

    def normalize(self, points): # put everything together
        points_new = self.resample(points)
        angle = -self.angle_between(points_new[0], self.centroid(points_new))
        points_new = self.rotate(points_new, self.centroid(points_new), angle)
        points_new = self.scale(points_new)
        return points_new

    def custom_filter(self, points):
        return(self.normalize(points))
