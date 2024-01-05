import copy

import numpy as np
from filterpy.kalman import KalmanFilter


class Kalman2DPointTracker(object):
    """
    This class represents the internal state of individual tracked objects observed as bbox.
    """
    count = 0

    def __init__(self, point):
        """
    Initialises a tracker using initial bounding box.
    """
        # define constant velocity model
        self.kf = KalmanFilter(dim_x=4, dim_z=2)
        self.kf.F = np.array(
            [[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]])
        self.kf.H = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0]])

        self.kf.R[1:, 1:] *= 10.
        self.kf.P[2:, 2:] *= 1000.  # give high uncertainty to the unobservable initial velocities
        self.kf.P *= 10.
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[2:, 2:] *= 0.01

        self.kf.x[:2] = point
        self.time_since_update = 0
        self.id = Kalman2DPointTracker.count
        Kalman2DPointTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0

    def update(self, point):
        """
    Updates the state vector with observed bbox.
    """
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        self.kf.update(point)

    def predict(self):
        """
        Advances the state vector and returns the predicted bounding box estimate.
        """
        # if (self.kf.x[6] + self.kf.x[2]) <= 0:
        #     self.kf.x[6] *= 0.0
        self.kf.predict()
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        self.history.append(self.kf.x)
        return self.history[-1]

    def get_state(self):
        """
    Returns the current bounding box estimate.
    """
        return self.kf.x


class PointTracker:
    def __init__(self, point_name, max_predict=5):
        self.name = point_name
        self.max_predict = max_predict
        self.status = 'pause'
        self.kalman = None

    def start_kalman(self, point):
        if all(~np.isnan(np.squeeze(point))):
            self.kalman = Kalman2DPointTracker(point)
            self.status = 'live'
        else:
            self.status = 'pause'
            self.kalman = None

    def one_step(self, point):
        is_number = all(~np.isnan(np.squeeze(point)))
        if self.status == 'init' or self.status == 'live':
            self.kalman.predict()
            self.status = 'live'
            if is_number:
                self.kalman.update(point)
            else:
                if self.kalman.time_since_update > self.max_predict:
                    self.status = 'pause'
                    self.kalman = None
                    return np.array([[np.NaN], [np.NaN], [np.NaN], [np.NaN]])
        if self.status == 'pause':
            if is_number:
                self.start_kalman(point)
            else:
                return np.array([[np.NaN], [np.NaN], [np.NaN], [np.NaN]])

        return self.kalman.get_state()


if __name__ == '__main__':
    point_1 = np.array([[1, 2.]])
    point_2 = np.array([[2., 2]])
    point_3 = np.array([[3., 2.]])
    point_4 = np.array([[1., 4.]])
    point_5 = np.array([[2., 4.]])
    point_6 = np.array([[3., 4.]])
    frame_now = [point_1, point_2, point_3, point_4, point_5, point_6]

    frame_1 = copy.deepcopy(frame_now)
    dict_frames = [frame_1]
    for i in range(1, 20):
        for _point in frame_now:
            _point += np.array([[0.5, 0]])
        frame_2 = copy.deepcopy(frame_now)
        dict_frames.append(frame_2)

    for i, _frame in enumerate(dict_frames):
        if i in range(13, 20) or i in range(3, 10):
            _frame[5] = np.array([[np.NaN, np.NaN]])
        if i in range(7, 10):
            _frame[4] = np.array([[np.NaN, np.NaN]])
        if i == 5 or i == 11 or i == 17:
            _frame[3] = np.array([[np.NaN, np.NaN]])

    trackers = []
    # for i, _point in enumerate(frame_now):
    #     point_tracker = Kalman2DPointTracker()
    point_trackers = []
    for i in range(len(frame_now)):
        point_trackers.append(PointTracker(str(i)))

    for i, _frame in enumerate(dict_frames):
        print(i, _frame)
        for j, _point in enumerate(_frame):
            print(point_trackers[j].one_step(_point.T))

            # if i == 0:
            #     point_tracker = Kalman2DPointTracker(_point.T)
            #     trackers.append(point_tracker)
            # else:
            #     trackers[j].predict()
            #     # print(all(np.isnan(np.squeeze(_point))))
            #     if all(~np.isnan(np.squeeze(_point))):
            #         trackers[j].update(_point.T)
            #     print(trackers[j].get_state(), trackers[j].time_since_update)

    # print(point_1 + np.array([2., 0]))
