Pagemaster is a simple collection of tools for creating stories from json-formatted choose-your-own-adventure-type story content.  

### json-format

All tools operate on a json file, which contains the content for the story including general information of the overall story (author, illustrator, title), and the individual pages.  

Every json story should contain a 'title', 'author' and 'start page' field linking to the first page of the story.  Pages are keyed by unique title strings and are referenced to each other using this key.  The file should also contain a 'pages' field, an array of all the pages in the story.  

Every page field should have a unique 'title' field (referenced by other pages).  Additionally it can contain an 'image' field, which is a relative path to an image on disk.  The 'options' field is an array referencing other pages.  If no such field is present or is empty, the page is assumed to be an "ending" page and will have "The End" appended to it.  Options are a tuple consisting of the choice text and the page title that choice leads to.  

For example...

      "options" : [ [ "If you decide to go to the bank because you're lazy and for whatever reason you think its a better idea", "bank fight" ],
		    [ "If you'd rather go to the store first", "jerk clerk" ] ]

will create to choices on that particular page with correct page references...

"If you decide to go to the bank because you're lazy and for whatever reason you think its a better idea, goto page 3."

"If you'd rather go to the store first, goto page 4."

For an entire example story file see _assets/story.json_.  

### toPdf.py

_toPdf.py_ is currently the only functional tool.  Run it on the json file to get an output pdf.  

ex. ./toPdf.py story.json

### EDITOR TODO

### SCRIPT TODO

* fix placement of options footer to always be at the bottom of the screen