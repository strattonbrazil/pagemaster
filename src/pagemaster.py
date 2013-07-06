#!/usr/bin/env python

import sys
import collections
from PyQt4 import QtGui, QtCore, QtWebKit

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

app = QtGui.QApplication(sys.argv)

window = QtGui.QMainWindow()

layout = QtGui.QHBoxLayout()
widget = QtGui.QWidget()
widget.setLayout(layout)

class Workspace(QtGui.QWidget):
    def __init__(self, *args):
        super(Workspace, self).__init__(*args)
        self.setMouseTracking(True)
        self._selectedPage = None
        self._hoverPage = None

        self.story = {
            'title' : '(title of story)',
            'author' : '(your name goes here)',
            'illustrator' : '(leave blank if none)',
            'start page' : '',
            'pages' : collections.OrderedDict([
                ('first page', { 'image' : None,
                                 'content' : 'This is the beginning of your story',
                                 'options' : [],
                                 }
                 )
                ])
            }

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

            painter.setBrush(QtCore.Qt.yellow)
            painter.drawRoundedRect(position['x'],
                                    position['y'],
                                    boxWidth,
                                    boxHeight,
                                    margin, margin)


            # save off for picking
            pageInfo['meta']['boxWidth'] = boxWidth
            pageInfo['meta']['boxHeight'] = boxHeight

#            painter.fillRect(
#                             QtCore.Qt.yellow)
            painter.drawText(position['x']+margin,
                             position['y']+titleHeight+margin,
                             pageTitle)

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def minimumSizeHint(self):
        return QtCore.QSize(700, 500)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)

        addPageAction = menu.addAction('Add page')

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == addPageAction:
            self.addPage(event.pos().x(),
                         event.pos().y())
            self.story['pages']

    def addPage(self, x, y):
        raise NotImplementedError()

#        self.story['pages'].append({ 'title' : 'new page',
#                                     'meta' : { 'position' : { 'x' : x, 'y' : y } },
#                                     })
#        self.update()

    def mousePressEvent(self, event):
        self._selectedPage = self._pageUnderMouse(event.pos())

        self.update()
#        print(event.button() )
#        print('something pressed')

    def mouseMoveEvent(self, event):
        self._hoverPage = self._pageUnderMouse(event.pos())
        self.update()

    def _pageUnderMouse(self, pos):
        for pageTitle,pageInfo in self.story['pages'].iteritems():
            pagePos = pageInfo['meta']['position']

            pageRect = QtCore.QRect(pageInfo['meta']['position']['x'],
                                    pageInfo['meta']['position']['y'],
                                    pageInfo['meta']['boxWidth'],
                                    pageInfo['meta']['boxHeight'])

            if pageRect.contains(pos):
                return pageTitle

        return None

    

workspace = Workspace()
layout.addWidget(workspace)
'''
webView = QtWebKit.QWebView()
webView.load(QtCore.QUrl('./index.html'))

layout.addWidget(webView)

def loadValue():
    doc = webView.page().mainFrame().documentElement()
    search = doc.findFirst('input[name=username]')
    search.setAttribute('value', 'Josh')
'''

button = QtGui.QPushButton('Load Value')
#button.clicked.connect(loadValue)
layout.addWidget(button)

window.setCentralWidget(widget)
window.show()

app.exec_()
