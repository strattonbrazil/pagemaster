#!/usr/bin/python
import sys, os, json, tempfile, subprocess, time
from collections import defaultdict
import weasyprint

#from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import letter
#from reportlab.platypus import Image

if len(sys.argv) < 2:
    print('usage: toPdf.py title.story.json')
    quit()

# read story data
#
story = json.load(open(sys.argv[1], 'r'))

#c = canvas.Canvas('/tmp/reportlab_test.pdf')
#c.drawCentredString(415, 500, "Something here")
#c.showPage()
#c.save()

#subprocess.call(['evince', '/tmp/reportlab_test.pdf'])
#print(story)

pagesById = {}
for page in story['pages']:
    pagesById[page['id']] = page

def genHtml(pageIndexBySection={}):
    content = ''
    html = ''
    for page in story['pages']:
        html += '<div style="page-break-after: always">'

        # add title and content
        html += '<h1 id="section%i">%s</h1>' % (page['id'], page['title'])
        html += '<p>%s</p>' % (page['content']*3)

        # add options
        if 'options' in page:
            for choice, dstPageId in page['options']:
                dstPageSectionId = 'section%i' % dstPageId
                if dstPageSectionId in pageIndexBySection:
                    dstPageNum = pageIndexBySection[dstPageSectionId] + 1
                else:
                    dstPageNum = 'X X' # placeholder for spacing
                html += '<p>choose to %s, go to page %s</p>' % (choice, dstPageNum)

        html += '</div>'

    return html

mainCssPath = os.path.dirname(os.path.realpath(__file__)) + '/style.css'

# build the html with dummy page references
htmlNoLinks = genHtml()
docNoLinks = weasyprint.HTML(string=htmlNoLinks)
weasyNoLinks = docNoLinks.render()
docNoLinks.write_pdf('/tmp/placeholders.pdf', stylesheets=[mainCssPath])

# map sections to pages
pageIndexBySection = {}
for pageIndex,page in enumerate(weasyNoLinks.pages):
    assert(len(page.anchors) < 2)

    if len(page.anchors) is 1:
        sectionId = page.anchors.keys()[0]
        pageIndexBySection[sectionId] = pageIndex

# rebuild the html
htmlWithLinks = genHtml(pageIndexBySection)
docWithLinks = weasyprint.HTML(string=htmlWithLinks)
docWithLinks.write_pdf('/tmp/test.pdf', stylesheets=[mainCssPath])

# verify the pages match after swapping out placeholders
for pageIndex,page in enumerate(docWithLinks.render().pages):
    assert(len(page.anchors) < 2)

    if len(page.anchors) is 1:
        sectionId = page.anchors.keys()[0]
        assert pageIndexBySection[sectionId] is pageIndex, 'placeholder swap changed page layout: %s' % sectionId

subprocess.call(['evince', '/tmp/test.pdf'])

