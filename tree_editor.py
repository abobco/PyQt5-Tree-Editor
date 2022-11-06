from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np

class SceneTreeNode(QGraphicsRectItem):
  def __init__(self, x, y, text, parent=None):
    super().__init__(x, y, 50, 10, parent)

    self.on = True
    self.text = text
    self.on_color = QColor()
    self.on_color.setRgb(15, 135, 85)

    self.off_color = QColor()
    self.off_color.setRgb(6, 59, 37)

    self.text_on_color = Qt.white
    self.text_off_color = QColor()
    self.text_off_color.setRgb(146, 146, 146)
 
    brush = QBrush(self.on_color)
    self.setBrush(brush)

    self.text_item = QGraphicsTextItem(text, self)
    self.text_item.setPos(x,y)
    self.text_item.setDefaultTextColor(Qt.white)

    bounds = self.text_item.boundingRect()
    self.setRect(bounds)
    self.setFlags(QGraphicsItem.ItemIsSelectable)


  def setOn(self, on):
    self.on = on
    if on:
      self.setBrush(self.on_color)
      self.text_item.setDefaultTextColor(self.text_on_color)
    else:
      self.setBrush(self.off_color)
      self.text_item.setDefaultTextColor(self.text_off_color)
      

class TreeEditor(QGraphicsScene):
  def __init__(self, tree, parent=None):
    super().__init__(parent)

    self.tree = tree

    self.initTree()

  def updateTree(self, tree):
    self.tree = tree
    self.clear()
    self.initTree()

  def initTree(self):
    offset = np.array([10, 10]) # margin to the scene origin
    padding = np.array([50, 10]) # margin between tree nodes

    parent_position = offset.copy()
    for k, v in self.tree.items():
      # create parent node
      parent_node = SceneTreeNode(0, 0, k)
      parent_rect = parent_node.boundingRect()

      # create child nodes
      children = []
      child_sizes = np.zeros((len(v), 2))
      for i in range(len(v)):
        child = SceneTreeNode(0, 0, v[i], parent_node)
        child_bounds = child.boundingRect()
        child_sizes[i] = [child_bounds.width(), child_bounds.height()]
        children.append(child)


      subtree_size = np.array([
        np.max(child_sizes[:,0]) + parent_rect.width() + padding[0],
        np.sum(child_sizes[:,1]) + padding[1] * (len(v) + 1)
      ])
      
      # reposition parent node to the middle-left of child nodes
      base_position = parent_position.copy()
      base_position[1] += ((subtree_size[1] - parent_rect.height()) *0.5) 
      parent_node.setPos(base_position[0], base_position[1])
      self.addItem(parent_node)

      # reposition each child node
      curr_pos = padding.copy()
      curr_pos[1] -= (subtree_size[1]*0.5) 
      curr_pos[1] += parent_rect.height()*0.5
      curr_pos[0] += parent_rect.width()
      for i in range(len(v)):
        children[i].setPos(curr_pos[0], curr_pos[1])
        curr_pos[1] += child_sizes[i][1] + padding[1]

        # add line connections
        cb = children[i].boundingRect()
        p1 = QPointF(parent_rect.width(), parent_rect.height()*0.5)
        p2 = children[i].pos() + QPointF(0, cb.height()*0.5)
        line = QGraphicsLineItem(QLineF(p1, p2), parent_node)
        line.setPen(Qt.white)

      parent_position[1] += subtree_size[1] + offset[1]
