import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from tree_editor import TreeEditor

class MainWindow(QMainWindow):
    def __init__(self):
      super().__init__()

      self.scroll = QScrollArea() 
      self.widget = QWidget()                 
      self.vbox = QVBoxLayout()               

      label = QLabel("Scene")
      self.vbox.addWidget(label)

      scene_tree = {
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

      self.scene = TreeEditor(scene_tree)
      self.scene.selectionChanged.connect(self.nodeSelectionChanged)
      self.view = QGraphicsView(self.scene)
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

      self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
      self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
      self.scroll.setWidgetResizable(True)
      self.scroll.setWidget(self.widget)
      self.setCentralWidget(self.scroll)

      self.setGeometry(600, 100, 1000, 900)
      self.setWindowTitle('Tree Editor')
      self.show()

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