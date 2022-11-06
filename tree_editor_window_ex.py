#!/ms/foss/anaconda/envs/robo/bin/python
import grp
import os
import sys
import json
import copy
import pprint

pp = pprint.PrettyPrinter(indent=2)
proj_dir = os.path.dirname(os.path.realpath(__file__))
proj_dir = os.path.dirname(proj_dir)

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from tree_editor import *


# from node_groups import std_node_groups

class App(QMainWindow):
   def __init__(self):
      super().__init__()

      self.nodes = {}

      self.nodes_loaded = {}

      self.timer = QTimer()
      self.timer.timeout.connect(self.pluginHeartbeat)
      self.timer.start(100)
      self.pairs_selected = {}


      self.setWindowTitle('Tree Editor')
      self.setGeometry(10,  10, 800, 800)
      self.initUI()
      self.updateTreeState()
      self.show()


   def updateTreeState(self):

      # new_groups = copy.deepcopy(self.nodes_loaded)

      # def refreshItems(msg, widgets, list_widget):
      #    for w in widgets:
      #       item = list_widget.takeItem(list_widget.row(w))
      #       del item
         
      #    widgets.clear()
      #    for k, v in msg.items():
      #       item = QListWidgetItem(k, list_widget)
      #       item.setForeground(Qt.green)
      #       widgets.append(item)

      msg = {}

      if self.nodes_loaded != msg:
         self.nodes_loaded = msg

         for k, v in msg.items():
            self.nodes[k] = v    

         self.grp_list_widget.clear()
         self.pair_list_widget_a.clear()
         self.pair_list_widget_b.clear()
         for k in sorted(self.nodes):
            item0 = QListWidgetItem(k, self.grp_list_widget)
            item1 = QListWidgetItem(k, self.pair_list_widget_a)
            item2 = QListWidgetItem(k, self.pair_list_widget_b)


   def addChildBtn(self, btn):
      hbox = QHBoxLayout()
      hbox.addWidget(btn)
      hbox.addStretch()
      self.vbox.addLayout(hbox)
      self.children.append(btn)

   def groupChanged(self, group, prev):
      # print('group:', group)
      self.list_widget.clear()
      for n in sorted(self.nodes[group.text()]):
         label = QListWidgetItem(n, self.list_widget)
         self.group_nodes.append(label)
      # hbox.addWidget(self.list_widget)
      # self.vbox.addLayout(hbox)

   def pairAChanged(self):
      # for i in range(self.pair_list_widget_b.count()):
      #    # self.pair_list_widget_b.item(i).setHidden(False)
      #    item_b = self.pair_list_widget_b.item(i)
      #    item_b.setFlags(item_b.flags() | Qt.ItemIsSelectable)

      # for item_a in self.pair_list_widget_a.selectedItems():
      #    # print(item_a.text())
      #    for j in range(self.pair_list_widget_b.count()):
      #       item_b = self.pair_list_widget_b.item(j)
      #       if item_a.text() == item_b.text():
      #          # item_b.setHidden(True)
      #          item_b.setSelected(False) 
      #          item_b.setFlags(item_b.flags() & ~Qt.ItemIsSelectable)
      self.pairsChanged()
   
   def pairsChanged(self):
      pairs_text = ''
      self.pairs_selected = []
      for item_a in self.pair_list_widget_a.selectedItems():
         for item_b in self.pair_list_widget_b.selectedItems():
            pairs_text += f'{item_a.text()} vs {item_b.text()}\n'
            self.pairs_selected.append([item_a.text(), item_b.text()])
      self.pairs_label.setText(pairs_text)

   def getPairGraph(self):
      # pp.pprint(groups)
      pair_map = {}
      for k, v in pairs.items():
         if v[0] not in pair_map:
            pair_map[v[0]] = []
         if v[1] not in pair_map:
            pair_map[v[1]] = []

         pair_map[v[0]].append(v[1])
         pair_map[v[1]].append(v[0])

      keys_to_remove = []
      for k, v in pair_map.items():
         for group in v:
            print(k, v, pair_map[group])
            if len(pair_map[group]) < len(v):
               keys_to_remove.append(group)

      self.pair_map = {key: pair_map[key]
             for key in pair_map if key not in keys_to_remove}
      
      pp.pprint(self.pair_map)
      self.scene.updateTree(self.pair_map)

   def initUI(self):     
      self.children = []
      self.widget = QWidget()
      self.top_layout = QVBoxLayout()
      self.hbox = QHBoxLayout()                 
      self.vbox = QVBoxLayout() 
      
      self.group_hbox = QHBoxLayout()
      self.grp_list_widget = QListWidget()
      # grp_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
      for k in sorted(self.nodes):
         label = QListWidgetItem(k, self.grp_list_widget)
         # self.group_nodes.append(label)

      groups_vbox = QVBoxLayout()
      groups_label = QLabel('Groups')
      groups_vbox.addWidget(groups_label)
      groups_vbox.addWidget(self.grp_list_widget)
      self.group_hbox.addLayout(groups_vbox)
      self.grp_list_widget.currentItemChanged.connect(self.groupChanged)


      btn_refresh = QPushButton('Refresh')
      btn_refresh.clicked.connect(self.updateTreeState)
      self.addChildBtn(btn_refresh)

      # show list of nodes in group
      self.list_widget = QListWidget()
      self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
      nodes_vbox = QVBoxLayout()
      nodes_label = QLabel('Nodes in group')
      nodes_vbox.addWidget(nodes_label)
      nodes_vbox.addWidget(self.list_widget)
      self.group_hbox.addLayout(nodes_vbox)
      # self.vbox.addLayout(self.group_hbox)

      # pair selector lists
      self.pair_hbox = QHBoxLayout()
      self.pair_list_widget_a = QListWidget()
      self.pair_list_widget_b = QListWidget()
      self.pair_list_widget_a.setSelectionMode(QListWidget.ExtendedSelection)
      self.pair_list_widget_b.setSelectionMode(QListWidget.ExtendedSelection)
      self.pair_list_widget_a.itemSelectionChanged.connect(self.pairAChanged)
      self.pair_list_widget_b.itemSelectionChanged.connect(self.pairsChanged)

      pair_maker_label = QLabel('Quick Pairs')
      pair_maker_label.setAlignment(Qt.AlignCenter)
      self.vbox.addWidget(pair_maker_label)
      for k in sorted(self.nodes):
         label = QListWidgetItem(k, self.pair_list_widget_a)
         label = QListWidgetItem(k, self.pair_list_widget_b)
      self.pair_hbox.addWidget(self.pair_list_widget_a)
      self.pair_hbox.addWidget(self.pair_list_widget_b)
      self.vbox.addLayout(self.pair_hbox)
      
      btn_add_pairs = QPushButton('add pairs')
      btn_add_pairs.clicked.connect(self.addSelectedPairs)
      self.addChildBtn(btn_add_pairs)
      self.pairs_label = QLabel()
      self.vbox.addWidget(self.pairs_label)

      btn_list_groups = QPushButton('list groups')
      btn_list_groups.clicked.connect(self.listGroups)
      self.addChildBtn(btn_list_groups)

      btn_list_pairs = QPushButton('list pairs')
      btn_list_pairs.clicked.connect(self.listPairs)
      self.addChildBtn(btn_list_pairs)

      btn_pair_graph = QPushButton('pair graph')
      btn_pair_graph.clicked.connect(self.getPairGraph)
      self.addChildBtn(btn_pair_graph)

      self.pair_map = {}
      self.scene = TreeEditor(self.pair_map)
      self.scene.selectionChanged.connect(self.nodeSelectionChanged)
      self.view = QGraphicsView(self.scene)
      self.view.setDragMode(QGraphicsView.RubberBandDrag)
      self.vbox.addWidget(self.view)
      self.getPairGraph()

      self.group_on_toggle = QCheckBox('On')
      self.group_on_toggle.clicked.connect(self.toggleNodes)
      self.group_on_toggle.setDisabled(True)
      hbox = QHBoxLayout()
      hbox.addWidget(self.group_on_toggle)
      hbox.addStretch()
      self.vbox.addLayout(hbox)

      self.copied_items = []
      self.copy_btn = QPushButton('Copy')
      self.copy_btn.clicked.connect(self.copyNode)
      self.paste_btn = QPushButton('Paste')
      self.paste_btn.clicked.connect(self.pasteNode)
      hbox = QHBoxLayout()
      hbox.addWidget(self.copy_btn)
      hbox.addWidget(self.paste_btn)
      hbox.addStretch()
      self.vbox.addLayout(hbox)

      self.copy_action = QShortcut(QKeySequence("Ctrl+C"), self)
      self.copy_action.activated.connect(self.copyNode)

      self.paste_action = QShortcut(QKeySequence("Ctrl+V"), self)
      self.paste_action.activated.connect(self.pasteNode)

      # set main layout
      # self.vbox.addStretch()
      self.hbox.addLayout(self.vbox)
      self.top_layout.addLayout(self.hbox)
      self.widget.setLayout(self.top_layout) 

      # add scrollbar
      self.scroll = QScrollArea()            
      self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
      self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
      self.scroll.setWidgetResizable(True)
      self.scroll.setWidget(self.widget)  
      self.setCentralWidget(self.scroll)

   def copyNode(self):
      print('copy')
      self.copied_items = []
      for item in self.scene.selectedItems():
         if type(item) == SceneTreeNode:
            self.copied_items.append(item.text)
         
   def pasteNode(self):
      new_pairs = []
      for item in self.scene.selectedItems():
         if type(item) == SceneTreeNode and len(item.childItems()) > 1:
            for copied_item in self.copied_items:
               new_pairs.append([item.text, copied_item])
      self.addPairs(new_pairs)

   def toggleNodes(self, state):
      for item in self.scene.selectedItems():
         item.setOn(state)
         parent = item.parentItem()
         if parent is not None:
            name = parent.text + ' vs ' + item.text
            print(name)
      self.group_on_toggle.setTristate(False)


   def nodeSelectionChanged(self):
      on_count = 0
      off_count = 0
      parent_items = []

      if len(self.scene.selectedItems()):
         self.group_on_toggle.setDisabled(False)
      else:
         self.group_on_toggle.setDisabled(True)

      for item in self.scene.selectedItems():
         if len(item.childItems()) > 1:
            parent_items.append(item)
         
         if type(item) == SceneTreeNode:
            if item.on:
               on_count += 1
            else:
               off_count += 1
         
      if on_count == 0:
         self.group_on_toggle.setCheckState(Qt.Unchecked)
         self.group_on_toggle.setTristate(False)
      elif off_count == 0:
         self.group_on_toggle.setCheckState(Qt.Checked)
         self.group_on_toggle.setTristate(False)
      else:
         self.group_on_toggle.setTristate(True)
         self.group_on_toggle.setCheckState(Qt.PartiallyChecked)

      for item in parent_items:
         if item.isSelected():
            for child in item.childItems():
               child.setSelected(True)

   def addSelectedPairs(self):
      self.addPairs(self.pairs_selected)

   def addPairs(self, pairs):

      self.getPairGraph()

   def listGroups(self):
      pass

   def listPairs(self):
      pass

   


if __name__ == '__main__':
   app = QApplication(sys.argv)
   
   # dark theme
   app.setStyle("Fusion")
   palette = QPalette()
   palette.setColor(QPalette.Window, QColor(53, 53, 53))
   palette.setColor(QPalette.WindowText, QColor("white"))
   palette.setColor(QPalette.Base, QColor(25, 25, 25))
   palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
   palette.setColor(QPalette.ToolTipBase, QColor("white"))
   palette.setColor(QPalette.ToolTipText, QColor("white"))
   palette.setColor(QPalette.Text, QColor("white"))
   palette.setColor(QPalette.Button, QColor(53, 53, 53))
   palette.setColor(QPalette.ButtonText, QColor("white"))
   palette.setColor(QPalette.BrightText, QColor("red"))
   palette.setColor(QPalette.Link, QColor(42, 130, 218))
   palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
   palette.setColor(QPalette.HighlightedText, QColor("black"))
   palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("darkGray"))
   app.setPalette(palette)

   custom_font = QFont()
   custom_font.setPointSize(12)
   app.setFont(custom_font)

   ex = App()
   sys.exit(app.exec_())





