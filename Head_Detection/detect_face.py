import cv2
# import mmcv
import subprocess
import os

import pandas as pd
from tqdm import tqdm
import numpy as np

from distutils.dir_util import copy_tree
import shutil
from pathlib import Path
import sys

try:
    from Utility.utils import is_media_file, get_frame_list
except ModuleNotFoundError as err:
    print('In detect_face: ', err, ', try adding parent dir to sys.path . . .')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path + '/..')
    from Utility.utils import is_media_file, get_frame_list


def get_all_files_recursively_by_ext(root_dir, ext):
    found = []
    for path in Path(root_dir).rglob('*.{}'.format(ext)):
        found.append(str(path))
    return sorted(found)


def get_all_directories_containing_images(parent_dir):
    # Specify the top-level directory (folder A in your example)
    top_directory = parent_dir

    # Initialize a set to store the paths of directories containing images
    directories_with_images = set()

    # Use os.walk() to traverse the directory tree
    for _root, _dirs, _files in os.walk(top_directory):
        for file in _files:
            # Check if the file has a valid image extension
            # if any(file.lower().endswith(ext) for ext in image_extensions):
            if is_media_file(file) in ['image']:
                # Add the directory containing the image to the set
                directories_with_images.add(_root)

    # Convert the set of directories to a list and sort it if needed
    directory_paths = sorted(list(directories_with_images))

    print('there are: ', len(directory_paths))
    # Print the list of directory paths
    for path in directory_paths:
        print(path)
    return directory_paths


def ensure_dir(file_path):
    directory = file_path
    if file_path[-3] == "." or file_path[-4] == ".":
        directory = os.path.dirname(file_path)
    Path(directory).mkdir(parents=True, exist_ok=True)


def run_yolo_on_videos(input_path, output_path, exp_name, yolo_py_path, yolo_weight_path):
    ensure_dir(output_path)

    yolo_label_directory = os.path.join("runs", "detect")

    yolo_command = 'python "{py}" --weights "{yolo_weight}" --conf 0.25 --img-size 640 --source "{input}" --save-txt ' \
                   '--save-conf --name "{yolo_exp_name}" >> yolo_detect_log.txt 2>&1'.format(
                    py=yolo_py_path, yolo_weight=yolo_weight_path, input=input_path, yolo_exp_name=exp_name)
    print('yolo command:')
    print(yolo_command)
    # input()

    return_code = subprocess.call(yolo_command, shell=True)

    # Check the return code
    if return_code == 0:
        print("Subprocess executed without error.")
    else:
        print(f"Subprocess failed with return code: {return_code}")
        sys.exit(1)

    copy_tree(yolo_label_directory, output_path)
    shutil.rmtree(yolo_label_directory)


def gather_results(txt_directory, output_path, length):
    label_txts = get_all_files_recursively_by_ext(txt_directory, "txt")
    label_txts = sorted(label_txts, key=lambda x: int(x.split(os.sep)[-1].split("_")[-1][:-4]))

    if args.img_dir_input:
        labeled_frame = sorted([int(txt.split(os.sep)[-1].split("_")[-1][:-4]) for txt in label_txts])
    else:
        labeled_frame = sorted([int(txt.split(os.sep)[-1].split("_")[-1][:-4]) - 1 for txt in label_txts])
    # print('gather_results', labeled_frame)

    last_labeled_frame = labeled_frame[-1] if len(labeled_frame) > 0 else 0
    if length < last_labeled_frame + 1:
        length = last_labeled_frame + 1
    center_cords = np.ones((length, 4)) * -1
    print('gathering results: ')
    for label_txt in tqdm(label_txts, total=len(label_txts)):
        label_df = pd.read_csv(label_txt, header=None, sep=" ")
        idx = int(label_txt.split(os.sep)[-1].split("_")[-1].split(".txt")[0]) if args.img_dir_input else \
            int(label_txt.split(os.sep)[-1].split("_")[-1].split(".txt")[0]) - 1
        # print('idx', idx)
        bboxes_mom = label_df.loc[label_df[0] == 0]
        bboxes_baby = label_df.loc[label_df[0] == 1]

        cx_mom, cy_mom, cx_baby, cy_baby = -1, -1, -1, -1

        if len(bboxes_mom):
            _, x_float_mom, y_float_mom, _, _, _ = bboxes_mom.sort_values(5, ascending=False).iloc[0]
            cx_mom, cy_mom = x_float_mom, y_float_mom
        if len(bboxes_baby):
            _, x_float_baby, y_float_baby, _, _, _ = bboxes_baby.sort_values(5, ascending=False).iloc[0]
            cx_baby, cy_baby = x_float_baby, y_float_baby

        center_cords[idx] = cx_mom, cy_mom, cx_baby, cy_baby

    data_df = pd.DataFrame(center_cords, columns=["cx_mom", "cy_mom", "cx_baby", "cy_baby"], index=None)
    data_df.to_csv(output_path, index=False)


def main(input_path, txt_output_directory, exp_name, yolo_py_path, yolo_weight_path):
    csv_output_path = os.path.join(txt_output_directory, exp_name, 'csv_face', exp_name + ".csv")
    ensure_dir(csv_output_path)

    # remove the 'txt_face_labels' folder if existed, to prevent problem in the gather_results function
    if os.path.isdir(os.path.join(txt_output_directory, exp_name, 'txt_face_labels')):
        shutil.rmtree(os.path.join(txt_output_directory, exp_name, 'txt_face_labels'))

    if os.path.isfile(csv_output_path):
        os.remove(csv_output_path)

    video = cv2.VideoCapture(input_path)
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    # print('hehehe', length)
    # input()
    if args.img_dir_input:
        frm_lst_path = os.path.join(txt_output_directory, exp_name, 'face_frm_lst', exp_name + ".txt")
        ensure_dir(frm_lst_path)
        frame_lst = get_frame_list(input_path)
        # Open the file for writing
        with open(frm_lst_path, 'w') as file:
            # Write each list element to the file
            for item in frame_lst:
                file.write(str(item) + '\n')

    run_yolo_on_videos(input_path=input_path, output_path=txt_output_directory, exp_name=exp_name,
                       yolo_py_path=yolo_py_path, yolo_weight_path=yolo_weight_path)
    txt_directory = os.path.join(txt_output_directory, exp_name, 'txt_face_labels')
    gather_results(txt_directory=txt_directory, output_path=csv_output_path, length=length)


if __name__ == "__main__":
    folder_path = os.path.normpath(r"X:\Sensors_Folder\Input_image_list\Sing_100")
    output_folder = os.path.normpath(r"X:\Sensors_Folder\Pose_estimation_output\face\Sing_100_sensors_24_8_8")

    import argparse

    parser = argparse.ArgumentParser(description='Hello, world.')
    parser.add_argument('--input-path', default=folder_path,
                        type=str,
                        help='The path to the input video.')
    parser.add_argument('--txt-output-directory', default=output_folder, type=str,
                        help='Where to save the yolo raw output?')
    parser.add_argument('--yolo-py-path', default=r"yolov7-main\\detect.py", type=str,
                        help='The path to detect.py from YoloV7 folder.')
    parser.add_argument('--yolo-weight-path', default=r"yolov7-main\\best_sensors_24_8_8.pt", type=str,
                        help='The path to the yolov7 weight you want to load.')
    parser.add_argument('--img-dir-input', action='store_false', help='display results')

    args = parser.parse_args()

    folder_or_file = args.input_path
    is_file = False
    is_folder = False

    print('Working directory: ', folder_or_file)

    log_file = "yolo_detect_log.txt"
    # Check if the file exists
    if os.path.exists(log_file):
        # Remove the file
        os.remove(log_file)
        print(f"Old '{log_file}' removed successfully.")

    if os.path.isfile(folder_or_file):
        is_file = True
    elif os.path.isdir(folder_or_file):
        is_folder = True
    else:
        print('The file or folder does not exist')
        sys.exit(1)

    if not os.path.isfile(args.yolo_weight_path):
        print(r'The face detection model is missing! Please download and store it in Head_Detection/yolov7-main')
        sys.exit(1)

    print('. . . RUNNING . . . CHECK LOG FILE IN Head_Detection/yolo_detect_log.txt')

    if is_file:
        file_name = os.path.basename(folder_or_file)
        print('************************************************')
        print(file_name)
        print('************************************************')
        yolo_exp_name = file_name[:file_name.rindex('.')]
        if is_media_file(file_name) in ['video', 'image']:
            main(input_path=folder_or_file, txt_output_directory=args.txt_output_directory,
                 exp_name=yolo_exp_name, yolo_py_path=args.yolo_py_path,
                 yolo_weight_path=args.yolo_weight_path)
        else:
            print("Not a video or image!")
    elif is_folder:
        print('Looking for subfolders...........')

        if args.img_dir_input:
            print('treating as image folders')
            list_of_img_folders = get_all_directories_containing_images(folder_or_file)
            for _img_folder in list_of_img_folders:
                main(input_path=_img_folder, txt_output_directory=args.txt_output_directory,
                     exp_name=os.path.basename(_img_folder), yolo_py_path=args.yolo_py_path,
                     yolo_weight_path=args.yolo_weight_path)
        else:
            print('treating as individual files')
            for root, dirs, files in os.walk(folder_or_file):
                for _file in files:
                    print('************************************************')
                    print(_file)
                    print('************************************************')

                    yolo_exp_name = _file[:_file.rindex('.')]
                    if is_media_file(_file) in ['video', 'image']:
                        main(input_path=os.path.join(root, _file), txt_output_directory=args.txt_output_directory,
                             exp_name=yolo_exp_name, yolo_py_path=args.yolo_py_path,
                             yolo_weight_path=args.yolo_weight_path)
                    else:
                        print("Not a video or image!")
