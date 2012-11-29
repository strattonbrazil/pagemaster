#!/usr/bin/python
import sys, os, json, tempfile, subprocess, time
from pyPdf import PdfFileWriter

if len(sys.argv) < 2:
    print('usage: toPdf.py title.story.json')
    quit()

# read story data
#
story = json.load(open(sys.argv[1], 'r'))

print(story)

'''
# write every page to its own html
tmpDir = tempfile.mkdtemp()

# turn every page into its own pdf
for i,page in enumerate(story['pages']):
    html = tempfile.NamedTemporaryFile(prefix='page%i-'%i, suffix='.html', dir=tmpDir, delete=False)
    html.write(page['content'])
    print(html.name)

print(tmpDir)

# combine all pdfs into one
'''

# write everything to latex
latexFile = tempfile.NamedTemporaryFile('w+', suffix='.tex', delete=False)
print("""
***********************************
* latex file: %s
***********************************
""" % latexFile.name)

content = ''
for page in story['pages']:
    #content += '\\pagestyle{myheadings}'
    #content += '\\markright{%s}\n' % page['title']
    if page['title'] != story['start page']:
        content += '\\newpage\n'
    content += '\n\\label{%s}\n' % page['title']
    pageContent = '\n' + page['content']
#    pageContent = pageContent.replace('\n\n', '\n\n')
#    pageContent = pageContent.replace('\n', '\n\n')

    content += '%s\n\n' % pageContent
    content += '\\vspace{1 em}\n'

    if 'options' in page: # if not story-ender
        for option in page['options']:
            choice, dstPage = option
            content += '\\noindent %s, goto page \\pageref{%s}\n\n' % (choice, dstPage)
            content += '\n'

latexFile.write(r"""
\documentclass{article}
\usepackage{lipsum}

\title{%(title)s}

\begin{document}
\maketitle
\newpage
  %(content)s
\end{document}
""" % { 'title' : story['title'], 'content' : content })

# convert to pdf
#
os.chdir(os.path.dirname(latexFile.name))
latexFile.flush()

# run twice to get correct page references
subprocess.call(['pdflatex', latexFile.name])
subprocess.call(['pdflatex', latexFile.name])
latexFile.close()

print('created pdf: %s' % (latexFile.name.replace('.tex', '.pdf')))
subprocess.call(['evince', latexFile.name.replace('.tex', '.pdf')])


# update pdf with page numbers
