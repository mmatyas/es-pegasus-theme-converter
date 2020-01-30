#! /usr/bin/env python3

import argparse
import os
import sys
from distutils.dir_util import copy_tree
from typing import Dict

from errors import print_info, print_error
from qml import create_qml
from es_reader import find_platforms
from es_items import create_default_views


def print_systems(ui_platforms):
    for system in ui_platforms:
        print_info("Platform: " + system['name'])
        if system['variables']:
            print_info("Variables:")
            for k, v in system['variables'].items():
                print_info(f"  - {k}: {v}")
        if system['views']:
            print_info("Views:")
            for viewtype, elems in system['views'].items():
                print_info(f"  - {viewtype}: {len(elems)} elem")
                for elem in elems:
                    print_info(f"    - {elem['type']} {elem['name']} extra:{elem['is_extra']}")
                    for prop in elem['params']:
                        print_info(f"      - {prop}: {elem['params'][prop]}")
        break


def has_structural_similarity(ui_platforms):
    if not ui_platforms:
        return True

    for system in ui_platforms:
        for viewtype, elems in system['views'].items():
            if viewtype not in ui_platforms[0]['views']:
                print_info(f"{system['name']}: {viewtype} not in {ui_platforms[0]['views'].keys()}")
                return False
            if len(elems) != len(ui_platforms[0]['views'][viewtype]):
                print_info(f"{system['name']}: {len(elems)} != {len(ui_platforms[0]['views'][viewtype])}")
                return False
            for idx, _ in enumerate(elems):
                if elems[idx]['type'] != ui_platforms[0]['views'][viewtype][idx]['type']:
                    print_info(f"{system['name']}: at idx {idx} {elems[idx]['type']} != {ui_platforms[0]['views'][viewtype][idx]['type']}")
                    return False

    return True


def dump_files(files: Dict[str, str], out_root: str):
    hashmark_header = \
        "# Autogenerated content, do not edit by hand!\n" + \
        "# converter v0.1.0\n" + \
        "\n"
    # "# " + str(datetime.now()) + "\n" + \
    qml_header = hashmark_header.replace('#', '//')

    idx_cur = 0
    # idx_max = len(out_files)
    for relpath, contents in files.items():
        actual_path = os.path.join(out_root, relpath)
        os.makedirs(os.path.dirname(actual_path), exist_ok=True)
        with open(actual_path, 'wt') as file:
            # print(f"[{idx_cur + 1:3}/{idx_max:3}] Writing `{actual_path}`...")
            if actual_path.endswith('.qml') or actual_path.endswith('.js'):
                file.write(qml_header)
            else:
                file.write(hashmark_header)
            file.write(contents)
        idx_cur += 1


def copy_resources(targetdir: str):
    dirname = '__es_resources'
    copy_tree(sys.path[0] + '/' + dirname, targetdir + '/' + dirname)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('INPUTDIR', help="directory of the ES theme")
    parser.add_argument('OUTPUTDIR', help="directory where generated content should be written", nargs='?')
    # parser.add_argument('-v', '--verbose', help="verbose output", action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    theme_name = os.path.basename(os.path.abspath(args.INPUTDIR))
    platforms = find_platforms(args.INPUTDIR)
    default_views = create_default_views(args.INPUTDIR)

    out_files = create_qml(theme_name, platforms, default_views)
    if args.OUTPUTDIR:
        print_info("Writing files...")
        dump_files(out_files, args.OUTPUTDIR)
        copy_resources(args.OUTPUTDIR)

    # print(has_structural_similarity(ui_platforms))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as err:
        print_error(err)
