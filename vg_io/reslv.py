
# coding=utf-8
# Copyright (C) 2023-2026 Roy Pfund. All rights reserved.
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
###################################

# reslv.py

import os, re, types, typing, inspect, json, pydantic, jinja2

def Load_Plaintxt(file_path):
    """Utility to read file content safely."""
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found.", True
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read(), False
    except Exception as e:
        return f"Error reading file: {str(e)}", True

class FileDependency(pydantic.BaseModel):
    name: str
    content: str
    subtrees: typing.List["FileDependency"] = []
    raw_tag: typing.Optional[str] = None

def build_dependency_tree(file_path: str, visited: typing.Set[str] = None) -> FileDependency:
    if visited is None:
        visited = set()

    abs_path = os.path.abspath(file_path)

    if abs_path in visited:
        raise ValueError(f"Circular dependency detected: {file_path}")

    visited.add(abs_path)

    content, error = Load_Plaintxt(file_path)
    if error:
        visited.remove(abs_path)
        return FileDependency(name=file_path, content=content)

    # Matches {{{path:"./SomeFile.md"}}}
    tag_pattern = r'\{\{\{path:"([^"]+)"\}\}\}'
    dependencies = re.findall(tag_pattern, content)

    node = FileDependency(name=file_path, content=content)

    for dep_path in dependencies:
        resolved_path = os.path.abspath(os.path.join(os.path.dirname(abs_path), dep_path))
        child_node = build_dependency_tree(resolved_path, visited.copy())

        # Store the raw tag EXACTLY as it appeared in the file
        child_node.raw_tag = f'{{{{{{path:"{dep_path}"}}}}}}'

        node.subtrees.append(child_node)

    # print("FOUND DEPENDENCIES:", dependencies)
    return node


def re_solve(file_path):
    """
    Resolves recursive file dependencies and string variables 
    by looking at the caller's local variables.
    File: TestA.md = `I've got a {{{path:"./TestB.md"}}}`
    File: TestB.md =`lovely bunch of {{{path:"./TestC.md"}}}`
    File: TestC.md =`coconuts.{{{var_str:"some_str"}}}`
    def reslv_test():
        some_str = "\nAND ALSO STRINGS!!!"
        test_file = cwfd + "/coconuts/TestA.md"
        content = vg_io.reslv.re_solve(test_file)
        print(content)
    reslv_test() prints
    I've got a lovely bunch of coconuts.
    AND ALSO STRINGS!!!
    """
    # Use inspect to get the caller's locals
    # This allows main() to work without passing a dict explicitly.
    caller_frame = inspect.currentframe().f_back
    context = caller_frame.f_locals

    try:
        tree = build_dependency_tree(file_path)
    except Exception as e:
        print(f"Failed to build dependency tree: {e}")
        return

    def resolve_node(node):
        text = node.content
        
        # 1. Resolve Path Dependencies
        for sub in node.subtrees:
            if sub.raw_tag:
                text = text.replace(sub.raw_tag, resolve_node(sub))
        
        # 2. Resolve String Variables
        var_pattern = r'\{\{\{var_str:"([^"]+)"\}\}\}'
        for var_name in re.findall(var_pattern, text):
            raw_tag = f'{{{{{{var_str:"{var_name}"}}}}}}'
            # Pull from the captured context; default to the tag if not found
            replacement = str(context.get(var_name, raw_tag))
            text = text.replace(raw_tag, replacement)
            
        return text

    return resolve_node(tree)
