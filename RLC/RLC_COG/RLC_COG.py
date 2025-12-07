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

import re, os, sys, subprocess, threading, optparse, math, random, readline
rows, columns = os.popen('stty size', 'r').read().split() #http://stackoverflow.com/questions/566746#943921

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader

def open_directory():
    dir_name = QtWidgets.QFileDialog.getExistingDirectory(window, "Open Directory", "")
    if dir_name:
        populate_tree(tree_widget, dir_name)

def populate_tree_item(parent_item, path):
    entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
    for entry in entries:
        item = QtWidgets.QTreeWidgetItem([entry.name, "❌", "❌"])
        item.setData(0, QtCore.Qt.UserRole, entry.path)
        parent_item.addChild(item)
        if entry.is_dir():
            # Add a placeholder child to make it expandable
            placeholder = QtWidgets.QTreeWidgetItem()
            item.addChild(placeholder)

def populate_tree(tree_widget, dir_name):
    tree_widget.clear()
    root_name = os.path.basename(dir_name) or dir_name
    root_item = QtWidgets.QTreeWidgetItem([root_name, "❌", "❌"])
    root_item.setData(0, QtCore.Qt.UserRole, dir_name)
    tree_widget.addTopLevelItem(root_item)
    populate_tree_item(root_item, dir_name)
    root_item.setExpanded(True)

def on_item_expanded(item):
    # If it has a placeholder, populate the children
    if item.childCount() == 1 and item.child(0).text(0) == "":
        item.takeChild(0)
        path = item.data(0, QtCore.Qt.UserRole)
        populate_tree_item(item, path)

def on_selection_changed():
    items = tree_widget.selectedItems()
    if items:
        item = items[0]
        path = item.data(0, QtCore.Qt.UserRole)
        if path and os.path.isfile(path):
            with open(path, 'r') as f:
                content = f.read()
            plain_text_edit.setPlainText(content)
        else:
            plain_text_edit.clear()

def on_item_clicked(item, column):
    if column == 2:
        current = item.text(2)
        if current == "❌":
            item.setText(2, "✅")
        elif current == "✅":
            item.setText(2, "❌")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    loader = QUiLoader()
    window = loader.load("RLC_COG.ui", None)

    # Find widgets
    tree_widget = window.findChild(QtWidgets.QTreeWidget, "treeWidgetFileList")
    plain_text_edit = window.findChild(QtWidgets.QPlainTextEdit, "plainTextEditViewCurrentFile")
    menu_bar = window.findChild(QtWidgets.QMenuBar, "menubar")

    if plain_text_edit:
        plain_text_edit.setReadOnly(True)

    if tree_widget:
        tree_widget.setColumnCount(3)
        tree_widget.setHeaderLabels(["File", "sgst", "pert"])
        tree_widget.itemSelectionChanged.connect(on_selection_changed)
        tree_widget.itemExpanded.connect(on_item_expanded)
        tree_widget.itemClicked.connect(on_item_clicked)
        tree_widget.setSortingEnabled(True)
        tree_widget.sortByColumn(0, QtCore.Qt.AscendingOrder)

    # Ensure we have an Open action
    action_open = QtGui.QAction("Open", window)
    window.menuFile.addAction(action_open)

    action_open.triggered.connect(open_directory)

    window.show()
    sys.exit(app.exec())