import collections

class Story(object):
    def __init__(self):
        self.title = '(title of story)'
        self.author = '(your name goes here)'
        self.illustrator = '(leave blank if none)',
        self._startPage = None
        self._pages = collections.OrderedDict()

    def getPageById(self, id):
        return self._pages[id]

    def getPages(self):
        for page in self._pages.values():
            yield page

    def createPage(self, title, pos=None):
        uniqueId = 0
        while uniqueId in self._pages.keys():
            uniqueId += 1

        page = Page()
        page.title = title
        self._pages[uniqueId] = page

        if pos:
            page.meta['position'] = \
                {
                    'x' : pos.x(),
                    'y' : pos.y()
                }

class Page(object):
    def __init__(self):
        self.title = '(no title)'
        self.image = None
        self.content = 'This is the beginning of your story'
        self.options = []
        self.meta = {}
