#!/usr/bin/python
import sys, os, json, tempfile, subprocess, time
from collections import defaultdict
from pyPdf import PdfFileWriter

if len(sys.argv) < 2:
    print('usage: toPdf.py title.story.json')
    quit()

# read story data
#
story = json.load(open(sys.argv[1], 'r'))

print(story)

# write everything to latex
latexFile = tempfile.NamedTemporaryFile('w+', suffix='.tex', delete=False)
print("""
***********************************
* latex file: %s
***********************************
""" % latexFile.name)

pageTitles = []
pageRefs = defaultdict(list)

content = ''
for page in story['pages']:
    if page['title'] != story['start page']:
        content += '\\newpage\n'
    pageTitles.append(page['title'])
    content += '\n\\label{%s}\n' % page['title']

#    \includegraphics{myfig.pdf}

    content += '%s\n\n' % page['content']
    content += '\\vspace{1 em}\n'
    
    if 'options' in page: # if not story-ender
        for option in page['options']:
            choice, dstPage = option
            pageRefs[dstPage].append(page['title'])
            content += '\\noindent %s, goto page \\pageref{%s}\n\n' % (choice, dstPage)
            content += '\n'

for title in pageTitles:
    if title not in pageRefs and title != story['start page']:
        print('* warning: `%s` page is never referenced' % title)
for ref in pageRefs:
    if ref not in pageTitles:
        for title in pageRefs[ref]:
            print('* warning: `%s` page is referenced by `%s`, but never defined' % (ref, title))
print('\n...done building latex file\n')

latexFile.write(r"""
\documentclass{article}
\usepackage{lipsum}
\usepackage{graphicx}

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
