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
import fnmatch

def load_ignore_patterns(dir_path: str):
    cfg_file = os.path.join(dir_path, "cog_cfg.json")
    patterns = []
    if os.path.isfile(cfg_file):
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            gignore_str = cfg.get("projectConfig", {}).get("gignore", "")
            if isinstance(gignore_str, str):
                # split on newlines, strip whitespace
                patterns = [p.strip() for p in gignore_str.splitlines() if p.strip()]
        except Exception:
            pass
    return patterns

def should_ignore(name: str, full_path: str, patterns: list) -> bool:
    for pat in patterns:
        # directory ignore (like ".git/")
        if pat.endswith("/") and name == pat.rstrip("/"):
            return True
        # glob-style ignore
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(full_path, pat):
            return True
    return False

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

    ignore_patterns = load_ignore_patterns(dir_path)

    def build_tree(path: str) -> dict:
        name = os.path.basename(path) or path
        node = {
            "name": name,
            "is_dir": os.path.isdir(path),
            "children": []
        }
        if node["is_dir"]:
            try:
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    if should_ignore(entry, full_path, ignore_patterns):
                        continue
                    node["children"].append(build_tree(full_path))
            except PermissionError:
                pass
        return node

    file_tree = build_tree(dir_path)
    file_tree["is_valid_path"] = True
    file_tree["path_exists"] = True
    return file_tree

def ftree2bashtree(ftree):
    """
    Convert a file tree dict into a bash-style tree output string.
    """
    def recurse(node, prefix="", last=True):
        lines = []
        connector = "└── " if last else "├── "
        lines.append(prefix + connector + node["name"])
        if node.get("is_dir", False):
            children = sorted(node["children"], key=lambda x: x["name"])
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                new_prefix = prefix + ("    " if last else "│   ")
                lines.extend(recurse(child, new_prefix, is_last))
        return lines

    lines = ["."]
    if ftree.get("is_dir", False):
        children = sorted(ftree["children"], key=lambda x: x["name"])
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            lines.extend(recurse(child, "", is_last))
    return "\n".join(lines)

def ftree2sums(ftree, parent_path=""):
    """
    Convert a file tree dict into a flat list of file entries.
    Only includes files, not directories.
    """
    files = []
    current_path = os.path.join(parent_path, ftree["name"])
    if ftree.get("is_dir", False):
        for child in ftree.get("children", []):
            files.extend(ftree2sums(child, current_path))
    else:
        rel_path = os.path.normpath(current_path)
        if not rel_path.startswith("./"):
            rel_path = "./" + rel_path.lstrip("./")
        files.append({
            "name": rel_path,
            "sum": False,
            "time": False
        })
    return files

def main():
    parser = argparse.ArgumentParser(description="Generate JSON tree of a directory.")
    parser.add_argument("directory", help="Path to the directory")
    args = parser.parse_args()

    ftree = dir2tree_data(args.directory)
    # print(json.dumps(ftree, indent=2))
    flist = ftree2sums(ftree)
    print(json.dumps(flist, indent=2))
    print(ftree2bashtree(ftree))

if __name__ == "__main__":
    main()

# ./dir_sum2json.py ~/sync/RLC/RLC_COG


# ./dir_sum2json.py John --age 25 -v