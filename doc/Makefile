doc:
	npm install docco
	node_modules/.bin/docco -l linear Semanticizer.js
	node_modules/.bin/docco -l linear advanced.js
	node_modules/.bin/docco -l linear learning.js

all: doc

publish: all
	rsync -av docs/ zookma:/datastore/applications/semanticize/doc/

watch:
	watch "*.js" 1s "make publish" 
