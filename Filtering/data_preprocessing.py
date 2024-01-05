import os
import sys
from all_frame_extract_pose_per_joint import poses_for_baby_ids
from all_frame_data_preprocessing import data_preprocessing_many_ids

try:
    from Utility.utils import folder_list_giving_parent_folder, update_prefix
    import Utility.const as const
except ModuleNotFoundError as err:
    print('In filtering_main: ', err, ', try adding parent dir to sys.path . . .')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path + '/..')
    from Utility.utils import folder_list_giving_parent_folder, update_prefix
    import Utility.const as const

if __name__ == "__main__":
    # big_pose_dir = r"X:\\PCI-PD\\Sensors Final Test\\"
    import argparse

    parser = argparse.ArgumentParser(description='This script preprocesses data.')
    parser.add_argument('--input-pose-folder', default=r"..\\data",
                        type=str,
                        help='The path to the big pose folder.')
    parser.add_argument('--input-face-folder', default=None,
                        type=str,
                        help='The path to the output of YOLO, if same as pose folder, no need to declare.')

    args = parser.parse_args()

    _big_folder_pose = args.input_pose_folder
    list_of_dirs = folder_list_giving_parent_folder(_big_folder_pose)

    for _dir in list_of_dirs:
        print('***************************************')
        print(_dir)
        print('***************************************')
        const.INPUT_FOLDER = _dir
        update_prefix()
        poses_for_baby_ids(body_relative=False)
        data_preprocessing_many_ids()
