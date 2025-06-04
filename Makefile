VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
ACTIVATE := source $(VENV_DIR)/bin/activate

# The Kindle Publishing Guidelines recommend -c2 (huffdic compression),
# but it is excruciatingly slow. That's why -c1 is selected by default.
# Compression currently is not officially supported by Kindle Previewer according to the documentation
COMPRESSION ?= 1

# Sets the max sentences per entry
# If there are too many sentences for the combined dictionary,
# it will not build (exceeds 650MB size limit). The amount is limited to 0 in this makefile for the combined.mobi
SENTENCES ?= 5

# This flag determines wheter only good and verified sentences are used in the
# dictionary. Set it to TRUE if you only want those sentences.
# It is only used by jmdict.mobi
# It is ignored bei combined.mobi. There it is always true
# This is due to size constraints.
ONLY_CHECKED_SENTENCES ?= FALSE

# If true adds pronunciations to entries. The combined dictionary ignores this flag due to size constraints
PRONUNCIATIONS ?= TRUE

# If true adds additional information to entries. The combined dictionary ignores this flag due to size constraints
ADDITIONAL_INFO ?= TRUE


ifeq ($(PRONUNCIATIONS), TRUE)
	FLAGS += -p
endif

ifeq ($(ADDITIONAL_INFO), TRUE)
	FLAGS += -i
endif


# Create virtual environment if it doesn't exist
venv:
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@$(ACTIVATE) && pip install -r requirements.txt

all: jmdict jmnedict combined

cache:
	mkdir $@

JMdict_e.gz:
	wget -nv -N http://ftp.edrdg.org/pub/Nihongo/$@

JMnedict.xml.gz:
	wget -nv -N http://ftp.edrdg.org/pub/Nihongo/$@

sentences.tar.bz2:
	wget -nv -N https://downloads.tatoeba.org/exports/$@

jpn_indices.tar.bz2:
	wget -nv -N https://downloads.tatoeba.org/exports/$@


jmdict: venv JMdict_e.gz sentences.tar.bz2 jpn_indices.tar.bz2
ifeq ($(ONLY_CHECKED_SENTENCES), TRUE)
	$(PYTHON) jmdict.py -s $(SENTENCES) -d j $(FLAGS)
else
	$(PYTHON) jmdict.py -a -s $(SENTENCES) -d j $(FLAGS)
endif

jmnedict: venv JMnedict.xml.gz style.css JMnedict-Frontmatter.html
	$(PYTHON) jmdict.py -d n $(FLAGS)

combined: venv JMdict_e.gz JMnedict.xml.gz sentences.tar.bz2 jpn_indices.tar.bz2
	if [ $(SENTENCES) -gt 2 ]; then \
		$(PYTHON) jmdict.py -s 2 -d c ; \
	else  \
		$(PYTHON) jmdict.py -s $(SENTENCES) -d c ; \
	fi

clean:
	rm -rf *.opf entry-*.html *cover.jpg *.tar.bz2 *.gz *.csv *cover.png *.tmp *.zip out cache

clean_all: clean
	rm -rf *.mobi

.PHONY: all clean jmdict jmnedict combined venv
