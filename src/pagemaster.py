#!/usr/bin/env python

import sys
import collections
from PyQt4 import QtGui, QtCore, QtWebKit

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from pagedialog import PageDialog
from editor import WorkspaceEditor

class Workspace(QtGui.QWidget):
    def __init__(self):
        super(Workspace, self).__init__()
        self.setMouseTracking(True)

        self._selectedPage = None
        self._hoverPage = None
        self._activeButton = None
        self._editor = None

        self.story = {
            'title' : '(title of story)',
            'author' : '(your name goes here)',
            'illustrator' : '(leave blank if none)',
            'start page' : '',
            'pages' : collections.OrderedDict()
            }

        self._createPage('first page')
        self._createPage('second page', QtCore.QPoint(100, 100))
        self._createPage('third page', QtCore.QPoint(200, 200))
        self._createPage('fourth page', QtCore.QPoint(300, 300))

    def editor(self):
        if not self._editor:
            self._editor = WorkspaceEditor(self)
        return self._editor

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.fillRect(0, 0, self.width(), self.height(), QtCore.Qt.darkGray)

        for pageTitle, pageInfo in self.story['pages'].iteritems():
            if 'meta' not in pageInfo:
                pageInfo['meta'] = {}
            if 'position' not in pageInfo['meta']:
                pageInfo['meta']['position'] = { 'x' : 50, 'y' : 50 }

            position = pageInfo['meta']['position']

            fm = QtGui.QFontMetrics(painter.font())
            titleWidth = fm.width(pageTitle)
            titleHeight = fm.height()

            margin = 10

            boxWidth = titleWidth+margin*2
            boxHeight = titleHeight+margin*2

            # draw shadow
            painter.setBrush(QtGui.QColor(20, 20, 20))
            painter.drawRect(position['x'] + 3,
                             position['y'] + 3,
                             boxWidth,
                             boxHeight)

            highlightColor = None
            if pageTitle == self._hoverPage and pageTitle == self._selectedPage:
                highlightColor = QtCore.Qt.blue
            elif pageTitle == self._selectedPage:
                highlightColor = QtCore.Qt.black
            elif pageTitle == self._hoverPage:
                highlightColor = QtCore.Qt.green

            if highlightColor:
                prehighlightMargin = 6
                painter.setBrush(highlightColor)
                painter.drawRoundedRect(position['x']-prehighlightMargin,
                                        position['y']-prehighlightMargin,
                                        boxWidth+prehighlightMargin*2,
                                        boxHeight+prehighlightMargin*2,
                                        margin, margin)

            painter.setBrush(QtCore.Qt.white)
            painter.drawRect(position['x'],
                             position['y'],
                             boxWidth,
                             boxHeight)

            # save off for picking
            pageInfo['meta']['boxWidth'] = boxWidth
            pageInfo['meta']['boxHeight'] = boxHeight

#            painter.fillRect(
#                             QtCore.Qt.yellow)
            painter.drawText(position['x']+margin,
                             position['y']+titleHeight+margin,
                             pageTitle)

        self._drawOverlay(painter)

    def _drawOverlay(self, painter):
        pass

        # gather all nodes to find range

        # render each node

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def minimumSizeHint(self):
        return QtCore.QSize(700, 500)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)

        addPageAction = menu.addAction('Add page')

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == addPageAction:
            self._createPage('new page', event.pos())

    def addPage(self, x, y):
        raise NotImplementedError()

#        self.story['pages'].append({ 'title' : 'new page',
#                                     'meta' : { 'position' : { 'x' : x, 'y' : y } },
#                                     })
#        self.update()

    def mousePressEvent(self, event):


        if self._activeButton == None:
            # TODO: change these to enumerations
            if event.button() == 1: # picking or moving
                self._setSelectedPage(self._pageUnderMouse(event.pos()))
                self._mousePick = event.pos()

                self._activeButton = event.button()            

        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == self._activeButton:
            self._activeButton = None

    def mouseMoveEvent(self, event):
        if self._activeButton == None:
            self._hoverPage = self._pageUnderMouse(event.pos())
        else:
            self._hoverPage = None

        if self._activeButton == 1:
            position = self.story['pages'][self._selectedPage]['meta']['position']
            xDiff = event.pos().x() - self._mousePick.x()
            yDiff = event.pos().y() - self._mousePick.y()
            position['x'] = position['x'] + xDiff
            position['y'] = position['y'] + yDiff
            self._mousePick = event.pos()

        self.update()

        '''
    def mouseDoubleClickEvent(self, event):
        if self._selectedPage:
            dialog = PageDialog(self, 
                                title=self._selectedPage,
                                info=self.story['pages'][self._selectedPage])
            dialog.exec_()

        self.update()
'''

    def _pageUnderMouse(self, pos):
        for pageTitle,pageInfo in self.story['pages'].iteritems():
            pagePos = pageInfo['meta']['position']

            # skip unrendered pages
            if 'boxWidth' not in pageInfo['meta']:
                continue

            pageRect = QtCore.QRect(pageInfo['meta']['position']['x'],
                                    pageInfo['meta']['position']['y'],
                                    pageInfo['meta']['boxWidth'],
                                    pageInfo['meta']['boxHeight'])

            if pageRect.contains(pos):
                return pageTitle

        return None

    def _createPage(self, title, pos=None):
        uniqueTitle = title
        counter = 1
        while uniqueTitle in self.story['pages']:
            uniqueTitle = '%s_%i' % (title, counter)
            counter += 1

        self.story['pages'][uniqueTitle] = \
            {
                'image' : None,
                'content' : 'This is the beginning of your story',
                'options' : [],
                'meta' : {}
            }

        if pos:
            self.story['pages'][uniqueTitle]['meta']['position'] = \
                {
                    'x' : pos.x(),
                    'y' : pos.y()
                }

    def _setSelectedPage(self, page):
        if page != self._selectedPage:
            self.editor().updatePage(page)

        self._selectedPage = page
        

app = QtGui.QApplication(sys.argv)

window = QtGui.QMainWindow()
window.setWindowTitle('Page Master')

layout = QtGui.QHBoxLayout()
widget = QtGui.QWidget()
widget.setLayout(layout)

workspace = Workspace()

layout.addWidget(workspace)
layout.addWidget(workspace.editor())

window.setCentralWidget(widget)
window.show()

app.exec_()
