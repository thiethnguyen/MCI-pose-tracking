#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import sys
import argparse
import pygame
from tqdm import tqdm

try:
    from openpose_handler import Input
    from Utility import const
    from Utility import utils
    from Utility.create_json_files import create_json
except ModuleNotFoundError as err:
    print('In openpose_main: ', err, ', try adding parent dir to sys.path . . .')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path + '/..')
    from openpose_handler import Input
    from Utility import const
    from Utility import utils
    from Utility.create_json_files import create_json


class Scene:
    def __init__(self, screen, _input):
        self.input = _input
        self.screen = screen

        self.sceneClock = pygame.time.Clock()
        self.backgroundColor = (0, 0, 0)
        self.screenDelay = None

    def render_webcam(self):
        frame = self.input.get_current_frame_as_image()
        self.screen.blit(frame, (0, 0))

    def render(self):
        self.render_webcam()

    def run(self):
        self.screenDelay = self.sceneClock.tick()
        self.screen.fill(self.backgroundColor)
        self.render()
        pygame.display.flip()


class Display:

    def __init__(self, filename):
        # print('----------------',Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT)
        self.input = Input(file_name=filename)
        self.total_frames = self.input.total_frames

        # not viewing the output directly
        if not no_view:
            pygame.init()
            pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
            pygame.display.set_caption("Displaying video")
            screen = pygame.display.get_surface()
            self.scene = Scene(screen, self.input)

    def run(self):
        for no_frames in tqdm(range(self.total_frames), desc="Processing frames", unit="frame"):
            if self.input.run(no_frames) == 0:
                break

            if not no_view:
                self.scene.run()
            # print("End of frame number:", no_frames)
            # print("==========================================================")
            # no_frames += 1

        print('Creating a json . . .')
        create_json(os.path.normpath(self.input.folder_csv))


if __name__ == "__main__":

    # Create the parser
    my_parser = argparse.ArgumentParser(description='Process some arguments')
    # Add the arguments
    my_parser.add_argument('--input',
                           type=str,
                           help='the file(s) or folder of input images and/or videos',
                           default=const.INPUT_FOLDER)
    my_parser.add_argument('--output',
                           type=str,
                           help='the file(s) or folder of output images and/or videos',
                           default=const.OUTPUT_FOLDER)
    my_parser.add_argument('--noview',
                           action='store_true',
                           help='noview is True meaning no output videos are displayed during processing')
    my_parser.add_argument('--skeleton',
                           action='store_true',
                           help='skeleton is True meaning skeleton results')
    my_parser.add_argument('--noheader',
                           action='store_true',
                           help='noheader is True meaning no header for csv files')
    my_parser.add_argument('--outtype',
                           type=str,
                           help='the file(s) or folder of input images and/or videos',
                           default=const.OUTPUT_TYPE)

    # Execute the parse_args() method
    args = my_parser.parse_args()

    folder_or_file = args.input
    no_view = args.noview
    const.OUTPUT_FOLDER = args.output
    const.SKELETON = args.skeleton
    const.NO_HEADER = args.noheader
    const.OUTPUT_TYPE = args.outtype

    is_file = False
    is_folder = False

    if os.path.isfile(folder_or_file):
        # print('this is a file')
        is_file = True
    elif os.path.isdir(folder_or_file):
        # print('this is a folder')
        is_folder = True
    else:
        print(f'The file or folder {folder_or_file} does not exist')
        sys.exit()

    if is_file:
        file_name = os.path.basename(folder_or_file)
        print('***************************************')
        print(file_name)
        print('***************************************')
        const.INPUT_FOLDER = os.path.dirname(folder_or_file)
        if utils.is_media_file(file_name) in ['video', 'image']:
            game = Display(filename=file_name)
            game.run()
        else:
            print(f"{file_name}: Not a video or image!")
    elif is_folder:
        print('Looking for subfolders...........')
        for root, dirs, files in os.walk(folder_or_file):
            for _file in files:
                print('***************************************')
                print(_file)
                print('***************************************')
                const.INPUT_FOLDER = os.path.dirname(os.path.join(root, _file))
                if utils.is_media_file(_file) in ['video', 'image']:
                    file_name = _file
                    # print("RUNNING folder")
                    game = Display(filename=file_name)
                    game.run()
                else:
                    print(f"{_file}: Not a video or image!")
