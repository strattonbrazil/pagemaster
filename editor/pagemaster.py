#!/usr/bin/env python

import sys
import os
import json
from PyQt4 import QtGui, QtCore, QtWebKit, uic

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from pagedialog import PageDialog
from editor import WorkspaceEditor
#from models import Story, Page

class Page(QtGui.QGraphicsRectItem):#ItemGroup): #RectItem):
    def __init__(self, x, y):
        super(Page, self).__init__(0, 0, 80, 20)

        self._children = []

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)

        self.setPos(x, y)

        self._textItem = QtGui.QGraphicsTextItem(self)

        self.setTitle('hello')

    def paint(self, painter, option, widget):
        super(Page, self).paint(painter, option, widget)

    def setTitle(self, title):
        self._textItem.setPlainText(title)

        self.setRect(self._textItem.boundingRect())

    def addOption(self, toPage):
        fromPage = self
        option = Option(fromPage, toPage)

        self._children.append(toPage)

        return option

class Option(QtGui.QGraphicsLineItem):
    def __init__(self, page1, page2):
        super(Option, self).__init__()
        self._from = page1
        self._to = page2

        #self.setParentItem(page1)

        self.updatePosition()

    def updatePosition(self):
        if self._from is None or self._to is None:
            return

        r1 = self._from.boundingRect()
        r2 = self._to.boundingRect()

        # take page position into account
        r1.moveTo(self._from.scenePos())
        r2.moveTo(self._to.scenePos())

        # bottom of "from"
        p1 = QtCore.QPointF(r1.x() + r1.width() * 0.5, r1.y() + r1.height())

        # top of "to"
        p2 = QtCore.QPointF(r2.x() + r2.width() * 0.5, r2.y())

        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

class Workspace(QtGui.QGraphicsView):
    def __init__(self):
        super(Workspace, self).__init__()
        #self.setMouseTracking(True)

        self._scene = QtGui.QGraphicsScene(self)
        self.setScene(self._scene)

        self.pages = []

        page1 = Page(0, 0)
        self._scene.addItem(page1)

        page2 = Page(100, 100)
        self._scene.addItem(page2)

        page3 = Page(100, 0)
        self._scene.addItem(page3)

        option = page1.addOption(page2)
        self._scene.addItem(option)

        option = page1.addOption(page3)
        self._scene.addItem(option)

        self._mode = None
        self._selectedPage = None
        self._hoverPage = None
        self._activeButton = None
        self._editor = None

        #self.story = Story()

        #self.story.createPage('first page')
        #self.story.createPage('second page', QtCore.QPoint(100, 100))
        #self.story.createPage('third page', QtCore.QPoint(200, 200))
        #self.story.createPage('fourth page', QtCore.QPoint(300, 300))

    def editor(self):
        if not self._editor:
            self._editor = WorkspaceEditor(self)
        return self._editor

    #def paintEvent(self, event):

        # call the parent code to draw scene
        #super(Workspace, self).paintEvent(event)

        # do a bit more of my own thing
        #print('repainting')

        #super(Workspace, 
        #painter = QtGui.QPainter(self)



    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def minimumSizeHint(self):
        return QtCore.QSize(700, 500)

    def storyObjAt(self, pos):
        item = self.itemAt(pos)

        # we use graphics item hierarchies and only want to deal with the parents
        while item != None and item.parentItem():
            item = item.parentItem()

        return item

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)

        item = self.storyObjAt(event.pos())

        if isinstance(item, Page):
            addOptionAction = menu.addAction('Add Option')
            setStartPageAction = menu.addAction('Set as start page')
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action is setStartPageAction:
                self.setStartPage(item)
            elif action is addOptionAction:
                self.showOptionDialog(item)
        else:
            addPageAction = menu.addAction('Add page')
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action is addPageAction:
                self.addPage(event.pos().x(), event.pos().y())

    def setStartPage(self, page):
        self._startPage = page
        self.relayoutGraph()

    def relayoutGraph(self):
        width = self.width()

        #self._startPage.setPos(0, 0)

        # store page levels, counts per level, and page index in level
        maxLevel = [1]
        levelByPage = {}
        pageIndexInLevel = {}
        levelCount = {}
        def addChildrenByLevel(page, level):
            maxLevel[0] = max(maxLevel[0], level)
            levelByPage[page] = level

            if level not in levelCount:
                levelCount[level] = 0
            levelCount[level] += 1

            pageIndexInLevel[page] = levelCount[level] - 1

            for child in page._children:
                addChildrenByLevel(child, level+1)
        addChildrenByLevel(self._startPage, 1)

        print(maxLevel)
        print(levelByPage)
        print(pageIndexInLevel)
        print(levelCount)

        queue = [self._startPage]
        while queue:
            page = queue.pop(0)

            # render page
            pageLevel = levelByPage[page]
            spacing = width / levelCount[pageLevel]

            if page is self._startPage:
                x = 0
            else:
                left = 0.5 * (width - spacing)
                x = spacing * pageIndexInLevel[page] - left
            page.setPos(x, pageLevel * 100)

            for child in page._children:
                queue.append(child)


        # update option lines based on new page positions
        for item in self._scene.items():
            if isinstance(item, Option):
                item.updatePosition()

    def addPage(self, x, y):
        page = Page(self.story.getUniquePageId())
        self.story.addPage(page)

        page.meta['position'] = { 'x' : x, 'y' : y }

        self._setSelectedPage(page)

    def showOptionDialog(self, page):
        dialog = QtGui.QInputDialog()
        dialog.setWindowTitle('Add Option')
        if dialog.exec_():
            newPage = Page(0, 200)
            self._scene.addItem(newPage)

            option = page.addOption(newPage)
            self._scene.addItem(option)

            self.relayoutGraph()

#        self.story.pages.append({ 'title' : 'new page',
#                                     'meta' : { 'position' : { 'x' : x, 'y' : y } },
#                                     })
#        self.update()

    def mousePressEvent(self, event):
        return
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
        return
        if event.button() == self._activeButton:
            self._activeButton = None

            # connect an option
            if event.button() == QtCore.Qt.MiddleButton and self._hoverPage:
            
                if self._selectedPage != self._hoverPage:
                    self.editor().addOption(self._hoverPage)

            self._mode = None
            self.update()

    def mouseMoveEvent(self, event):
        return
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

        #centralWidget = self.centralWidget()
        self.workspaceFrame.layout().addWidget(workspace)
        #self.editorFrame.layout().addWidget(workspace.editor())

        #self.fileMenu.addAction('Open Story...', workspace.openFile, QtGui.QKeySequence("Ctrl+O"))
        #self.fileMenu.addAction('Save Story...', workspace.saveFile, QtGui.QKeySequence("Ctrl+S"))
        #self.fileMenu.addAction('Save Story As...', workspace.saveFileAs)

QtCore.QCoreApplication.setOrganizationName('Night Carnival')
QtCore.QCoreApplication.setApplicationName('Pagemaster')

app = QtGui.QApplication(sys.argv)
window = AppWindow()
window.show()
app.exec_()
