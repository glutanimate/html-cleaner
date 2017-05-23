# builds zip file for AnkiWeb (among other things)

VERSION = `git describe HEAD --tags --abbrev=0`
ADDON = "html-cleaner"
ADDONDIR = "html_cleaner"

all: ui zip

clean:
	rm -rf dist
	rm $(ADDON)-*.zip

ui:
	rm -rf $(ADDON)/forms
	./tools/build_ui.sh

zip:
	rm -rf dist
	mkdir -p dist
	find . -name '*.pyc' -delete
	cp *.py dist/
	cp -r $(ADDONDIR) dist/
	cd dist && zip -r ../$(ADDON)-current.zip *
	rm -rf dist

release:
	rm -rf dist
	mkdir -p dist
	find . -name '*.pyc' -delete
	git archive --format tar $(VERSION) | tar -x -C dist/
	cd dist &&  \
		zip -r ../$(ADDON)-release-$(VERSION).zip $(ADDONDIR) *.py
	rm -rf dist