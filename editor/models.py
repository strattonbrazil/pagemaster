import collections

class Story(object):
    def __init__(self):
        self.title = '(title of story)'
        self.author = '(your name goes here)'
        self.illustrator = '(leave blank if none)',
        self._startPage = None
        self._pages = collections.OrderedDict()

    def setStartPage(self, page):
        self._startPage = page

    def fromJson(self, data):
        self.title = data['title']
        self.author = data['author']
        self.illustrator = data['illustrator']
        self._startPage = None

        self._pages = collections.OrderedDict()
        for pageData in data['pages']:
            page = Page(pageData['id'])
            page.title = pageData['title']
            page.imagePath = pageData['image']
            page.content = pageData['content']
            for option in pageData['options']:
                page.options.append({ 'text' : option[0],
                                      'id' : option[1] })
            page.meta = pageData['meta']
            self._pages[page.id] = page

        if data['start page']:
            self._startPage = self.getPageById(data['start page'])

    def toJson(self):
        data = {}

        data['title'] = self.title
        data['author'] = self.author
        data['illustrator'] = self.illustrator
        if self._startPage:
            data['start page'] = self._startPage.id

        data['pages'] = []
        for page in self.getPages():
            options = []
            for option in page.options:
                options.append([option['text'], option['id']])

            data['pages'].append({
                'id'    : page.id,
                'title' : page.title,
                'image' : page.imagePath,
                'content' : page.content,
                'options' : options,
                'meta' : page.meta
            })

        return data

    def getPageById(self, id):
        return self._pages[id]

    def getPages(self):
        for page in self._pages.values():
            yield page

    def createPage(self, title, pos=None):
        uniqueId = 0
        while uniqueId in self._pages.keys():
            uniqueId += 1

        page = Page(uniqueId)
        page.title = title
        self._pages[uniqueId] = page

        if pos:
            page.meta['position'] = \
                {
                    'x' : pos.x(),
                    'y' : pos.y()
                }

class Page(object):
    def __init__(self, id):
        self.id = id
        self.title = '(no title)'
        self.imagePath = None
        self.content = 'This is the beginning of your story'
        self.options = []
        self.meta = {}
