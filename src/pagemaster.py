#!/usr/bin/env python

import sys
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

        self.story = {
            'title' : '(title of story)',
            'author' : '(your name goes here)',
            'illustrator' : '(leave blank if none)',
            'start page' : '',
            'pages' : [
                { 
                    'title' : 'first page',
                    'image' : None,
                    'content' : 'This is the beginning of your story',
                    'options' : []
                    }
                ]
            }

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.fillRect(0, 0, self.width(), self.height(), QtCore.Qt.darkGray)

        for page in self.story['pages']:
            if 'meta' not in page:
                page['meta'] = {}
            if 'position' not in page['meta']:
                page['meta']['position'] = { 'x' : 50, 'y' : 50 }

            position = page['meta']['position']

            fm = QtGui.QFontMetrics(painter.font())
            titleWidth = fm.width(page['title'])
            titleHeight = fm.height()

            margin = 10

            painter.setBrush(QtCore.Qt.yellow)
            painter.drawRoundedRect(position['x'],
                                    position['y'],
                                    titleWidth+margin*2,
                                    titleHeight+margin*2,
                                    margin, margin)
#            painter.fillRect(
#                             QtCore.Qt.yellow)
            painter.drawText(position['x']+margin,
                             position['y']+titleHeight+margin,
                             page['title'])

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
        self.story['pages'].append({ 'title' : 'new page',
                                     'meta' : { 'position' : { 'x' : x, 'y' : y } },
                                     })
        self.update()

    def mousePressEvent(self, event):
        print('something pressed')
    

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
