#!/usr/bin/python
import sys, os, json, tempfile, subprocess, time
from collections import defaultdict, OrderedDict
import weasyprint
import markdown

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

#from reportlab.pdfgen import canvas
#from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
#from reportlab.lib.styles import getSampleStyleSheet

if len(sys.argv) < 2:
    print('usage: toPdf.py title.story.json')
    quit()

# read story data
#
story = json.load(open(sys.argv[1], 'r'))

def genSectionHtml(section, pageIndexBySectionId={}):
    html = '<div style="page-break-after: always">'

    # add title and content
    html += '<h1 id="section%i">%s</h1>' % (section['id'], section['title'])
    if section['image']:
        html += '<div class="section-image-ctn"><img class="section-image" src="file://%s"></div>' % section['image']
    html += markdown.markdown(section['content'])

    # add options
    if section['options']:
        html += '<div class="options-block">'
        for choice, dstSectionId in section['options']:
            dstSectionId = 'section%i' % dstSectionId
            if dstSectionId in pageIndexBySectionId:
                dstPageNum = pageIndexBySectionId[dstSectionId] + 1
            else:
                dstPageNum = 'X X' # placeholder for spacing
            html += '<p class="option-text">%s, go to page %s</p>' % (choice, dstPageNum)
        html += '</div>'
    else:
        html += '<div class="end-block">The End</div>'

    html += '</div>'

    return html

def getPdfPages(path):
    with open(path, 'r') as fd:
        parser = PDFParser(fd)

        document = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = PDFDevice(rsrcmgr)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        pages = []
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            pages.append({
                'layout' : device.get_result()
            })

            #for group in layout.groups:
            #    if group.get_text().startswith('section'):
            #        print(dir(page))
        return pages

mainCssPath = os.path.dirname(os.path.realpath(__file__)) + '/style.css'

# find the first page
for i,section in enumerate(story['pages']):
    if section['id'] is story['start page']:
        story['pages'][0], story['pages'][i] = story['pages'][i], story['pages'][0]
        break

# build the html with dummy page references
sectionPages = {}
for section in story['pages']:
    sectionId = 'section%i' % section['id']
    sectionHtml = genSectionHtml(section)
    doc = weasyprint.HTML(string=sectionHtml)
    doc.write_pdf('/tmp/section.pdf', stylesheets=[mainCssPath])

    sectionPages[sectionId] = getPdfPages('/tmp/section.pdf')

# map the section to a given page
pageCount = 0
pageIndexBySectionId = {}
for section in story['pages']:
    sectionId = 'section%i' % section['id']
    pageIndexBySectionId[sectionId] = pageCount
    pageCount += len(sectionPages[sectionId])

# reorder the options to be ascending
def getOptionPage(option):
    optionId = 'section%i' % option[1]
    return pageIndexBySectionId[optionId]
for section in story['pages']:
    section['options'] = sorted(section['options'], key=getOptionPage)        

# rebuild the html with proper references
storyHtml = ''
for section in story['pages']:
    sectionId = 'section%i' % section['id']
    storyHtml += genSectionHtml(section, pageIndexBySectionId)
doc = weasyprint.HTML(string=storyHtml)
doc.write_pdf('/tmp/story.pdf', stylesheets=[mainCssPath])

# rebuild the individual sections to verify page counts haven't changed
for section in story['pages']:
    sectionId = 'section%i' % section['id']
    sectionHtml = genSectionHtml(section)
    doc = weasyprint.HTML(string=sectionHtml)
    doc.write_pdf('/tmp/section.pdf', stylesheets=[mainCssPath])

    assert len(sectionPages[sectionId]) == len(getPdfPages('/tmp/section.pdf'))

#htmlNoLinks = genHtml()
#docNoLinks = weasyprint.HTML(string=htmlNoLinks)
#weasyNoLinks = docNoLinks.render()
#docNoLinks.write_pdf('/tmp/placeholders.pdf', stylesheets=[mainCssPath])

sectionIdToPageNum = {}



quit()

# map sections to pages
#pageIndexBySection = {}
#for pageIndex,page in enumerate(weasyNoLinks.pages):
#    assert(len(page.anchors) < 2)

#    if len(page.anchors) is 1:
#        sectionId = page.anchors.keys()[0]
#        pageIndexBySection[sectionId] = pageIndex
#print(pageIndexBySection)

#print('# of pages before: %i' % len(weasyNoLinks.pages))

# rebuild the html
#htmlWithLinks = genHtml(pageIndexBySection)
#docWithLinks = weasyprint.HTML(string=htmlWithLinks)
#docWithLinks.write_pdf('/tmp/test.pdf', stylesheets=[mainCssPath])

# verify the pages match after swapping out placeholders
for pageIndex,page in enumerate(docWithLinks.render().pages):
    assert(len(page.anchors) < 2)

    if len(page.anchors) is 1:
        sectionId = page.anchors.keys()[0]
        assert pageIndexBySection[sectionId] is pageIndex, 'placeholder swap changed page layout: %s' % sectionId

print('# of pages after: %i' % len(docWithLinks.render().pages))

for page in docWithLinks.render().pages:
    print(page.anchors)

subprocess.call(['evince', '/tmp/test.pdf'])

