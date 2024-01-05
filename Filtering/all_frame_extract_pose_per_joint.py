import json
import numpy as np
import os
import sys
from scipy.io import savemat

try:
    import Utility.const as const
    import Utility.utils as utils
except ModuleNotFoundError as err:
    print('In all_frame_extract_pose_per_joint: ', err, ', try adding parent dir to sys.path . . .')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path + '/..')
    import Utility.const as const
    import Utility.utils as utils


def poses_for_baby_ids(baby_ids=None, body_relative=False):
    # list all file paths in folder "json_files"
    if baby_ids is None:
        baby_ids = [0, 1]

    json_file = utils.file_path_giving_folder("json_files")
    # load the json file into a dictionary
    for _file in json_file:
        if const.JSON_COMBINED_FILE in _file:
            with open(_file, 'r') as f:
                json_combined_data = json.load(f)

    total_no_frames = len(json_combined_data)
    # print(no_csv_files)
    list_of_data_for_all_ids = {}
    for _baby_id in baby_ids:

        list_of_matrices = [np.zeros([total_no_frames, 3])] * len(const.LIST_OF_KEYPOINTS)
        for i, matrix in enumerate(list_of_matrices):
            list_of_matrices[i] = np.zeros([total_no_frames, 3])
        for i, matrix in enumerate(list_of_matrices):
            list_of_matrices[i][:] = np.nan

        list_of_data_for_all_ids[_baby_id] = list_of_matrices
    if body_relative:
        list_of_keypoints = const.LIST_OF_KEYPOINTS_RELATIVE
    else:
        list_of_keypoints = const.LIST_OF_KEYPOINTS
    for i, keypoint in enumerate(list_of_keypoints):
        # print(keypoint)
        for key, all_person in json_combined_data.items():
            for _person in all_person['Data']:
                for _baby_id in baby_ids:
                    if _baby_id == _person['baby_id']:
                        # print('here is in the baby list, is baby?', _baby_id, 'person id', _person['ID'])
                        # input()
                        try:
                            key_drift = int(key) - 0
                            list_of_data_for_all_ids[_baby_id][i][int(key_drift) - 1:int(key_drift)] = \
                                np.asarray(_person['Body'][keypoint])
                            break
                        except Exception:
                            # if keypoint == "Neck":
                            pass
                            # print(key, e)

    # save to matlab
    if 1:
        for _baby_id in baby_ids:
            keypoint_matrix_dict = dict(zip(list_of_keypoints, list_of_data_for_all_ids[_baby_id]))
            if not os.path.exists(os.path.join(const.INPUT_FOLDER, "matlab_files", str(_baby_id))):
                os.makedirs(os.path.join(const.INPUT_FOLDER, "matlab_files", str(_baby_id)))

            savemat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(_baby_id),
                                 const.PREFIX + const.MATLAB_RAW_DATA_FILE), keypoint_matrix_dict)


def run_for_many_videos(big_folder_pose=None):
    list_of_dirs = utils.folder_list_giving_parent_folder(big_folder_pose)
    for _dir in list_of_dirs:
        const.INPUT_FOLDER = _dir
        utils.update_prefix()
        poses_for_baby_ids(body_relative=False)


if __name__ == "__main__":
    big_pose_dir = r"X:\\PCI-PD\\Sensors Final Test\\"
    run_for_many_videos(big_folder_pose=big_pose_dir)
