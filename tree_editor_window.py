import sys
import copy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from tree_editor import *

LOGGING = True

def log(*args):
  if LOGGING:
    print(*args)

class MainWindow(QMainWindow):
    def __init__(self):
      super().__init__()

      self.copy_action = QShortcut(QKeySequence("Ctrl+C"), self)
      self.copy_action.activated.connect(self.copyNode)

      self.paste_action = QShortcut(QKeySequence("Ctrl+V"), self)
      self.paste_action.activated.connect(lambda: self.recordAction(self.pasteNode))

      self.delete_action = QShortcut(QKeySequence("Delete"), self)
      self.delete_action.activated.connect(lambda: self.recordAction(self.deleteSelection))

      self.undo_action = QShortcut(QKeySequence("Ctrl+Z"), self)
      self.undo_action.activated.connect(self.undo)

      self.redo_action = QShortcut(QKeySequence("Ctrl+Y"), self)
      self.redo_action.activated.connect(self.redo)

      self.scene_tree = {
        'SSRMS 5ft env': [
          'PMM',
          'Lab',
          'Node 2',
          'SPDM',
        ],
        'SSRMS 2ft env': [
          'Columbus',
          'PMM',
          'MBS',
          'Node 2',
          'SPDM',
        ],
      }

      # undo/redo history
      self.tree_history = [copy.deepcopy(self.scene_tree)]
      self.tree_history_loc = 0

      self.parent_node_names = ['SSRMS', 'SPDM', 'MBS']
      self.child_node_names = [
        'PMM','Lab','Node 1','Node 2',
        'Node 3','SPDM','Columbus',
        'MBS'
      ]
      
      # central widget/layout
      self.scroll = QScrollArea() 
      self.widget = QWidget()                 
      self.vbox = QVBoxLayout()     

      # pair selector lists
      pair_maker_label = QLabel('Quick Pairs')
      pair_maker_label.setAlignment(Qt.AlignCenter)
      self.vbox.addWidget(pair_maker_label)

      self.pair_hbox = QHBoxLayout()
      self.pair_list_widget_a = QListWidget()
      self.pair_list_widget_b = QListWidget()
      pair_lists = [self.pair_list_widget_a, self.pair_list_widget_b]
      
      for k in sorted(self.parent_node_names):
         label = QListWidgetItem(k, self.pair_list_widget_a)
      for k in sorted(self.child_node_names):
         label = QListWidgetItem(k, self.pair_list_widget_b)

      for x in pair_lists:
        x.setSelectionMode(QListWidget.ExtendedSelection)
        x.itemSelectionChanged.connect(self.pairsChanged)
        x.setMaximumHeight(250)
        self.pair_hbox.addWidget(x)
      self.vbox.addLayout(self.pair_hbox)
      
      btn_add_pairs = QPushButton('add pairs')
      btn_add_pairs.clicked.connect(lambda state: self.recordAction(self.addSelectedPairs))
      self.addChildBtn(btn_add_pairs)
      self.pairs_label = QLabel()
      self.vbox.addWidget(self.pairs_label)

      # interactive scene tree
      label = QLabel("Scene")
      self.vbox.addWidget(label)

      self.scene = TreeEditor(self.scene_tree)
      self.scene.selectionChanged.connect(self.nodeSelectionChanged)
      self.view = QGraphicsView(self.scene)
      self.view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
      self.view.setDragMode(QGraphicsView.RubberBandDrag)
      self.vbox.addWidget(self.view)

      self.group_on_toggle = QCheckBox('On')
      self.group_on_toggle.clicked.connect(self.toggleNodes)
      self.group_on_toggle.setDisabled(True)

      hbox = QHBoxLayout()
      hbox.addWidget(self.group_on_toggle)
      hbox.addStretch()
      self.vbox.addLayout(hbox)

      self.widget.setLayout(self.vbox)

      # self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
      self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
      self.scroll.setWidgetResizable(True)
      self.scroll.setWidget(self.widget)
      self.setCentralWidget(self.scroll)

      self.setGeometry(600, 100, 1000, 900)
      self.setWindowTitle('Tree Editor')
      self.show()

    def addChildBtn(self, btn):
      hbox = QHBoxLayout()
      hbox.addWidget(btn)
      hbox.addStretch()
      self.vbox.addLayout(hbox)
      # self.children.append(btn)

    def recordAction(self, action):
      if self.tree_history_loc > 0:
        self.tree_history = self.tree_history[self.tree_history_loc:]
        self.tree_history_loc = 0

      # prev_tree = copy.deepcopy(self.scene_tree)
      # self.tree_history.insert(0, prev_tree)

      action()

      new_tree = copy.deepcopy(self.scene_tree)
      self.tree_history.insert(0, new_tree)

      log(f'{len(self.tree_history)} items in undo history ({sys.getsizeof(self.tree_history)} bytes)')

    def pairsChanged(self):
      pairs_text = ''
      self.pairs_selected = []
      for item_a in self.pair_list_widget_a.selectedItems():
         for item_b in self.pair_list_widget_b.selectedItems():
            pairs_text += f'{item_a.text()} vs {item_b.text()}\n'
            self.pairs_selected.append([item_a.text(), item_b.text()])
      self.pairs_label.setText(pairs_text)

    def addSelectedPairs(self):
      self.addPairs(self.pairs_selected)

    def addPairs(self, pairs):
      log('adding pairs')
      for pair in pairs:
        if pair[0] in self.scene_tree:
          if not pair[1] in self.scene_tree[pair[0]]:
            self.scene_tree[pair[0]].append(pair[1])
        else:
          self.scene_tree[pair[0]] = [pair[1]]
      
      self.scene.updateTree(self.scene_tree)
      
    def redo(self):
      if self.tree_history_loc > 0:
        self.tree_history_loc -= 1
        self.scene_tree = self.tree_history[self.tree_history_loc]
        self.scene.updateTree(self.scene_tree)

    def undo(self):
      if self.tree_history_loc < len(self.tree_history)-1:
        self.tree_history_loc += 1
        self.scene_tree = self.tree_history[self.tree_history_loc]
        self.scene.updateTree(self.scene_tree)

    def copyNode(self):
      log('copy')
      self.copied_items = []
      for item in self.scene.selectedItems():
         if type(item) == SceneTreeNode:
            log(item.text)
            self.copied_items.append(item.text)
         
    def pasteNode(self):
      new_pairs = []
      log('paste')
      for item in self.scene.selectedItems():
          if type(item) == SceneTreeNode and len(item.childItems()) > 1:
            for copied_item in self.copied_items:
              new_pairs.append([item.text, copied_item])
              self.scene_tree[item.text].append(copied_item)
      self.scene.updateTree(self.scene_tree)

    def deleteSelection(self):
      new_tree = copy.deepcopy(self.scene_tree)
      for item in self.scene.selectedItems():
        if type(item) == SceneTreeNode:
          if len(item.childItems()) > 1:
            # delete parent node
            del new_tree[item.text]
          else:
            # delete child node
            parent = item.parentItem()
            new_tree[parent.text].remove(item.text)

      self.scene_tree = new_tree 
      self.scene.updateTree(self.scene_tree)
        
    def toggleNodes(self, state):
      for item in self.scene.selectedItems():
        item.setOn(state)
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
        if len(item.childItems()):
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

app = QApplication(sys.argv)
app.setStyle("Fusion")
palette = QPalette()
palette.setColor(QPalette.Window, QColor(53, 53, 53))
palette.setColor(QPalette.WindowText, Qt.white)
palette.setColor(QPalette.Base, QColor(25, 25, 25))
palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
palette.setColor(QPalette.ToolTipBase, Qt.black)
palette.setColor(QPalette.ToolTipText, Qt.white)
palette.setColor(QPalette.Text, Qt.white)
palette.setColor(QPalette.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, Qt.red)
palette.setColor(QPalette.Link, QColor(42, 130, 218))
palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.HighlightedText, Qt.black)
app.setPalette(palette)

window = MainWindow()
window.show() 

app.exec()