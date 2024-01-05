import os
import sys
import numpy as np
from scipy.io import savemat, loadmat

try:
    import Utility.const as const
    from Utility.utils import read_video_info, calculate_moving_ave_array, continuous_nan_num_ranges, filter_sub_series
    from Utility.utils import short_nan_sub_series, interpolate_sub_series, folder_list_giving_parent_folder, \
        update_prefix
except ModuleNotFoundError as err:
    print('In all_frame_data_preprocessing: ', err, ', try adding parent dir to sys.path . . .')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path + '/..')
    import Utility.const as const
    from Utility.utils import read_video_info, calculate_moving_ave_array, continuous_nan_num_ranges, filter_sub_series
    from Utility.utils import short_nan_sub_series, interpolate_sub_series, folder_list_giving_parent_folder, \
        update_prefix


def remove_zero_data(person_id):
    keypoint_matrices_dict = loadmat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                                                  const.PREFIX + const.MATLAB_RAW_DATA_FILE))

    for key, data in keypoint_matrices_dict.items():
        # print(key)
        # print(np.shape(data))
        if key not in ['__header__', '__version__', '__globals__']:
            i = 0
            for row in data:
                if i < 0:
                    row[0] = np.nan
                    row[1] = np.nan
                elif row[2] == 0:
                    row[0] = np.nan
                    row[1] = np.nan

                keypoint_matrices_dict[key][i:i + 1, :] = row
                i += 1

    savemat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                         const.PREFIX + const.MATLAB_RAW_DATA_REMOVE_ZERO_DATA),
            keypoint_matrices_dict)


# removing sudden changes using moving average, by a threshold
def remove_sudden_changes_using_ma(person_id, abnormal_threshold, in_file=None, out_file=None, ma_in_file=None):
    if in_file is None:
        in_file = const.PREFIX + const.MATLAB_RAW_DATA_REMOVE_ZERO_DATA
    if out_file is None:
        out_file = const.PREFIX + const.MATLAB_REMOVE_SUDDEN_AFTER_MA
    if ma_in_file is None:
        ma_in_file = const.PREFIX + const.MATLAB_MOVING_AVERAGE_DATA

    # input data
    keypoint_matrices_dict = loadmat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                                                  in_file))

    # moving ave data
    keypoint_matrices_ma_dict = loadmat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                                                     ma_in_file))

    for key, data in keypoint_matrices_dict.items():
        # print(key)
        # print(np.shape(data))
        if key not in ['__header__', '__version__', '__globals__']:
            # print(key)
            i = 0
            for row in data:
                ma_row = keypoint_matrices_ma_dict[key][i]
                # print('row', row, ma_row)
                # print('herehere', np.abs(row[0] - ma_row[0]), abnormal_threshold)
                # input()
                if (row[2] == 0 or np.abs(row[0] - ma_row[0]) > abnormal_threshold
                        or np.abs(row[1] - ma_row[1]) > abnormal_threshold):
                    row[0] = np.nan
                    row[1] = np.nan

                keypoint_matrices_dict[key][i:i + 1, :] = row
                i += 1

    savemat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id), out_file),
            keypoint_matrices_dict)


def remove_short_num_ranges(person_id):
    keypoint_matrices_dict_nan = \
        loadmat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                             const.PREFIX + const.MATLAB_PREPROCESSED_DATA_FILE_EARLY))

    nan_dict, num_dict = continuous_nan_num_ranges(keypoint_matrices_dict_nan)

    # print('==============Removing short num ranges==================')
    for key, data in keypoint_matrices_dict_nan.items():
        # print(key)
        # print(np.shape(data))
        if key not in ['__header__', '__version__', '__globals__']:
            for num_slice in num_dict[key]:
                if num_slice['length'] <= 5:  # if num_slice['length'] <= N:
                    # remove the short number ranges of less than N numbers
                    # print(num_slice)
                    keypoint_matrices_dict_nan[key][num_slice['begin']:num_slice['begin'] + num_slice['length'], 0:2] \
                        = np.nan

    savemat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                         const.PREFIX + const.MATLAB_PREPROCESSED_DATA_REMOVE_SHORT_NUM),
            keypoint_matrices_dict_nan)


def data_filtering(person_id, window=5, in_file=None, out_file=None):
    if in_file is None:
        in_file = const.PREFIX + const.MATLAB_REMOVE_SUDDEN_AFTER_MA
    if out_file is None:
        out_file = const.PREFIX + const.MATLAB_PREPROCESSED_DATA_FILTERED

    keypoint_matrices_dict = loadmat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                                                  in_file))

    for key, data in keypoint_matrices_dict.items():
        # print(key)
        # print(np.shape(data))
        if key not in ['__header__', '__version__', '__globals__']:
            keypoint_matrices_dict[key] = np.c_[filter_sub_series(data[:, 0:2], window_length=window), data[:, 2:3]]

    savemat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                         out_file),
            keypoint_matrices_dict)


def data_interpolation(person_id, method='linear', maximum_nan_length=20, in_file=None, out_file=None):
    if in_file is None:
        in_file = const.PREFIX + const.MATLAB_PREPROCESSED_DATA_FILTERED
    if out_file is None:
        out_file = const.PREFIX + const.MATLAB_INTERPOLATED_DATA

    keypoint_matrices_dict = loadmat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                                                  in_file))

    for key, data in keypoint_matrices_dict.items():
        # print(key)
        # print(np.shape(data))
        if key not in ['__header__', '__version__', '__globals__']:
            list_of_short_nan_series = short_nan_sub_series(data, maximum_nan_length)
            for _ser in list_of_short_nan_series:
                _sub_series = data[_ser[0]:_ser[1], 0:2]
                try:
                    data[_ser[0]:_ser[1], 0:2] = interpolate_sub_series(_sub_series, method=method, order=3)
                except:
                    data[_ser[0]:_ser[1], 0:2] = interpolate_sub_series(_sub_series, method='linear')
            keypoint_matrices_dict[key] = data

    savemat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                         out_file),
            keypoint_matrices_dict)


def data_moving_average(person_id, window_size=20,
                        in_file=const.PREFIX + const.MATLAB_RAW_DATA_REMOVE_ZERO_DATA,
                        out_file=const.PREFIX + const.MATLAB_MOVING_AVERAGE_DATA):
    keypoint_matrices_dict = loadmat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                                                  in_file))

    for key, data in keypoint_matrices_dict.items():
        # print(key)
        # print(np.shape(data))
        if key not in ['__header__', '__version__', '__globals__']:
            keypoint_matrices_dict[key] = calculate_moving_ave_array(data, window_size)

    savemat(os.path.join(const.INPUT_FOLDER, "matlab_files", str(person_id),
                         out_file),
            keypoint_matrices_dict)


def data_preprocessing_many_ids(list_of_ids=None):
    frame_width, frame_height, frame_fps, total = read_video_info()

    # initial threshold for video of 720 x 576 and 25 fps is 30 pixels / frame
    abnormal_threshold = 30 * (frame_height / 576) * (25 / frame_fps)
    # print('abnormal threshold', abnormal_threshold)
    ma_window = int(30 * frame_fps / 50) if int(30 * frame_fps / 50) > 0 else 1
    if ma_window > total:
        ma_window = total
    filter_window = int(25 * frame_fps / 50) if int(25 * frame_fps / 50) % 2 == 1 else int(25 * frame_fps / 50) + 1

    if list_of_ids is None:
        list_of_ids = [0, 1]

    for _id in list_of_ids:
        print("Removing zero data...")
        remove_zero_data(_id)
        print("Calculating MA...")
        data_moving_average(_id, window_size=ma_window,
                            in_file=const.PREFIX + const.MATLAB_RAW_DATA_REMOVE_ZERO_DATA,
                            out_file=const.PREFIX + const.MATLAB_MOVING_AVERAGE_DATA)
        print("Removing sudden data using MA...")
        remove_sudden_changes_using_ma(_id, abnormal_threshold * ma_window / 5)
        print("Filtering...")
        # window must be an odd: 3, 5, 7, 9, etc
        if filter_window < 3:
            print(f'Cannot apply fine-filtering because the window is {filter_window}, less than default polyorder=2')
        else:
            data_filtering(_id, window=filter_window)


def run_for_many_videos(big_folder_pose=None):
    list_of_dirs = folder_list_giving_parent_folder(big_folder_pose)
    for _dir in list_of_dirs:
        const.INPUT_FOLDER = _dir
        update_prefix()
        data_preprocessing_many_ids()


if __name__ == "__main__":
    big_pose_dir = r"X:\\PCI-PD\\Sensors Final Test\\"
    run_for_many_videos(big_folder_pose=big_pose_dir)
