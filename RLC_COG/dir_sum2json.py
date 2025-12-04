#!/usr/bin/env python3
# coding=utf-8
#
# Permission is  hereby  granted,  free  of  charge,  to  any  person
# obtaining a copy of  this  software  and  associated  documentation
# files  (the  "Software"),  to  deal   in   the   Software   without
# restriction, including without limitation the rights to use,  copy,
# modify, merge, publish, distribute, sublicense, and/or sell  copies
# of the Software, and to permit persons  to  whom  the  Software  is
# furnished to do so.
#
# The above copyright notice and  this  permission  notice  shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT  WARRANTY  OF  ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES  OF
# MERCHANTABILITY,   FITNESS   FOR   A   PARTICULAR    PURPOSE    AND
# NONINFRINGEMENT.  IN  NO  EVENT  SHALL  THE  AUTHORS  OR  COPYRIGHT
# OWNER(S) BE LIABLE FOR  ANY  CLAIM,  DAMAGES  OR  OTHER  LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING  FROM,
# OUT OF OR IN CONNECTION WITH THE  SOFTWARE  OR  THE  USE  OR  OTHER
# DEALINGS IN THE SOFTWARE.
#
######################################################################
import argparse
import os
import json
import re

def dir2tree_data(dir_path: str) -> dict:
    forbidden_pattern = re.compile(r'[<>:"|?*\x00]')
    is_valid_path = isinstance(dir_path, str) and len(dir_path.strip()) > 0 and not forbidden_pattern.search(dir_path)

    if not is_valid_path or not os.path.isdir(dir_path):
        return {
            "name": dir_path,
            "is_dir": False,
            "children": [],
            "is_valid_path": is_valid_path,
            "path_exists": os.path.isdir(dir_path)
        }

    def build_tree(path: str) -> dict:
        node = {
            "name": os.path.basename(path) or path,
            "is_dir": os.path.isdir(path),
            "children": []
        }
        if node["is_dir"]:
            try:
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    node["children"].append(build_tree(full_path))
            except PermissionError:
                pass  # skip inaccessible directories
        return node

    tree = build_tree(dir_path)
    tree["is_valid_path"] = True
    tree["path_exists"] = True
    return tree

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate JSON tree of a directory.")
    parser.add_argument("directory", help="Path to the directory")
    args = parser.parse_args()

    tree = dir2tree_data(args.directory)
    print(json.dumps(tree, indent=2))

if __name__ == "__main__":
    main()

# ./dir_sum2json.py ~/sync/RLC/RLC_COG


# ./dir_sum2json.py John --age 25 -v