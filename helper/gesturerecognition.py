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
        self.flash_bug = [(0.0, 48.75489573055079),
         (3.0427655814856562, 51.042603617404765),
         (5.988169750135261, 53.08806202510603),
         (9.101887364619092, 54.95431253225092),
         (12.072288169158185, 57.590906882514226),
         (15.016352135090257, 60.178297151096075),
         (18.14632233331658, 61.719314589463345),
         (21.21941420358029, 63.5130363964232),
         (24.3328910262144, 65.32710002296905),
         (27.438123852364082, 67.33165981897517),
         (30.20753092138773, 70.59536929192589),
         (33.21375197701975, 73.06730501807615),
         (36.263282637413255, 75.33304851624129),
         (39.04718497793381, 78.53511227371335),
         (42.07973474170925, 80.86801825375039),
         (45.22675561966715, 82.11178917327905),
         (48.27158275065384, 83.75312682976488),
         (51.30414424703057, 85.40506277836387),
         (54.353747634673056, 87.37549157752186),
         (57.03117550398263, 90.4948674274288),
         (59.58873783824337, 94.27269263174244),
         (62.14636829755126, 97.13954969617896),
         (65.01632800772211, 99.42896922384351),
         (67.28299202006208, 100.0),
         (65.58157828367243, 94.75862517000976),
         (64.03754180072622, 89.35998080007356),
         (62.336128064336556, 84.11860597008331),
         (60.6347143279469, 78.87723114009303),
         (58.93330059155725, 73.6358563101028),
         (57.231886855167595, 68.3944814801125),
         (55.53047311877794, 63.15310665012227),
         (53.35792376878815, 58.562117908367014),
         (51.41184865083163, 53.67570228771413),
         (49.710434914441976, 48.43432745772386),
         (47.87801001939206, 43.43144555421154),
         (47.52191625908644, 37.572050793294906),
         (46.25181641667823, 32.00093508640835),
         (44.550402680288585, 26.759560256418066),
         (43.17863916925201, 21.249534093986046),
         (41.668197313842455, 15.954381327195856),
         (39.9667835774528, 10.713006497205617),
         (38.26536984106316, 5.4716316672153775),
         (37.11449849853357, 0.0),
         (38.519947107521446, 0.013567922995283713),
         (41.53806151735612, 2.3328486484530684),
         (44.57882950841026, 4.673753417723064),
         (47.77136830805187, 5.961599779740828),
         (50.94069296018402, 7.6218247191941),
         (54.012183542122074, 9.774356906454344),
         (57.14077441464959, 11.675418497488911),
         (59.66818607074372, 15.526954505207708),
         (62.634445910416254, 18.121264170308123),
         (65.63052025243775, 20.660709547489596),
         (68.5684775114223, 23.41572760725299),
         (71.57828862000983, 25.85393608601645),
         (74.73751407129659, 27.249647946788027),
         (77.80526370869244, 28.08997160100213),
         (80.99157780173137, 29.503716687969234),
         (84.14717603121962, 31.071070989906588),
         (87.163743713612, 32.970888327248915),
         (90.34055649012603, 33.56858512282614),
         (93.56139746492171, 33.92803306545487),
         (96.75717020772763, 35.022736763744845),
         (100.0, 35.27354253306493)]
        self.check_task = [(0.0, 59.42229435059191),
         (0.8472758433868934, 62.056127898870436),
         (1.4952796167056916, 64.7996652555484),
         (2.300506528563196, 67.54519685632772),
         (3.6708028509117088, 70.03579282067311),
         (5.384775090470716, 72.37385487035307),
         (6.9530887955406415, 74.79292804690816),
         (8.151683594119417, 77.35264345945617),
         (9.527476120059417, 79.84502703817468),
         (11.48896321681763, 81.8839697989688),
         (13.337004901475805, 84.07683965177749),
         (14.604586757829452, 86.06445583412926),
         (16.79323996624388, 88.00339031258567),
         (19.245906825633575, 89.61621109602031),
         (21.761369480836766, 91.15500860143726),
         (24.169204565524577, 92.84851360825859),
         (26.096530941750988, 94.91501135655446),
         (27.51685550361775, 97.36063625514777),
         (29.129290801002874, 99.76199707358766),
         (30.58468102442883, 100.0),
         (32.5503353828045, 97.96384325235185),
         (33.98878466610797, 95.54954831010943),
         (34.13290937536605, 92.90168492921737),
         (36.01769364156453, 90.68676862513877),
         (37.78542350379946, 88.38547741725266),
         (39.60239839420846, 86.11915160278348),
         (41.46429328959875, 83.88672039903437),
         (43.281659769982525, 81.62712506394612),
         (44.966501538901575, 79.27602662005337),
         (46.81247121397935, 77.03108388110162),
         (48.65844088905716, 74.78614114214984),
         (50.79176426683313, 72.78684030124059),
         (52.93353964955405, 70.79476458573409),
         (55.07531503227495, 68.80268887022757),
         (57.04146078658442, 66.66500214233812),
         (58.81506483578212, 64.36768293750931),
         (60.72831410277067, 62.186140789893905),
         (62.832927740667344, 60.158493996643784),
         (64.92170929571196, 58.116774473659135),
         (66.81955641776786, 55.91147119938953),
         (68.43061963944216, 53.5163764399317),
         (69.93579217854247, 51.05120400217125),
         (71.71286246667937, 48.75852908634734),
         (73.6725339038494, 46.60289720351284),
         (75.60882040242107, 44.42941009626416),
         (77.38874516378516, 42.136535294414855),
         (79.16866992514926, 39.84366049256554),
         (79.2647208408252, 37.03529336088639),
         (80.25834458855628, 34.359333614559766),
         (81.66136654876857, 32.04366400394745),
         (81.66492158089352, 29.191505709437553),
         (82.98043486207521, 26.740926657180022),
         (85.12054125359235, 24.752311869401783),
         (86.69488149344977, 22.48099256995558),
         (88.66707700394373, 20.342584056286203),
         (90.37849385152467, 18.15553831377398),
         (92.48732922615108, 16.167904237576895),
         (94.64234535360106, 14.240357529584672),
         (97.17454495721141, 12.720189568631998),
         (96.17972515245445, 10.499647669235308),
         (97.10255144775499, 8.008219639139444),
         (98.29861707344496, 5.410942341257209),
         (98.9129075660835, 2.6258199566742673),
         (100.0, 0.0)]
        self.circle_epic = [(6.673651633466164, 47.81272114754497),
         (6.952546401370067, 53.281112037374115),
         (7.213813249061207, 58.750058598459624),
         (7.607704725805585, 64.21482453622946),
         (8.001596202549973, 69.67959047399928),
         (8.39548767929435, 75.14435641176912),
         (9.456438649374821, 80.28128929842673),
         (12.157368142277408, 84.83763518287113),
         (16.35537838047886, 87.72582935346327),
         (19.86163994413284, 91.74471249289415),
         (24.08461731624079, 94.36377548105294),
         (28.789616472575553, 96.54803954074374),
         (33.77581931398295, 98.17203865348849),
         (38.85862481521275, 99.3670011655608),
         (44.004875847315155, 100.0),
         (49.23052001477501, 99.84639041047703),
         (54.444774267959424, 99.43357495868426),
         (59.58089744137674, 98.50672997214727),
         (64.63749727750209, 97.57312704059254),
         (68.5781680423076, 94.00339651936287),
         (72.62185717430623, 90.56900689030178),
         (76.91117920506046, 87.72427485147851),
         (80.06600059081873, 83.4721888721093),
         (83.69944857657268, 79.53362265644155),
         (87.71306281932637, 76.08787728758901),
         (90.44879466145818, 71.48457373698872),
         (94.00053293501897, 67.53303134765493),
         (95.93457960739374, 63.17888785790138),
         (98.15060983634851, 58.30139613855212),
         (99.80876576754055, 53.267043629990916),
         (100.0, 47.94012057412413),
         (99.60610852325563, 42.47535463635429),
         (99.21221704651126, 37.010588698584456),
         (98.25154537747225, 31.642594308159424),
         (98.33456271295509, 26.328490870982392),
         (97.13020391150482, 21.059632753751636),
         (93.9965126126406, 17.084111124379877),
         (89.99911001829116, 13.56313229015968),
         (86.14789659791586, 9.859455287287483),
         (83.67960175629317, 5.033384736247499),
         (80.09678375935309, 1.246760410288738),
         (75.07257053640565, 0.0),
         (69.88976308511512, 0.02818285264512575),
         (64.67724448083807, 0.10209446319064797),
         (59.46014042631384, 0.45572207777080637),
         (54.24588617312942, 0.8685375295635458),
         (49.031631919945, 1.2813529813562925),
         (43.817377666760585, 1.6941684331490319),
         (38.603123413576164, 2.1069838849417786),
         (33.38886916039176, 2.519799336734518),
         (28.26074019968456, 2.4723751559281664),
         (23.465792153711316, 4.3030314033104755),
         (19.134853539087914, 7.102800112993633),
         (15.138303610655521, 10.340514824886249),
         (11.527201531309244, 14.134689012161331),
         (7.4881237772862965, 17.560679948013963),
         (4.171597668532337, 21.718963310928874),
         (1.87011150889575, 26.451009622851053),
         (0.9350557544478786, 31.843015193356187),
         (0.0, 37.23502076386132),
         (0.34852574615832976, 42.69730291059628),
         (0.4943166652113137, 48.163225830964414),
         (1.612012217011186, 53.34014153864418),
         (3.9270743631770864, 57.91281002056099)]

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
