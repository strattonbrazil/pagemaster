#!/usr/bin/env python

import sys
from PyQt4 import QtGui, QtCore, QtWebKit

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from pagedialog import PageDialog
from editor import WorkspaceEditor
from models import Story, Page

class Workspace(QtGui.QWidget):
    def __init__(self):
        super(Workspace, self).__init__()
        self.setMouseTracking(True)

        self._selectedPage = None
        self._hoverPage = None
        self._activeButton = None
        self._editor = None

        self.story = Story()

        self.story.createPage('first page')
        self.story.createPage('second page', QtCore.QPoint(100, 100))
        self.story.createPage('third page', QtCore.QPoint(200, 200))
        self.story.createPage('fourth page', QtCore.QPoint(300, 300))

    def editor(self):
        if not self._editor:
            self._editor = WorkspaceEditor(self)
        return self._editor

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.fillRect(0, 0, self.width(), self.height(), QtCore.Qt.darkGray)

        # calculate positions
        #
        for page in self.story.getPages():
            if 'position' not in page.meta:
                page.meta['position'] = { 'x' : 50, 'y' : 50 }

            fm = QtGui.QFontMetrics(painter.font())
            titleWidth = fm.width(page.title)
            titleHeight = fm.height()

            margin = 10

            boxWidth = titleWidth+margin*2
            boxHeight = titleHeight+margin*2

            # save off for picking
            page.meta['boxWidth'] = boxWidth
            page.meta['boxHeight'] = boxHeight

        # draw hover info
        #
        if self._hoverPage:
            boxPos = self._hoverPage.meta['position']
            
            painter.setBrush(QtGui.QColor(220, 220, 220))
            painter.drawRect(boxPos['x'],
                             boxPos['y'] + self._hoverPage.meta['boxHeight'] + 10,
                             80,
                             80)

        # draw option lines
        #
        for page in self.story.getPages():
            for dstPageId in page.options:
                dstPage = self.story.getPageById(dstPageId)

                p1 = page.meta['position']
                p2 = dstPage.meta['position']

                srcXOffset = page.meta['boxWidth'] / 2
                srcYOffset = page.meta['boxHeight']
                dstXOffset = dstPage.meta['boxWidth'] / 2
                
                
                painter.drawLine(p1['x'] + srcXOffset, p1['y'] + srcYOffset,
                                 p2['x'] + dstXOffset, p2['y'])


        # draw boxes
        #
        for page in self.story.getPages():
            position = page.meta['position']

            boxWidth = page.meta['boxWidth']
            boxHeight = page.meta['boxHeight']

            # draw shadow
            painter.setBrush(QtGui.QColor(20, 20, 20))
            painter.drawRect(position['x'] + 3,
                             position['y'] + 3,
                             boxWidth,
                             boxHeight)

            highlightColor = None
            if page is self._hoverPage and page is self._selectedPage:
                highlightColor = QtCore.Qt.blue
            elif page is self._selectedPage:
                highlightColor = QtCore.Qt.black
            elif page is self._hoverPage:
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

            painter.drawText(position['x']+margin,
                             position['y']+titleHeight+margin,
                             page.title)

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

        if self._hoverPage:
            setStartPageAction = menu.addAction('Set as start page')
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == setStartPageAction:
                print('set hover page as start page')
        else:
            addPageAction = menu.addAction('Add page')
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == addPageAction:
                self._createPage('new page', event.pos())

    def addPage(self, x, y):
        raise NotImplementedError()

#        self.story.pages.append({ 'title' : 'new page',
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

        if self._activeButton == None:
            pass
        elif self._activeButton == 1:
            position = self._selectedPage.meta['position']
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
                                info=self.story.pages[self._selectedPage])
            dialog.exec_()

        self.update()
'''

    def _pageUnderMouse(self, pos):
        for page in self.story.getPages():
            pagePos = page.meta['position']

            # skip unrendered pages
            if 'boxWidth' not in page.meta:
                continue

            pageRect = QtCore.QRect(page.meta['position']['x'],
                                    page.meta['position']['y'],
                                    page.meta['boxWidth'],
                                    page.meta['boxHeight'])

            if pageRect.contains(pos):
                return page

        return None

    def _setSelectedPage(self, page):
        if not page is self._selectedPage:
            self.editor().setPage(page)

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
