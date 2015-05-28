#!/usr/bin/python
import sys, os, json
import xml.etree.ElementTree as ET
from xml.dom import minidom

if len(sys.argv) < 2:
    print('usage: toHtml.py title.story.json')
    quit()

# read story data
#
story = json.load(open(sys.argv[1], 'r'))

def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def titleToFileName(title):
    return '%s.html' % title.lower().replace(' ','_')

def baseStyledHtmlElement():
    html = ET.Element('html')
    comment = ET.Comment('Generated by toHtml.py of Pagemaster')
    html.append(comment)

    head = ET.SubElement(html, 'head')
    viewport = ET.SubElement(head, 'meta', 
                             { 'name' : 'viewport',
                               'content' : 'width=device-width,initial-scale=1.0,maximum-scale=2.0,user-scalable=yes' })
    style = ET.SubElement(head, 'link', { 'rel' : 'stylesheet',
                                          'type' : 'text/css',
                                          'href' : 'style.css' })

    body = ET.SubElement(html, 'body')
    return html, body

# write out starting page template 
#
print('* Creating splash page: "pagemaster_splash.html"')
html, body = baseStyledHtmlElement()
main = ET.SubElement(body, 'div', { 'id' : 'content' })
outer = ET.SubElement(main, 'div', { 'id' : 'outer'})
inner = ET.SubElement(outer, 'div', { 'id' : 'inner' })

titleDiv = ET.SubElement(inner, 'div', { 'id' : 'title' })
titleDiv.text = story['title']
splashDiv = ET.SubElement(inner, 'div', { 'id' : 'splash' })
splash = ET.SubElement(splashDiv, 'image', { 'id' : 'splashImage', 'src' : './splash.png' })
if not os.path.exists('./splash.png'):
    print('  - missing splash image: splash.png')
buttonDiv = ET.SubElement(inner, 'div', { 'class' : 'buttonDiv' })
link = ET.SubElement(buttonDiv, 'a', { 'href' : './%s' % story['start page'] })
button = ET.SubElement(link, 'button', { 'class' : 'navButton' })
button.text = 'Start'
authorDiv = ET.SubElement(inner, 'div', { 'class' : 'contributor' })
authorDiv.text = 'written by %s' % story['author']
illustratorDiv = ET.SubElement(inner, 'div', { 'class' : 'contributor' })
illustratorDiv.text = 'illustrated by %s' % story['illustrator']
footerDiv = ET.SubElement(inner, 'div')
copyright = ET.SubElement(footerDiv, 'p', { 'class' : 'footer' })
copyright.text = '&copy; Red Robot Stories 2012'
powered = ET.SubElement(footerDiv, 'p', { 'class' : 'footer' })
powered.text = 'powered by Pagemaster'

html = prettify(html)
html = html.replace('&amp;', '&')

f = open('pagemaster_splash.html', 'w')
f.write(html)

# write out to html files
#
for page in story['pages']:
    fileName = titleToFileName(page['title'])
    print('* Creating new page: "%s"' % fileName)

    html, body = baseStyledHtmlElement()

    main = ET.SubElement(body, 'div', { 'id' : 'content' })

    header = ET.SubElement(main, 'div', { 'class' : 'header' })
    header.text = page['title']



    imageDiv = ET.SubElement(main, 'div')
    image = ET.SubElement(imageDiv, 'image', {'src' : page['picture'], 'class' : 'picture' })
    if not os.path.exists(page['picture']):
        print('  - missing picture file: %s' % page['picture'])

    text = ET.SubElement(main, 'div')
    lines = page['text'].split('\n')
    for line in lines:
        p = ET.SubElement(text, 'p')
        p.text = line
#    text.text = page['text']

    for i,option in enumerate(page['options']):
        buttonDiv = ET.SubElement(main, 'div', { 'class' : 'buttonDiv' })
        if option['link'] in map(lambda page: page['title'], story['pages']):
            fileLink = titleToFileName(option['link'])
        else:
            print('  - unknown link from "%s" to "%s"' % (option['action'], option['link']))
            fileLink = '#'
        link = ET.SubElement(buttonDiv, 'a', { 'href' : './%s' % fileLink })
        button = ET.SubElement(link, 'button', { 'class' : 'navButton' })
        button.text = option['action'] 

    if len(page['options']) == 0:
        # add ending tag
        p = ET.SubElement(text, 'p', { 'class' : 'end' })
        p.text = 'THE END'

        hr = ET.SubElement(main, 'hr')

        # add etsy link
        etsyDiv = ET.SubElement(main, 'div', { 'class' : 'referenceDiv' })
        etsy = ET.SubElement(etsyDiv, 'p', { 'class' : 'reference' })
        etsy.text = 'If you enjoyed this story, visit '
        etsyLink = ET.SubElement(etsy, 'a', { 'href' : story['etsy link'] })
        etsyLink.text = 'etsy.com'
        etsyLink.tail = ' to see some of our available prints for sale.  '
        

    footerDiv = ET.SubElement(main, 'div')
    copyright = ET.SubElement(footerDiv, 'p', { 'class' : 'footer' })
    copyright.text = '&copy; Red Robot Stories 2012'
    powered = ET.SubElement(footerDiv, 'p', { 'class' : 'footer' })
    powered.text = 'powered by Pagemaster'
    

    html = prettify(html)
    html = html.replace('&amp;', '&')

    f = open(fileName, 'w')
    f.write(html)


