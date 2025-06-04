jmdict-stardict
=====

What is this?
-------------

This is a **Japanese-English dictionary** in the Stardict format based on the
[JMdict](http://www.edrdg.org/jmdict/j_jmdict.html)
and [JMnedict](https://www.edrdg.org/enamdict/enamdict_doc.html)
and [Tatoeba](https://tatoeba.org/) databases.
It is intended for use with [KOReader](https://koreader.rocks) or any other E-reader software
that supports Stardict dictionaries. It includes **pitch accent** information and
**example sentences** and supports **lookup of inflected verbs**.

It is a fork of [jmdict-kindle](https://github.com/jmdict-kindle/jmdict-kindle),
leveraging [PyGlossary](https://github.com/ilius/pyglossary/) to adapt it to the
Stardict format.

Why is this?
------------

Other Japanese-English Stardict dictionaries online lack
[pitch accent](https://en.wikipedia.org/wiki/Japanese_pitch_accent)
and example sentences, aren't updated regularly and aren't easy to customize or extend.
This is generated using a Python script and the latest JMDict data,
making it simple to keep up to date or customize.

Download
--------

Coming soon™️

Build
-----

Requires `python`, `pip`, `wget`.

```sh
# General dictionary:
make jmdict
# Name dictionary:
make jmnedict
# Both combined in one dictionary:
make combined
```

You can change the variables in the `Makefile`
to customize things like the number of example sentences
per entry, or whether to include pitch accent.

To do
-----

 [-] Add screenshots

 [-] Provide ready-to-use builds

 [-] Improve KOReader CSS


Credits
-------

* José Fonseca for creating the original [Kindle version](https://github.com/jmdict-kindle/jmdict-kindle/tree/main)
* Jim Breen and the [JMdict/EDICT project](http://www.edrdg.org/jmdict/j_jmdict.html) as well as the [ENAMDICT/JMnedict](https://www.edrdg.org/enamdict/enamdict_doc.html)
* The [Tatoeba](https://tatoeba.org/) project
* John Mettraux for his [EDICT2 Japanese-English Kindle dictionary](https://github.com/jmettraux/edict2-kindle)
* Choplair-network for their [Nihongo conjugator](http://www.choplair.org/?Nihongo%20conjugator)
* javdejong for the [pronunciation data and the parser](https://github.com/javdejong/nhk-pronunciation)
* mifunetoshiro for the [additional pronunciation data](https://github.com/mifunetoshiro/kanjium/blob/main/data/source_files/raw/accents.txt)
