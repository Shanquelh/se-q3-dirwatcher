#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "Shanquel Scott, Gabby, Sondos and got help from John"


import sys
import time
import signal
import argparse
import os
import logging


exit_flag = False

global_dict = {}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler("file.log")
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def directory_dict(ns):
    polling_dict = dict()
    try:
        if os.path.isdir(ns.path):
            for content in os.walk(ns.path):
                files = content[2]
            for file in files:
                if file.endswith(ns.e):
                    polling_dict.setdefault(file, [])
        else:
            logger.info(f"The directory {ns.path} does not exist")
    except Exception as e:
        logger.exception(e)
    dir_finding(polling_dict, ns)


def dir_finding(polling_dict, ns):
    try:
        for file in polling_dict:
            if file not in global_dict:
                logger.info(f'{file} has been added in {ns.path}')
                global_dict[file] = []
        for file in global_dict:
            if file not in polling_dict:
                logger.info(f'{file} has been removed from {ns.path}')
                del global_dict[file]
    except Exception as e:
        logger.info(e)
    search_for_magic(ns)


def search_for_magic(ns):
    try:
        for file in global_dict:
            with open(ns.path + "/" + file) as f:
                line_files = f.readlines()
                for i, lines in enumerate(line_files):
                    if ns.magic in lines:
                        if i not in global_dict[file]:
                            global_dict[file].append(i)
                            logger.info(
                                f'{file} found magic text in this file')
    except Exception as e:
        logger.info(e)


def create_parser():
    """Create a command line parser object with 2 argument definitions."""
    parser = argparse.ArgumentParser(
        description="In search of magic phrases")
    parser.add_argument(
        '-e', help='extension of the file', default=".txt")
    parser.add_argument(
        '-i', help='polling interval', default=1)
    parser.add_argument(
        'path', help='path to watch for')
    parser.add_argument(
        'magic', help='creates a magic string')
    return parser


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag
    # log the associated signal name
    logger.warning('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def main(args):
    parser = create_parser()
    ns = parser.parse_args(args)
    global exit_flag
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.
    while not exit_flag:
        try:
            # call my directory watching function
            directory_dict(ns)
            time.sleep(1.0)
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            logger.exception(e)

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        # time.sleep(polling_interval = 1000)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start


if __name__ == '__main__':
    main(sys.argv[1:])
