
import numpy as np

from Utility.utils import Point2D, LineSegment2D, average_nan_same_name_points, Point2DRelative, point2d_to_relative
import time
from Utility.kalman_filter_class import PointTracker


class Body25:
    def __init__(self):
        self.Nose = Point2D(0, 0, name='Nose')
        self.Neck = Point2D(0, 0, name='Neck')
        self.RShoulder = Point2D(0, 0, name='RShoulder')
        self.RElbow = Point2D(0, 0, name='RElbow')
        self.RWrist = Point2D(0, 0, name='RWrist')
        self.LShoulder = Point2D(0, 0, name='LShoulder')
        self.LElbow = Point2D(0, 0, name='LElbow')
        self.LWrist = Point2D(0, 0, name='LWrist')
        self.MidHip = Point2D(0, 0, name='MidHip')
        self.RHip = Point2D(0, 0, name='RHip')
        self.RKnee = Point2D(0, 0, name='RKnee')
        self.RAnkle = Point2D(0, 0, name='RAnkle')
        self.LHip = Point2D(0, 0, name='LHip')
        self.LKnee = Point2D(0, 0, name='LKnee')
        self.LAnkle = Point2D(0, 0, name='LAnkle')
        self.REye = Point2D(0, 0, name='REye')
        self.LEye = Point2D(0, 0, name='LEye')
        self.REar = Point2D(0, 0, name='REar')
        self.LEar = Point2D(0, 0, name='LEar')
        self.LBigToe = Point2D(0, 0, name='LBigToe')
        self.LSmallToe = Point2D(0, 0, name='LSmallToe')
        self.LHeel = Point2D(0, 0, name='LHeel')
        self.RBigToe = Point2D(0, 0, name='RBigToe')
        self.RSmallToe = Point2D(0, 0, name='RSmallToe')
        self.RHeel = Point2D(0, 0, name='RHeel')

    def class_dict(self):
        return dict(Nose=self.Nose,
                    Neck=self.Neck,
                    RShoulder=self.RShoulder,
                    RElbow=self.RElbow,
                    RWrist=self.RWrist,
                    LShoulder=self.LShoulder,
                    LElbow=self.LElbow,
                    LWrist=self.LWrist,
                    MidHip=self.MidHip,
                    RHip=self.RHip,
                    RKnee=self.RKnee,
                    RAnkle=self.RAnkle,
                    LHip=self.LHip,
                    LKnee=self.LKnee,
                    LAnkle=self.LAnkle,
                    REye=self.REye,
                    LEye=self.LEye,
                    REar=self.REar,
                    LEar=self.LEar,
                    LBigToe=self.LBigToe,
                    LSmallToe=self.LSmallToe,
                    LHeel=self.LHeel,
                    RBigToe=self.RBigToe,
                    RSmallToe=self.RSmallToe,
                    RHeel=self.RHeel,
                    )

    def body_nan(self):
        for i, _joint in self.__dict__.items():
            if _joint.is_false_origin_approx():
                setattr(self, _joint.name, _joint.to_nan())

    def body_zero(self):
        for i, _joint in self.__dict__.items():
            if _joint.is_nan():
                setattr(self, _joint.name, _joint.to_zero())

    def body_torso(self):
        return [self.RShoulder, self.LShoulder, self.Neck, self.MidHip, self.RHip, self.LHip]

    def body_head(self):
        return [self.Nose, self.LEye, self.REye, self.LEar, self.REar]

    def body_arms(self):
        return [self.RElbow, self.LElbow, self.RWrist, self.LWrist]

    def no_body_head(self):
        # return all(x.is_origin() for x in self.body_head())
        return all(x.is_nan() for x in self.body_head())

    def number_of_body_head_points(self):
        # return all(x.is_origin() for x in self.body_head())
        return 5 - np.array([x.is_nan() for x in self.body_head()]).sum()

    def no_body_torso(self):
        return all(x.is_nan() for x in self.body_torso())

    def body_base_not_nan(self):
        not_nan_list = []
        if not self.no_body_torso():
            for _i, _point in enumerate(self.body_torso()):
                if not _point.is_nan():
                    not_nan_list.append(_point.name)
        return not_nan_list

    def body_center(self):
        return LineSegment2D(self.Neck, self.MidHip).mid_point(name='body center')

    def body_head_rectangular_diagonal(self):
        if self.no_body_head():
            return [np.NaN, 0]
        else:
            conf = (self.number_of_body_head_points() - 1) / 4.
            x_min = np.nanmin([joint.x for joint in self.body_head()])
            y_min = np.nanmin([joint.y for joint in self.body_head()])
            x_max = np.nanmax([joint.x for joint in self.body_head()])
            y_max = np.nanmax([joint.y for joint in self.body_head()])
            return [np.sqrt((x_max - x_min) ** 2 + (y_max - y_min) ** 2), conf]

    def body_spine_length(self):
        return LineSegment2D(self.Neck, self.MidHip).length()

    def body_upper_arm_length(self):
        r_ = LineSegment2D(self.RShoulder, self.RElbow).length()
        l_ = LineSegment2D(self.LShoulder, self.LElbow).length()
        r_arm = 0 if np.isnan(r_) else r_
        l_arm = 0 if np.isnan(l_) else l_
        if np.isnan(r_) and np.isnan(l_):
            return np.nan
        return r_arm if r_arm >= l_arm else l_arm

    def body_lower_arm_length(self):
        r_ = LineSegment2D(self.RWrist, self.RElbow).length()
        l_ = LineSegment2D(self.LWrist, self.LElbow).length()
        r_arm = 0 if np.isnan(r_) else r_
        l_arm = 0 if np.isnan(l_) else l_
        if np.isnan(r_) and np.isnan(l_):
            return np.nan
        return r_arm if r_arm >= l_arm else l_arm

    def body_arm_length(self):
        return self.body_upper_arm_length() + self.body_lower_arm_length()

    def spine_ratio(self):
        # print('spine', self.body_spine_length())
        return self.body_spine_length() / self.body_head_rectangular_diagonal()[0]

    def upper_arm_ratio(self):
        # print('upper arm', self.body_upper_arm_length())
        return self.body_upper_arm_length() / self.body_head_rectangular_diagonal()[0]

    def lower_arm_ratio(self):
        # print('lower arm', self.body_lower_arm_length())
        return self.body_lower_arm_length() / self.body_head_rectangular_diagonal()[0]

    def arm_ratio(self):
        return self.body_arm_length() / self.body_head_rectangular_diagonal()[0]

    def head_diagonal_ratios(self):
        # print('head', self.body_head_rectangular_diagonal())
        return np.array([self.spine_ratio(), self.upper_arm_ratio(), self.lower_arm_ratio()]), \
               self.body_head_rectangular_diagonal()[1]

    def body_base_track(self):
        return [self.REye, self.LEye, self.Neck, self.RShoulder, self.LShoulder, self.MidHip, self.RHip, self.LHip]

    def body_base_kalman(self):
        return [self.Neck, self.RShoulder, self.LShoulder, self.MidHip, self.RHip, self.LHip]

    def boby_to_relative(self):
        new_body = Body25Relative()
        new_body.Neck = self.Neck
        new_body.LHip = self.LHip
        new_body.RHip = self.RHip
        new_body.LShoulder = self.LShoulder
        new_body.RShoulder = self.RShoulder
        new_body.MidHip = self.MidHip

        new_body.Nose_Neck = point2d_to_relative(self.Nose, self.Neck)
        new_body.REye_Neck = point2d_to_relative(self.REye, self.Neck)
        new_body.LEye_Neck = point2d_to_relative(self.LEye, self.Neck)
        new_body.REar_Neck = point2d_to_relative(self.REar, self.Neck)
        new_body.LEar_Neck = point2d_to_relative(self.LEar, self.Neck)

        new_body.RElbow_RShoulder = point2d_to_relative(self.RElbow, self.RShoulder)
        new_body.RWrist_RShoulder = point2d_to_relative(self.RWrist, self.RShoulder)

        new_body.LElbow_LShoulder = point2d_to_relative(self.LElbow, self.LShoulder)
        new_body.LWrist_LShoulder = point2d_to_relative(self.LWrist, self.LShoulder)

        new_body.RKnee_RHip = point2d_to_relative(self.RKnee, self.RHip)
        new_body.RAnkle_RHip = point2d_to_relative(self.RAnkle, self.RHip)

        new_body.LKnee_LHip = point2d_to_relative(self.LKnee, self.LHip)
        new_body.LAnkle_LHip = point2d_to_relative(self.LAnkle, self.LHip)

        return new_body


class Body25Relative:
    def __init__(self):
        self.Neck = Point2D(0, 0, name='Neck')
        self.Nose_Neck = Point2DRelative(0, 0, self.Neck, name='Nose_Neck')
        self.RShoulder = Point2D(0, 0, name='RShoulder')
        self.RElbow_RShoulder = Point2DRelative(0, 0, self.RShoulder, name='RElbow_RShoulder')
        self.RWrist_RShoulder = Point2DRelative(0, 0, self.RShoulder, name='RWrist_RShoulder')
        self.LShoulder = Point2D(0, 0, name='LShoulder')
        self.LElbow_LShoulder = Point2DRelative(0, 0, self.LShoulder, name='LElbow_LShoulder')
        self.LWrist_LShoulder = Point2DRelative(0, 0, self.LShoulder, name='LWrist_LShoulder')
        self.MidHip = Point2D(0, 0, name='MidHip')
        self.RHip = Point2D(0, 0, name='RHip')
        self.RKnee_RHip = Point2DRelative(0, 0, self.RHip, name='RKnee_RHip')
        self.RAnkle_RHip = Point2DRelative(0, 0, self.RHip, name='RAnkle_RHip')
        self.LHip = Point2D(0, 0, name='LHip')
        self.LKnee_LHip = Point2DRelative(0, 0, self.LHip, name='LKnee_LHip')
        self.LAnkle_LHip = Point2DRelative(0, 0, self.LHip, name='LAnkle_LHip')
        self.REye_Neck = Point2DRelative(0, 0, self.Neck, name='REye_Neck')
        self.LEye_Neck = Point2DRelative(0, 0, self.Neck, name='LEye_Neck')
        self.REar_Neck = Point2DRelative(0, 0, self.Neck, name='REar_Neck')
        self.LEar_Neck = Point2DRelative(0, 0, self.Neck, name='LEar_Neck')

    def class_dict(self):
        return dict(Nose_Neck=self.Nose_Neck,
                    Neck=self.Neck,
                    RShoulder=self.RShoulder,
                    RElbow_RShoulder=self.RElbow_RShoulder,
                    RWrist_RShoulder=self.RWrist_RShoulder,
                    LShoulder=self.LShoulder,
                    LElbow_LShoulder=self.LElbow_LShoulder,
                    LWrist_LShoulder=self.LWrist_LShoulder,
                    MidHip=self.MidHip,
                    RHip=self.RHip,
                    RKnee_RHip=self.RKnee_RHip,
                    RAnkle_RHip=self.RAnkle_RHip,
                    LHip=self.LHip,
                    LKnee_LHip=self.LKnee_LHip,
                    LAnkle_LHip=self.LAnkle_LHip,
                    REye_Neck=self.REye_Neck,
                    LEye_Neck=self.LEye_Neck,
                    REar_Neck=self.REar_Neck,
                    LEar_Neck=self.LEar_Neck
                    )

    def body_nan(self):
        for i, _joint in self.__dict__.items():
            if _joint.is_false_origin_approx():
                setattr(self, _joint.name, _joint.to_nan())

    def body_zero(self):
        for i, _joint in self.__dict__.items():
            if _joint.is_nan():
                setattr(self, _joint.name, _joint.to_zero())

    def body_torso(self):
        return [self.RShoulder, self.LShoulder, self.Neck, self.MidHip, self.RHip, self.LHip]

    def body_head(self):
        return [self.Nose_Neck, self.LEye_Neck, self.REye_Neck, self.LEar_Neck, self.REar_Neck]

    def body_arms(self):
        return [self.RElbow_RShoulder, self.LElbow_LShoulder, self.RWrist_RShoulder, self.LWrist_LShoulder]

    def no_body_head(self):
        # return all(x.is_origin() for x in self.body_head())
        return all(x.is_nan() for x in self.body_head())

    def number_of_body_head_points(self):
        # return all(x.is_origin() for x in self.body_head())
        return 5 - np.array([x.is_nan() for x in self.body_head()]).sum()

    def no_body_torso(self):
        return all(x.is_nan() for x in self.body_torso())

    def body_base_not_nan(self):
        not_nan_list = []
        if not self.no_body_torso():
            for _i, _point in enumerate(self.body_torso()):
                if not _point.is_nan():
                    not_nan_list.append(_point.name)
        return not_nan_list

    def body_center(self):
        return LineSegment2D(self.Neck, self.MidHip).mid_point(name='body center')

    def body_head_rectangular_diagonal(self):
        if self.no_body_head():
            return [np.NaN, 0]
        else:
            conf = (self.number_of_body_head_points() - 1) / 4.
            x_min = np.nanmin([joint.x for joint in self.body_head()])
            y_min = np.nanmin([joint.y for joint in self.body_head()])
            x_max = np.nanmax([joint.x for joint in self.body_head()])
            y_max = np.nanmax([joint.y for joint in self.body_head()])
            return [np.sqrt((x_max - x_min) ** 2 + (y_max - y_min) ** 2), conf]

    def body_spine_length(self):
        return LineSegment2D(self.Neck, self.MidHip).length()

    def body_upper_arm_length(self):
        r_ = LineSegment2D(Point2DRelative(0, 0), self.RElbow_RShoulder).length()
        l_ = LineSegment2D(Point2DRelative(0, 0), self.LElbow_LShoulder).length()
        r_arm = 0 if np.isnan(r_) else r_
        l_arm = 0 if np.isnan(l_) else l_
        if np.isnan(r_) and np.isnan(l_):
            return np.nan
        return r_arm if r_arm >= l_arm else l_arm

    def body_lower_arm_length(self):
        r_ = LineSegment2D(self.RWrist_RShoulder, self.RElbow_RShoulder).length()
        l_ = LineSegment2D(self.LWrist_LShoulder, self.LElbow_LShoulder).length()
        r_arm = 0 if np.isnan(r_) else r_
        l_arm = 0 if np.isnan(l_) else l_
        if np.isnan(r_) and np.isnan(l_):
            return np.nan
        return r_arm if r_arm >= l_arm else l_arm

    def body_arm_length(self):
        return self.body_upper_arm_length() + self.body_lower_arm_length()

    def spine_ratio(self):
        # print('spine', self.body_spine_length())
        return self.body_spine_length() / self.body_head_rectangular_diagonal()[0]

    def upper_arm_ratio(self):
        # print('upper arm', self.body_upper_arm_length())
        return self.body_upper_arm_length() / self.body_head_rectangular_diagonal()[0]

    def lower_arm_ratio(self):
        # print('lower arm', self.body_lower_arm_length())
        return self.body_lower_arm_length() / self.body_head_rectangular_diagonal()[0]

    def arm_ratio(self):
        return self.body_arm_length() / self.body_head_rectangular_diagonal()[0]

    def head_diagonal_ratios(self):
        # print('head', self.body_head_rectangular_diagonal())
        return np.array([self.spine_ratio(), self.upper_arm_ratio(), self.lower_arm_ratio()]), \
               self.body_head_rectangular_diagonal()[1]

    def body_base_track(self):
        return [self.Neck, self.RShoulder, self.LShoulder, self.MidHip, self.RHip, self.LHip]

    def body_base_kalman(self):
        return [self.Neck, self.RShoulder, self.LShoulder, self.MidHip, self.RHip, self.LHip]

    def boby_to_relative(self):
        return self


class Person:
    def __init__(self, body_relative=False):
        self.pose_id = 0
        self.body_relative = body_relative
        if not self.body_relative:
            self.Body = Body25()
        else:
            self.Body = Body25Relative()
        self.head_ratio_score = 0
        self.is_baby = -1  # -1: neither baby nor mom, # 0: mom, # 1: baby
        self.head_ratio_conf = 0
        self.baby_MA_ID = -1
        self.closeness_score = 0
        self.total_score = 0
        self.joint_trackers = {}

    def class_dict(self):
        return dict(baby_id=self.baby_MA_ID, Body=self.Body, pose_id=self.pose_id)

    def human_body(self):
        return self.Body

    def display_human(self):
        for i, _joint in self.Body.__dict__.items():
            print(vars(_joint))

    def display_head(self):
        print([vars(joint) for joint in self.Body.body_head()])

    def input_skeleton(self, _id, skeleton_dict):
        self.pose_id = _id
        for _joint, _value in skeleton_dict.items():
            setattr(self.Body, _joint, Point2D(_value[0], _value[1], conf=_value[2], name=_joint))
        self.Body.body_nan()

    def point_trackers_init(self, max_predict=10):
        for _joint_name, _joint_point in self.Body.class_dict().items():
            self.joint_trackers[_joint_name] = PointTracker(_joint_name, max_predict=max_predict)

    def body25_to_body25relative(self):
        if not self.body_relative:
            self.Body = self.Body.boby_to_relative()

    def face_bounding_box_center(self):
        # find the minimum and maximum x and y coordinates using list comprehension
        x_coordinates = [point.x for point in self.Body.body_head()]
        y_coordinates = [point.y for point in self.Body.body_head()]
        x_min, y_min = np.nanmin(x_coordinates), np.nanmin(y_coordinates)
        x_max, y_max = np.nanmax(x_coordinates), np.nanmax(y_coordinates)

        # find the center of the bounding box
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2

        # the case when head is not detected, but body (neck) is detected
        if (np.isnan(center_x) or np.isnan(center_y)) and not self.Body.Neck.is_nan():
            return self.Body.Neck.x, self.Body.Neck.y

        return center_x, center_y


class KalmanPerson:
    def __init__(self):
        self.ID = 0
        self.Body = Body25()
        self.head_ratio_score = 0
        self.is_baby = -1  # -1: neither baby nor mom, # 0: mom, # 1: baby
        self.head_ratio_conf = 0
        self.baby_MA_ID = -1
        self.closeness_score = 0
        self.total_score = 0
        self.joint_trackers = {}

    def point_trackers_init(self, max_predict=10):
        for _joint_name, _joint_point in self.Body.class_dict().items():
            self.joint_trackers[_joint_name] = PointTracker(_joint_name, max_predict=max_predict)


def average_multi_person_ma(*list_of_person):
    if len(list_of_person) == 0:
        return None
    average_person = Person()
    for _joint_name, _joint_point in average_person.Body.class_dict().items():
        alist = [getattr(_person.Body, _joint_name) for _person in list_of_person]
        setattr(average_person.Body, _joint_name,
                average_nan_same_name_points(*alist))

    return average_person


def kalman_person_init(max_predict=10, body_relative=False):
    km_person = Person(body_relative=body_relative)
    km_person.Body.body_nan()
    km_person.point_trackers_init(max_predict=max_predict)
    return km_person


def kalman_person_update(current_km_person, new_observed_person):
    for _joint_name, _joint_point in current_km_person.Body.class_dict().items():
        # if _joint_name == 'Neck':
        #     print(_joint_name)
        new_joint_point = new_observed_person.Body.class_dict()[_joint_name]
        new_joint_point_ = np.array([[new_joint_point.x], [new_joint_point.y]])
        # print(new_joint_point)
        new_state_joint_point = current_km_person.joint_trackers[_joint_name].one_step(new_joint_point_)
        # if _joint_name == 'Neck':
        #     print(new_state_joint_point)
        #     input()
        setattr(current_km_person.Body, _joint_name,
                Point2D(new_state_joint_point[0, 0], new_state_joint_point[1, 0],
                        conf=new_joint_point.conf, name=_joint_name))
        # input()


def body_base_distance(*two_person):
    if len(two_person) < 2:
        return None
    distance = []
    base_couples = zip(two_person[0].Body.body_base_track(), two_person[1].Body.body_base_track())
    for _base_couple in base_couples:
        distance.append(LineSegment2D(_base_couple[0], _base_couple[1]).length())
    # print('distance are', distance)
    mean_distance = np.nanmean(np.nanmean(np.sort(distance)[:6]))
    return mean_distance


if __name__ == "__main__":
    t0 = time.time()
    person_1 = Person()
    ddd = {"Nose": [666.456, 430.645, 0.708944], "Neck": [0.0, 0.0, 0.0],
           "RShoulder": [700.722, 426.32, 0.744396], "RElbow": [610.726, 555.025, 0.66274],
           "RWrist": [650.713, 574.979, 0.0967774], "LShoulder": [0.0, 0.0, 0.0],
           "LElbow": [749.307, 556.406, 0.554543], "LWrist": [766.464, 586.417, 0.105041],
           "MidHip": [749.307, 556.406, 0.554543], "RHip": [0.0, 0.0, 0.0], "RKnee": [0.0, 0.0, 0.0],
           "RAnkle": [0.0, 0.0, 0.0], "LHip": [700.722, 426.32, 0.744396], "LKnee": [772.223, 566.419, 0.526498],
           "LAnkle": [670.754, 622.084, 0.48631], "REye": [656.454, 422.079, 0.774239],
           "LEye": [0.0, 0.0, 0.0], "REar": [0.0, 0.0, 0.0],
           "LEar": [0.0, 0.0, 0.0], "LBigToe": [656.434, 623.514, 0.187501],
           "LSmallToe": [656.428, 623.56, 0.22175], "LHeel": [659.314, 619.282, 0.253819], "RBigToe": [0.0, 0.0, 0.0],
           "RSmallToe": [0.0, 0.1, 0.0], "RHeel": [0.0, 0.0, 0.0]}
    person_1.input_skeleton(1, ddd)
    # person_1.Body.body_nan()
    print(vars(person_1.Body.MidHip))
    print('body center is')
    print(vars(person_1.Body.body_center()))
    print('body base that is not NaN')
    print(person_1.Body.body_base_not_nan())
    print(person_1.Body.body_head_rectangular_diagonal())
    print(person_1.Body.number_of_body_head_points())
    # person_1.display_human()
    print('head is')
    person_1.display_head()

    print('total time:', time.time() - t0)
