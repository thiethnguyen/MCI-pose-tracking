import numpy as np
import json
import os
import argparse
from tqdm import tqdm
import Utility.const as reaching_const


def create_json(csv_folder, output_json_folder=None, frame_range=None):
    # Note: current code only applies for csv files without a header

    # json folder to contain the json file, the folder is of same level with csv_folder
    if output_json_folder is None:
        output_json_folder = os.path.join(os.path.dirname(csv_folder), 'json_files')
    # prefix of the filename is the name of the parent folder of csv_folder
    json_prefix = os.path.basename(os.path.dirname(csv_folder))

    frames = {}

    if frame_range is None:
        # No. of csv files in the csv folder // which is also the number of frames
        list_of_csv_files = [name_ for name_ in os.listdir(csv_folder)
                             if os.path.isfile(os.path.join(csv_folder, name_))]
        no_csv_files = len(list_of_csv_files)
        # list_of_files = sorted(filter(lambda x: os.path.isfile(os.path.join(csv_folder, x)),
        #                               os.listdir(csv_folder)))
        list_of_frames = sorted([int(name_[6:-4]) for name_ in list_of_csv_files])

        no_last_frame = list_of_frames[-1]
        frame_range = range(no_last_frame)
        # print(no_last_frame)
    else:
        frame_range = range(frame_range[0], frame_range[1])
    # print(frame_range)

    set_of_person_ids = set()
    # print('im here')
    for no_frames in tqdm(frame_range, desc="Processing csvs", unit="csv"):
        # print(no_frames)
        # read the current csv
        if not os.path.exists(os.path.join(csv_folder, 'frame_' + str(no_frames + 1) + '.csv')):
            data = np.zeros([1, 75])
            data[0, 0] = -1
        else:
            data = np.genfromtxt(os.path.join(csv_folder, 'frame_' + str(no_frames + 1) + '.csv'), delimiter=',')

        # print(data[0])
        # input()
        # for csv file that has only 1 row of data
        while data.ndim < 2:
            data = np.expand_dims(data, axis=0)
            # print(data[0,0])
        if np.isnan(data[0, 0]):
            data = data[1:, :]

        while data.ndim < 2:
            data = np.expand_dims(data, axis=0)

        data_id = data[:, 0]  # id is the first column
        data_keypoints = data[:, 1:]  # main data is from the second column
        no_persons = len(data_id)  # no. of ids

        # print(data_id)
        # print(data_id.tolist())
        new_ids = [int(x) for x in data_id.tolist()]
        # print(new_ids)
        set_of_person_ids.update(new_ids)  # update the set of all ids in whole video

        # a dict of person with key is data_id, and data is data_2
        dict_person = {}
        for _id, _data in zip(data_id, data_keypoints):
            dict_person[int(_id)] = _data.tolist()

        # new dict with the names of the keypoints included
        new_dict_persons = {}
        for k, v in dict_person.items():
            keypoints_list = []
            for i in range(0, len(v), 3):
                keypoints_list.append(v[i:i + 3])
            keypoints_dict_ = dict(enumerate(keypoints_list))
            keypoints_dict_final = dict(
                (value, keypoints_dict_[key]) for (key, value) in reaching_const.KEYPOINTS_DICT.items())
            new_dict_persons[k] = keypoints_dict_final

        subdict_of_frame = {"Count": no_persons, "Data": new_dict_persons}
        frames[no_frames + 1] = subdict_of_frame

    # print('output_json_folder', output_json_folder)
    if not os.path.exists(output_json_folder):
        os.makedirs(output_json_folder)
    with open(os.path.join(output_json_folder, json_prefix + '-' + reaching_const.JSON_FILE), 'w') as fp:
        json.dump(frames, fp)

    return set_of_person_ids


# for multiple videos (each video is in a child folder)
# parent folder is the Parent Dir (see more info in utils.py)
def create_json_batch(parent_folder, output_folder=None):
    for root, dirs, files in os.walk(parent_folder):
        for name in dirs:
            if name == 'csv_files':
                folder_name = os.path.join(root, name)
                print(folder_name)
                create_json(folder_name, output_folder)
                print('===================================================================')


if __name__ == "__main__":
    # print(os.path.dirname(os.path.realpath(__file__)))
    # Create the parser
    my_parser = argparse.ArgumentParser(description='Process some arguments')
    # Add the arguments
    my_parser.add_argument('--input',
                           type=str,
                           help='the file(s) or folder of input images and/or videos',
                           default=reaching_const.INPUT_FOLDER)
    my_parser.add_argument('--output',
                           type=str,
                           help='the file(s) or folder of input images and/or videos',
                           default=reaching_const.INPUT_FOLDER)
    args = my_parser.parse_args()

    folder_or_file = args.input
    out_folder = args.output

    # create a json for a parent folder for many videos
    create_json_batch(folder_or_file)
