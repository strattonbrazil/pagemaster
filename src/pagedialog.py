from PyQt4 import QtGui, QtCore, QtWebKit

class PageDialog(QtGui.QDialog):
    def __init__(self, parent, title, info):
        super(PageDialog, self).__init__(parent)

        self.setWindowTitle('Edit: ' + title)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        upper = QtGui.QWidget()
        gridLayout1 = QtGui.QGridLayout()
        upper.setLayout(gridLayout1)
        layout.addWidget(upper)

        gridLayout1.addWidget(QtGui.QLabel('Title:'), 0, 0)
        self.titleInput = QtGui.QLineEdit()
        gridLayout1.addWidget(self.titleInput, 0, 1)

        self.editor = QtWebKit.QWebView()
        self.connect(self.editor, QtCore.SIGNAL("loadFinished(bool)"), self.render)
        self.editor.setHtml(EDITOR_HTML)
        layout.addWidget(self.editor)

    def render(self, ok):
        if ok:
            self.editor.page().mainFrame().evaluateJavaScript("alert('okay')")
            self.editor.page().mainFrame().evaluateJavaScript("""
   tinymce.init({selector:'textarea'});
""")


EDITOR_HTML = \
"""
<html>
<head><!-- CDN hosted by Cachefly -->
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js" type="text/javascript"></script>

<script src="http://tinymce.cachefly.net/4.0/tinymce.min.js"></script>
<script>
$(function() {
   tinymce.init({selector:'textarea'});
});

</script>
</head>
<body>
        <textarea>Your content here.</textarea>
</body>
</html>
"""
