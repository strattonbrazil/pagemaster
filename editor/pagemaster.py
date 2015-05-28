#!/usr/bin/env python

import sys
import os
import json
from PyQt4 import QtGui, QtCore, QtWebKit, uic

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from pagedialog import PageDialog
from editor import WorkspaceEditor
from models import Story, Page

class Workspace(QtGui.QWidget):
    def __init__(self):
        super(Workspace, self).__init__()
        self.setMouseTracking(True)

        self._recentFileName = None
        self._mode = None
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

        fm = QtGui.QFontMetrics(painter.font())

        # calculate positions
        #
        for page in self.story.getPages():
            if 'position' not in page.meta:
                page.meta['position'] = { 'x' : 50, 'y' : 50 }

            titleWidth = fm.width(page.title)
            titleHeight = fm.height()

            margin = 10

            boxWidth = titleWidth+margin*2
            boxHeight = titleHeight+margin*2

            # save off for picking
            page.meta['boxWidth'] = boxWidth
            page.meta['boxHeight'] = boxHeight

        if self._mode == 'ADD_OPTION':
            boxPos = self._selectedPage.meta['position']
            cursorPos = self.mapFromGlobal(QtGui.QCursor.pos())
            painter.setBrush(QtGui.QColor(220, 220, 0))
            painter.drawLine(boxPos['x'], boxPos['y'], 
                             cursorPos.x(), cursorPos.y())

        # draw hover info
        #
        if self._hoverPage:
            boxPos = self._hoverPage.meta['position']
            
            painter.setBrush(QtGui.QColor(220, 220, 220))
            painter.drawRect(boxPos['x'],
                             boxPos['y'] + self._hoverPage.meta['boxHeight'] + 10,
                             80,
                             80)

            if self._hoverPage.imagePath:
                image = QtGui.QImage(self._hoverPage.imagePath)
                filteredImage = image.scaled(60, 60, 
                                             QtCore.Qt.IgnoreAspectRatio,
                                             QtCore.Qt.SmoothTransformation)
                target = QtCore.QRectF(boxPos['x'] + 10, 
                                       boxPos['y'] + self._hoverPage.meta['boxHeight'] + 20,
                                       60, 60)
                painter.drawImage(target, filteredImage)

        # draw option lines
        #
        for page in self.story.getPages():
            for option in page.options:
                dstPage = self.story.getPageById(option['id'])

                boxP1 = page.meta['position']
                boxP2 = dstPage.meta['position']

                srcXOffset = page.meta['boxWidth'] / 2
                srcYOffset = page.meta['boxHeight']
                dstXOffset = dstPage.meta['boxWidth'] / 2                
                
                p1 = (boxP1['x'] + srcXOffset, boxP1['y'] + srcYOffset)
                p2 = (boxP2['x'] + dstXOffset, boxP2['y'])

                painter.drawLine(p1[0], p1[1], p2[0], p2[1])

                midLineP = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

                boxPadding = 5
                stringWidth = fm.width(option['text'])
                stringOffset = stringWidth / 2
                stringHeight = fm.height()

                # draw text background
                #painter.setBrush(QtGui.QColor(220, 220, 220, 60))
                painter.fillRect(midLineP[0]-stringOffset-boxPadding, midLineP[1]-stringHeight,
                                 stringWidth+boxPadding*2, stringHeight,
                                 QtGui.QColor(220, 220, 220, 60))

                painter.drawText(midLineP[0]-stringOffset, midLineP[1], 
                                 option['text'])


        # draw page boxes
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

        if self._mode == 'BOX_SELECT':
            cursorPos = self.mapFromGlobal(QtGui.QCursor.pos())

            x = min(cursorPos.x(), self._mousePick.x())
            y = min(cursorPos.y(), self._mousePick.y())
            width = abs(cursorPos.x() - self._mousePick.x())
            height = abs(cursorPos.y() - self._mousePick.y())

            painter.setBrush(QtGui.QColor(255, 0, 255, 122))
            painter.drawRect(x, y, width, height)

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
            if action is setStartPageAction:
                self.story.setStartPage(self._hoverPage)
        else:
            addPageAction = menu.addAction('Add page')
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action is addPageAction:
                self.addPage(event.pos().x(), event.pos().y())

    def addPage(self, x, y):
        page = Page(self.story.getUniquePageId())
        self.story.addPage(page)

        page.meta['position'] = { 'x' : x, 'y' : y }

        self._setSelectedPage(page)

#        self.story.pages.append({ 'title' : 'new page',
#                                     'meta' : { 'position' : { 'x' : x, 'y' : y } },
#                                     })
#        self.update()

    def mousePressEvent(self, event):
        if self._activeButton is None:
            # picking or moving
            if event.button() == QtCore.Qt.LeftButton: 
                self._setSelectedPage(self._pageUnderMouse(event.pos()))
                self._mousePick = event.pos()

                if self._selectedPage:
                    self._mode = 'MOVE'
                else:
                    self._mode = 'BOX_SELECT'

                self._activeButton = event.button()      

            # connect an option
            elif event.button() == QtCore.Qt.MiddleButton and self._hoverPage:
                self._setSelectedPage(self._pageUnderMouse(event.pos()))
                self._mode = 'ADD_OPTION'
                self._activeButton = event.button()

        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == self._activeButton:
            self._activeButton = None

            # connect an option
            if event.button() == QtCore.Qt.MiddleButton and self._hoverPage:
            
                if self._selectedPage != self._hoverPage:
                    self.editor().addOption(self._hoverPage)

            self._mode = None
            self.update()

    def mouseMoveEvent(self, event):
        if self._activeButton is None or self._activeButton == QtCore.Qt.MiddleButton:
            self._hoverPage = self._pageUnderMouse(event.pos())
        else:
            self._hoverPage = None

        if self._activeButton == None:
            pass
        elif self._activeButton == QtCore.Qt.LeftButton:
            # drag around selected page
            if self._selectedPage:
                position = self._selectedPage.meta['position']
                xDiff = event.pos().x() - self._mousePick.x()
                yDiff = event.pos().y() - self._mousePick.y()
                position['x'] = position['x'] + xDiff
                position['y'] = position['y'] + yDiff
                self._mousePick = event.pos()

        self.update()

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
        

    def openFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Choose a file to open', '', '*.json')
        if fileName:
            with open(fileName, 'r') as fd:
                data = json.load(fd)
                self.story.fromJson(data)

                self._recentFileName = fileName

    def saveFile(self):
        if self._recentFileName:
            data = self.story.toJson()
            with open(self._recentFileName, 'w') as fd:
                json.dump(data, fd, indent=4)
        else:
            self.saveFileAs()

    def saveFileAs(self):
        data = self.story.toJson()

        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Choose a save file', '', '*.json')
        if fileName:
            with open(fileName, 'w') as fd:
                json.dump(data, fd, indent=4)
                self._recentFileName = fileName


class AppWindow(QtGui.QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()

        scriptPath = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(scriptPath + '/pagemaster.ui', self)

        workspace = Workspace()

        centralWidget = self.centralWidget()
        self.workspaceFrame.layout().addWidget(workspace)
        self.editorFrame.layout().addWidget(workspace.editor())

        self.fileMenu.addAction('Open Story...', workspace.openFile, QtGui.QKeySequence("Ctrl+O"))
        self.fileMenu.addAction('Save Story...', workspace.saveFile, QtGui.QKeySequence("Ctrl+S"))
        self.fileMenu.addAction('Save Story As...', workspace.saveFileAs)

QtCore.QCoreApplication.setOrganizationName('Night Carnival')
QtCore.QCoreApplication.setApplicationName('Pagemaster')

app = QtGui.QApplication(sys.argv)
window = AppWindow()
window.show()
app.exec_()
