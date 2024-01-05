# input:  - json from the pose estimation model (openpose-pose)
#         - csv_face from the face detection model (yolov7-face)
#         - (updated) a list of frames from the face detection folder (face)
# output: - a combined json file which have baby_MA_ID updated based on analysis of the face bounding box (from face)
#           and the head box (from pose)
#           (updated) if the list of frames is provided, the output json will only contain those specific frames

# update here
# 10/2023: add read_frm_list --> for convenience in case we want to save time for some specific frames
#          (note) this is only when per-frame method is used, shouldn't be used when tracking methods are used
#                 (such as kalman filter)
# ------------
# 29/10/2023: try:
#                 current_faces = [face_data[i][int(_frame) - 1, 0:2] for i in [0, 1]]
#             except IndexError:
# in some cases, the length of face_csv is less than the biggest frame number in the frame list
# (this happens when the late frames have no bounding boxes)


import copy
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.io import loadmat, savemat
from tqdm import tqdm

try:
    import Utility.const as const
    import Utility.utils as utils
    from Utility.human_properties import Person
    from Utility.utils import ComplexEncoder, assign_points
    from Utility.utils import (file_path_giving_folder, folder_list_giving_parent_folder, update_prefix, get_frame_list,
                               check_correspondence)
except ModuleNotFoundError as err:
    print('In integration_main: ', err, ', try adding parent dir to sys.path . . .')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path + '/..')
    import Utility.const as const
    import Utility.utils as utils
    from Utility.human_properties import Person
    from Utility.utils import ComplexEncoder, assign_points
    from Utility.utils import (file_path_giving_folder, folder_list_giving_parent_folder, update_prefix, get_frame_list,
                               check_correspondence)


# Read the csv file created from yolo face detection
def read_csv(filename=None, parent_dir=None):
    # Read the CSV file
    if filename is None:
        filenames = file_path_giving_folder("csv_face", parent_dir=parent_dir)
        if filenames is not None:
            filename = filenames[0]
    df = pd.read_csv(filename)
    # df = df.drop(0)
    # Display the data
    # print(df.head())

    # Convert the pandas DataFrame to a dictionary
    data_array = df.to_numpy()
    print(data_array.shape)
    data_array[data_array == -1] = np.nan
    data_mom = data_array[:, 0:2]
    data_baby = data_array[:, 2:4]
    data_mom = np.c_[data_mom, np.ones((data_mom.shape[0], 1)) * 0.5]
    data_baby = np.c_[data_baby, np.ones((data_baby.shape[0], 1)) * 0.5]
    # data_mom_dict = {'Neck': data_mom}
    # data_baby_dict = {'Neck': data_baby}
    data_all = {'0': data_mom, '1': data_baby}

    for _id, _data in data_all.items():
        # Save the data to a MATLAB .mat file
        if not os.path.exists(os.path.join(const.INPUT_FOLDER, "matlab_files", str(_id))):
            os.makedirs(os.path.join(const.INPUT_FOLDER, "matlab_files", str(_id)))

        savemat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(_id),
                             const.PREFIX + const.MATLAB_RAW_DATA_FILE), {'Face': _data})
    return df


def read_frm_list(filename=None, parent_dir=None):
    if filename is None:
        filenames = file_path_giving_folder("face_frm_lst", parent_dir=parent_dir)
        if filenames is not None:
            filename = filenames[0]

    if filename is not None:
        # Open the file for reading
        with open(filename, 'r') as file:
            # Read each line and append it to the list (removing trailing newline characters)
            my_list = [int(line.strip()) + 1 for line in file.readlines()]

    else:
        print('no face_frm_lst', parent_dir)
        # input()
        my_list_python = get_frame_list(parent_dir)
        my_list = [int(x) + 1 for x in my_list_python]

    # Print the list
    print(my_list)
    # input()
    return my_list


def compute_score_face(list_of_person_faces, face_data_yolo):
    mapping = assign_points(list_of_person_faces, face_data_yolo)
    closeness_to_baby_face_score = [-1] * len(list_of_person_faces)

    for _id, _value in mapping.items():
        # print(type(int(_id)), _id)
        # print(type(_value), _value)
        closeness_to_baby_face_score[int(_id)] = int(_value)  # convert from numpy.int64 to int
    return closeness_to_baby_face_score


def get_score_for_persons_based_on_face(list_of_frames, json_data, json_score_only, face_data):
    scores_frames = {}
    for _frame, _data in tqdm(json_data.items(), desc="Processing frames"):
        if int(_frame) in list_of_frames:
            # print('====================================================')
            # print('fr no:', _frame, end=', ')
            list_of_person = []
            list_of_person_faces = []
            for _person_id, _pose in _data['Data'].items():
                person_temp = Person()
                person_temp.input_skeleton(_person_id, _pose)
                list_of_person.append(person_temp)
                list_of_person_faces.append(person_temp.face_bounding_box_center())

            try:
                current_faces = [face_data[i][int(_frame) - 1, 0:2] for i in [0, 1]]
                # print(current_faces)

            except IndexError:
                print(f"face_data is too short with length {len(face_data[0])}, but frame no is {_frame}")
                current_faces = [np.array([np.nan, np.nan]), np.array([np.nan, np.nan])]

            face_closeness_scores \
                = compute_score_face(list_of_person_faces,
                                     current_faces)

            for i, _person in enumerate(list_of_person):
                # pass
                _person.baby_MA_ID = face_closeness_scores[i]
                # print(type(_person.baby_MA_ID))

            # print(scores[i])
            if json_score_only == 1:
                new_dict_persons = {}
                for k, _person in enumerate(list_of_person):
                    new_dict_persons[_person.pose_id] = [_person.closeness_score, _person.head_ratio_score,
                                                         _person.total_score, _person.baby_MA_ID]
                subdict_of_frame = {"Count": _data["Count"], "Data": new_dict_persons}
                scores_frames[_frame] = subdict_of_frame
            else:
                new_dict_persons = []
                for k, _person in enumerate(list_of_person):
                    __person = copy.deepcopy(_person)
                    __person.Body.body_zero()
                    new_dict_persons.append(json.loads(json.dumps(__person, cls=ComplexEncoder)))

                subdict_of_frame = {"Count": _data["Count"], "Data": new_dict_persons}
                scores_frames[_frame] = subdict_of_frame

    return scores_frames


def poses_for_frames(list_of_frames=None, output_json_folder=None, json_score_only=1, json_add_suf=''):
    # arguments:
    # list_of_frames: Eg. range(10, 20)
    # list all file paths in folder "json_files"

    json_file = utils.file_path_giving_folder("json_files")
    # load the json file into a dictionary
    for _file in json_file:
        if const.JSON_FILE in _file:
            print(_file)
            with open(_file, 'r') as f:
                json_data = json.load(f)

    no_csv_files = len(json_data)
    # print(no_csv_files)
    if list_of_frames is None:
        list_of_frames = range(0 + 1, no_csv_files + 1)
    # list_of_frames = [item + 1 for item in list_of_frames]
    print(list_of_frames)

    face_dict = read_matlab_yolo(data_type=const.MATLAB_RAW_DATA_FILE)
    face_data = []
    for _id in ['0', '1']:
        face_data.append(face_dict[_id])

    scores_frames = get_score_for_persons_based_on_face(list_of_frames, json_data, json_score_only, face_data)

    if json_score_only == 1:
        suf_name = const.JSON_SCORE_FILE
    elif json_score_only == 2:
        suf_name = const.JSON_SCORE_FILE_2
    elif json_score_only == 3:
        suf_name = const.JSON_SCORE_FILE_GROUND_TRUTH
    else:
        suf_name = const.JSON_COMBINED_FILE

    suf_name = suf_name[:-5] + json_add_suf + '.json'

    if output_json_folder is None:
        output_json_folder = os.path.join(const.INPUT_FOLDER, "json_files")
    # print('output_json_folder', output_json_folder)
    with open(os.path.join(output_json_folder, const.PREFIX + suf_name), 'w') as fp:
        # print(scores_frames)
        json.dump(scores_frames, fp)

    # print(data)


def read_matlab_yolo(data_type=None, save_face=False):
    if data_type is None:
        data_type = const.MATLAB_RAW_DATA_FILE
    frame_width, frame_height, frame_fps, total_no_frames = utils.read_video_info()
    print(frame_width, frame_height)
    face_data = {}
    for _id in ['0', '1']:
        # Load the face data from the face folder
        arr = loadmat(os.path.join(const.YOLO_INPUT_FOLDER, "matlab_files", str(_id),
                                   const.PREFIX + data_type))['Face']
        arr[:, 0] *= frame_width  # multiply the first column by 'a'
        arr[:, 1] *= frame_height  # multiply the second column by 'b
        face_data[_id] = arr
        if save_face:
            savemat(os.path.join(const.YOLO_INPUT_FOLDER, "matlab_files", str(_id),
                                 const.PREFIX + const.MATLAB_FACE_TO_OPENPOSE), {'Face': arr})
    # print(face_data)

    return face_data


def run_for_many_videos(big_folder_pose=None, big_folder_face=None, json_score_only=0, json_add_suf=''):
    if big_folder_face is None:
        list_of_dirs = folder_list_giving_parent_folder(big_folder_pose)
        for _dir in list_of_dirs:
            print('***************************************')
            print(_dir)
            print('***************************************')
            const.INPUT_FOLDER = _dir
            update_prefix()
            read_csv()
            poses_for_frames(json_score_only=json_score_only, json_add_suf=json_add_suf)
    else:
        list_of_pose_dirs = folder_list_giving_parent_folder(big_folder_pose)
        list_of_face_dirs = folder_list_giving_parent_folder(big_folder_face)
        if len(list_of_pose_dirs) != len(list_of_face_dirs):
            user_input = input("numbers of pose dirs and face dirs are not equal! continues?").strip().lower()
            if user_input == "yes":
                # Continue with the program
                print("Continuing with the program...")
                # Add your program logic here
            else:
                # Exit the program
                print("Exiting the program.")
                exit()
        for _pose_dir, _face_dir in zip(list_of_pose_dirs, list_of_face_dirs):
            print(_pose_dir, _face_dir)
            if not (check_correspondence(_pose_dir, _face_dir)):
                print('WRONG CORRESPONDENCE!!!!!!!!')
                exit(-1)

            const.INPUT_FOLDER = _pose_dir
            update_prefix()
            read_csv(parent_dir=_face_dir)
            frm_lst = read_frm_list(parent_dir=_face_dir)
            poses_for_frames(json_score_only=json_score_only, list_of_frames=frm_lst, json_add_suf=json_add_suf)
            # input()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='This script combines outputs of OpenPose and YOLOv7.')
    parser.add_argument('--input-pose-folder', default=r"..\\data",
                        type=str,
                        help='The path to the output of OpenPose.')
    parser.add_argument('--input-face-folder', default=None,
                        type=str,
                        help='The path to the output of YOLO, if same as pose folder, no need to declare.')
    parser.add_argument('--json-score-only', default=0, type=int,
                        help='The code for the json name.')
    parser.add_argument('--json-add-suf', default='', type=str,
                        help='The added suffix for json name.')

    args = parser.parse_args()

    _big_folder_pose = args.input_pose_folder
    _big_folder_face = args.input_face_folder
    _json_score_only = args.json_score_only
    _json_add_suf = args.json_add_suf
    # read_csv()
    # poses_for_frames(json_score_only=0)
    # run for face output from training YOLOv7

    run_for_many_videos(big_folder_pose=_big_folder_pose,
                        big_folder_face=_big_folder_face,
                        json_score_only=_json_score_only,
                        json_add_suf=_json_add_suf)

    # run for face output from GROUND TRUTH
    # run_for_many_videos(big_folder_pose=r'X:\Sensors_Folder\Pose_estimation_output\pose\Sing_2',
    #                     big_folder_face=r'X:\Sensors_Folder\Face_Ground_truth\Singapore_2(fr_no_in_name)',
    #                     json_score_only=3)
