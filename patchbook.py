#!/usr/bin/env python3
"""
PATCHBOOK MARKUP LANGUAGE & PARSER
CREATED BY SPEKTRO AUDIO
http://spektroaudio.com/
"""

import argparse
import logging
import sys

from parser import PatchbookParser

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

if __name__ == "__main__":
    # Parse script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-file", type=str, default="",
                        help="Name of the text file that will be parsed (including extension)")
    parser.add_argument("-debug", type=int, default=0,
                        help="Enable Debugging Mode")
    parser.add_argument("-dir", type=str, default="LR",
                        help="Graph direction: LR (left-to-right) or DN (top-to-bottom)")
    parser.add_argument("-modules", action="store_const", const="modules", dest="command",
                        help="Print all modules")
    parser.add_argument("-print", action="store_const", const="print", dest="command",
                        help="Print data structure")
    parser.add_argument("-export", action="store_const", const="export", dest="command",
                        help="Print JSON")
    parser.add_argument("-connections", action="store_const", const="connections", dest="command",
                        help="Print connections")
    parser.add_argument("-graph", action="store_const", const="graph", dest="command",
                        help="Print dot code for graph")
    args = parser.parse_args()

    filename = args.file
    direction = args.dir

    if args.command:
        one_shot_command = args.command
        quiet = True
    else:
        one_shot_command = None
        quiet = False

    connectionID = 0

    if args.debug == 1:
        logger.setLevel(logging.DEBUG)

    p = PatchbookParser()
    p.initial_print()
    p.parse_file(filename)
    p.ask_command()
