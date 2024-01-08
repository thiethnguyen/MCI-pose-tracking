# -*- coding: utf-8 -*-
import cv2
import sys
import numpy as np
import os
import pygame

try:
    from Utility import utils
    from Utility import const
except ModuleNotFoundError as err:
    print('In openpose_handler: ', err, ', try adding parent dir to sys.path . . .')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path + '/..')
    from Utility import utils
    from Utility import const

dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    # Change these variables to point to the correct folder (Release/x64 etc.)
    sys.path.append(dir_path + '/../bin/python/openpose/Release')
    # print(sys.path)
    ex_path = os.environ['PATH'] + ';' + dir_path + '/../bin/python/openpose/Release;' + dir_path + '/../bin;'
    # print(ex_path)
    os.environ['PATH'] = ex_path
    import pyopenpose as op

except ImportError as err:
    print(
        'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python '
        'script in the right folder?')
    raise err

body_25_colors = [(255, 0, 85), (255, 0, 0), (255, 85, 0), (255, 170, 0), (255, 255, 0), (170, 255, 0), (85, 255, 0),
                  (0, 255, 0), (255, 0, 0), (0, 255, 85), (0, 255, 170), (0, 255, 255), (0, 170, 255), (0, 85, 255),
                  (0, 0, 255), (255, 0, 170), (170, 0, 255), (255, 0, 255), (85, 0, 255), (0, 0, 255), (0, 0, 255),
                  (0, 0, 255), (0, 255, 255), (0, 255, 255), (0, 255, 255)]

video_name = 'Camcorder 2 DEmo.mp4'
video_name_no_extension = video_name[:video_name.rindex('.')]
# output_video_extension = '.avi'  # .avi, .mp4
output_image_extension = '.jpg'


def keypoint_filter(keypoint_array):
    list_of_out = []
    for i in range(keypoint_array.shape[0]):
        if (any(keypoint_array[i, 1, :] != 0) and (
                (any(keypoint_array[i, 2, :] != 0) and any(
                    keypoint_array[i, 3, :] != 0) and any(
                    keypoint_array[i, 4, :] != 0)) or (
                any(keypoint_array[i, 5, :] != 0) and any(
                    keypoint_array[i, 6, :] != 0) and any(
                    keypoint_array[i, 7, :] != 0)))
            ) or (
                any(keypoint_array[i, 0, :] != 0) and any(
                    keypoint_array[i, 1, :] != 0) and any(
                    keypoint_array[i, 2, :] != 0) and any(
                    keypoint_array[i, 5, :] != 0) and any(
                    keypoint_array[i, 15, :] != 0) and any(
                    keypoint_array[i, 16, :] != 0) and (
                any(keypoint_array[i, 17, :] != 0) or any(
                    keypoint_array[i, 18, :] != 0))
        ):
            pass
        else:
            list_of_out.append(i)
    return np.delete(keypoint_array, list_of_out, axis=0)


def keypoint_filter_full_body(keypoint_array):
    list_of_out = []
    for i in range(keypoint_array.shape[0]):
        if keypoint_array[i].shape[0] >= 7:
            pass
        else:
            list_of_out.append(i)
    return np.delete(keypoint_array, list_of_out, axis=0)


class Input:
    def __init__(self, file_name=None):
        self.currentFrame = None
        if const.SKELETON:
            suffix = '-skeleton'
        elif const.KEYPOINT_ONLY:
            suffix = '-keypoints'
        else:
            suffix = '-output'
        # from openpose import *
        # print('-----START', const.INPUT_FOLDER, file_name)
        self.input_is_image = False
        self.input_is_video = False
        if utils.is_media_file(file_name) == 'video':
            self.input_is_video = True
        elif utils.is_media_file(file_name) == 'image':
            self.input_is_image = True
        else:
            print(utils.is_media_file(file_name))
        self.video_input = os.path.join(const.INPUT_FOLDER, file_name)
        prefix = file_name[:file_name.rindex('.')]
        # print(prefix)
        folder_csv = os.path.join(const.OUTPUT_FOLDER, prefix)
        # print(folder_csv)
        # input()

        self.folder_csv = os.path.join(folder_csv, 'csv_files')
        if not os.path.exists(self.folder_csv):
            os.makedirs(self.folder_csv)

        self.folder_output = os.path.join(folder_csv, 'output_videos')
        if not os.path.exists(self.folder_output):
            os.makedirs(self.folder_output)

        if not os.path.exists(os.path.join(folder_csv, 'output_videos_skeleton')):
            os.makedirs(os.path.join(folder_csv, 'output_videos_skeleton'))

        self.video_info = os.path.join(folder_csv, 'video_info')
        if not os.path.exists(self.video_info):
            os.makedirs(self.video_info)
        if self.input_is_image:
            self.video_output = os.path.join(folder_csv, 'output_videos', prefix + suffix + output_image_extension)
        else:
            if const.SKELETON:
                self.video_output = os.path.join(folder_csv, 'output_videos_skeleton',
                                                 prefix + suffix + const.OUTPUT_TYPE)
            else:
                self.video_output = os.path.join(folder_csv, 'output_videos',
                                                 prefix + suffix + const.OUTPUT_TYPE)
        params = dict()
        params["model_folder"] = const.OPENPOSE_MODEL_FOLDER
        params["net_resolution"] = "-1x432"
        # params["hand"] = True
        if const.SKELETON or const.KEYPOINT_ONLY:
            params["disable_blending"] = True
        if const.KEYPOINT_ONLY:
            params["alpha_pose"] = 0

        self.openpose = op.WrapperPython()
        self.openpose.configure(params)
        self.openpose.start()

        frame_rate = None
        dimensions = None
        if self.input_is_video:
            self.capture = cv2.VideoCapture(self.video_input)
            # print(self.video_file)
            self.frame_width = int(self.capture.get(3))
            self.frame_height = int(self.capture.get(4))
            frame_rate = (self.capture.get(5))
            self.total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

            if self.capture.isOpened():  # Checks the stream
                self.frameSize = (int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                                  int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
            const.SCREEN_HEIGHT = self.frameSize[0]
            const.SCREEN_WIDTH = self.frameSize[1]
        else:
            # read image
            self.capture = cv2.imread(self.video_input, cv2.IMREAD_UNCHANGED)

            # get dimensions of image
            dimensions = self.capture.shape

            # height, width, number of channels in image
            self.frame_height = self.capture.shape[0]
            self.frame_width = self.capture.shape[1]
            self.total_frames = 1
            const.SCREEN_HEIGHT = self.frame_height
            const.SCREEN_WIDTH = self.frame_width

        # to reduce the output resolution
        # if self.frame_height > 720:
        #     self.size = (int(self.frame_width * 720 / self.frame_height), 720)
        # else:
        #     self.size = (self.frame_width, self.frame_height)

        self.size = (self.frame_width, self.frame_height)

        if self.input_is_video:
            lines = ['Width: ' + str(self.frame_width), 'Height: ' + str(self.frame_height), 'FPS: ' + str(frame_rate),
                     'Size of output: ' + str(self.size), 'Total no. of frames: ' + str(self.total_frames)]
        else:
            lines = ['Width: ' + str(self.frame_width), 'Height: ' + str(self.frame_height),
                     'dimensions: ' + str(dimensions), 'Size of output: ' + str(self.size),
                     'Total no. of frames: ' + str(self.total_frames)]
        with open(os.path.join(self.video_info, 'readme.txt'), 'w') as f:
            for line in lines:
                f.write(line)
                f.write('\n')

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4',
                                        'v') if const.OUTPUT_TYPE == '.mp4' else cv2.VideoWriter_fourcc(
            *'MJPG')
        if self.input_is_video:
            self.result_video = cv2.VideoWriter(self.video_output,
                                                fourcc,
                                                frame_rate, self.size)

    def get_current_frame_as_image(self):
        frame = self.currentFrame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pgimg = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
        return pgimg

    def run(self, no_frames):
        if self.input_is_video:
            result, self.currentFrame = self.capture.read()
        else:
            self.currentFrame = self.capture
            if no_frames == 0:
                result = 1
            else:
                result = 0

        if not result:
            print("Can't receive frame (stream end?). Exiting ...")
            print("==========================================================================")
            lines = ['Real no. of frames: ' + str(no_frames)]
            with open(os.path.join(self.video_info, 'readme.txt'), 'a') as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')
            return 0
        datum = op.Datum()
        datum.cvInputData = self.currentFrame
        self.openpose.emplaceAndPop(op.VectorDatum([datum]))

        keypoints, self.currentFrame = np.array(datum.poseKeypoints), datum.cvOutputData
        try:
            keypoints = keypoint_filter(keypoints)
            poses = keypoints[:, :, :2]
            # Get containing box for each seen body
            boxes = utils.poses2boxes(poses)
        except (ValueError, IndexError):
            poses = np.zeros([1, 25, 3])
            boxes = []
        except Exception as e:
            print('1 ', e)
            poses = np.zeros([1, 25, 3])
            boxes = []

        # print(boxes)
        boxes_dict = [{'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2} for [x1, y1, x2, y2] in boxes]
        # print(boxes_dict)
        colors = [0] * len(boxes_dict)
        track_id = np.linspace(1, len(boxes_dict), len(boxes_dict))

        if const.SKELETON or const.KEYPOINT_ONLY:

            data_id = np.genfromtxt(os.path.join(self.folder_csv, "frame_" + str(no_frames + 1) + ".csv"),
                                    delimiter=",")
            while data_id.ndim < 2:
                data_id = np.expand_dims(data_id, axis=0)
            # print('+++++++++++++++++++++++++++',data_id[:,0], data_id.shape)
            # input()
            try:
                data_id = data_id[:, 0]
                for i in range(len(boxes_dict)):
                    # print(i)
                    # print(boxes_dict[i],colors[i])
                    cv2.rectangle(self.currentFrame, (int(boxes_dict[i]['x1']), int(boxes_dict[i]['y1'])),
                                  (int(boxes_dict[i]['x2']), int(boxes_dict[i]['y2'])), colors[i], 2)
                    cv2.putText(self.currentFrame, "%s" % (int(data_id[i])),
                                (int(boxes_dict[i]['x1']), int(boxes_dict[i]['y1']) - 5), 0,
                                5e-3 * 200 * self.frame_height / 720,
                                (255, 255, 255), 2)
            except Exception as e:
                print('2', e)

        if not (const.SKELETON or const.KEYPOINT_ONLY):
            try:
                for i in range(len(boxes_dict)):
                    # print(i)
                    # print(boxes_dict[i],colors[i])
                    cv2.rectangle(self.currentFrame, (int(boxes_dict[i]['x1']), int(boxes_dict[i]['y1'])),
                                  (int(boxes_dict[i]['x2']), int(boxes_dict[i]['y2'])), colors[i], 2)
                    cv2.putText(self.currentFrame, "%s" % (int(track_id[i])),
                                (int(boxes_dict[i]['x1']), int(boxes_dict[i]['y1']) - 5), 0,
                                5e-3 * 200 * self.frame_height / 720,
                                (255, 0, 0), 2)
            except Exception as e:
                print('3', e)

        cv2.putText(self.currentFrame, "%s" % (no_frames + 1),
                    (int(5 * self.frame_height / 720), int(25 * self.frame_height / 720)), 0,
                    5e-3 * 200 * self.frame_height / 720, (255, 0, 0), 2)

        # # keypoints only
        if const.KEYPOINT_ONLY:
            try:
                for i, xy in enumerate(np.reshape(poses, [-1, 2])):
                    if int(xy[0]) > 0 or int(xy[1]) > 0:
                        # print(x,y)
                        # print(type(x))
                        cv2.circle(self.currentFrame, (int(xy[0]), int(xy[1])), radius=5,
                                   color=body_25_colors[i % 25], thickness=-1)
            except (ValueError, IndexError):
                pass
            except Exception as e:
                print('4 ', e)

        arr_track_id = np.array(track_id)
        # print('Track ids', arr_track_id, arr_track_id.shape)
        # print('Track ids of sort', track_id_sort)
        if arr_track_id.shape[0] == 0:
            arr_track_id = np.array([-1])
        # print('Track ids', arr_track_id, arr_track_id.shape)

        if not (const.SKELETON or const.KEYPOINT_ONLY):
            _header = '' if const.NO_HEADER else const.CSV_HEADER
            try:
                data_to_save = np.reshape(keypoints, [np.shape(keypoints)[0], -1])
                data_to_save = np.c_[arr_track_id, data_to_save]
                # print('cs point', data_to_save.shape)
                np.savetxt(os.path.join(self.folder_csv, "frame_" + str(no_frames + 1) + ".csv"),
                           data_to_save, fmt='%.6g', delimiter=",",
                           header=_header, comments='')
            except (ValueError, IndexError):
                data_to_save = np.zeros([1, 75])
                data_to_save = np.c_[arr_track_id, data_to_save]
                # print('cs point', data_to_save.shape)
                np.savetxt(os.path.join(self.folder_csv, "frame_" + str(no_frames + 1) + ".csv"),
                           data_to_save, fmt='%.6g', delimiter=",",
                           header=_header, comments='')
            except Exception as e:
                print('6 ', e)
                data_to_save = np.zeros([1, 75])
                data_to_save = np.c_[arr_track_id, data_to_save]
                # print('cs point', data_to_save.shape)
                np.savetxt(os.path.join(self.folder_csv, "frame_" + str(no_frames + 1) + ".csv"),
                           data_to_save, fmt='%.6g', delimiter=",",
                           header=_header, comments='')

        if self.input_is_video:
            resize_frame = cv2.resize(self.currentFrame, self.size)
            self.result_video.write(resize_frame)
        elif self.input_is_image:
            cv2.imwrite(self.video_output, self.currentFrame)
        # input()
        if cv2.waitKey(1) == ord('p'):
            input()
