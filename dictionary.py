# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 Jose Fonseca
# All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from collections import namedtuple
from html import escape
from datetime import date
from io import StringIO
from shutil import copy
from os import makedirs

from kana import *
from pronunciation import format_pronunciations

from pyglossary.glossary_v2 import Glossary

NAME_ENTRY, VOCAB_ENTRY = range(2)
NAME_INDEX, VOCAB_INDEX = range(2)

SEP = '・'

Ortho = namedtuple("Ortho", ["value", "rank", "inflgrps"])

Kanji = namedtuple("Kanji", ["keb", "rank"])


class Reading:
    def __init__(self, reb, rank, re_restr, pronunciation):
        self.reb = reb
        self.rank = rank
        self.re_restr = re_restr
        self.pronunciation = pronunciation


Sense = namedtuple("Sense", ["pos", "dial", "gloss", "misc", "s_inf"])


class Sentence:
    def __init__(self, english, japanese, good_sentence):
        self.english = english
        self.japanese = japanese
        self.good_sentence = good_sentence


class Entry:
    def __init__(
        self, senses, orthos, kanjis, readings, sentences=None, entry_type=VOCAB_ENTRY
    ):
        self.senses = senses
        self.orthos = orthos
        self.kanjis = kanjis
        self.readings = readings
        self.readings.sort(key=lambda reading: reading.rank)
        self.kanjis.sort(key=lambda kanji: kanji.rank)
        self.orthos.sort(key=lambda ortho: ortho.rank)
        if sentences == None:
            self.sentences = []
        else:
            self.sentences = sentences

        self.entry_type = entry_type

        self.headword = self._headword()
        # self.section = self._section()

    def _headword(self):
        # Return the first hira/kata-kana word
        for ortho in self.orthos:
            reading = ortho.value
            if reading.startswith("っ"):
                reading = reading[1:]
            if is_kana(reading[:2]):
                return reading

        # Fallback to the first reading
        return self.orthos[0].value

    def _section(self):
        # Return the first syllable of the headword

        headword = self.headword

        initial = headword[0]
        if len(headword) > 1 and headword[1] in "ゃャゅュょョァィゥェォ":
            initial += headword[1]

        return initial

    def remove(self, reading):
        assert isinstance(reading, str)
        for i in range(len(self.orthos)):
            ortho = self.orthos[i]
            if ortho.value == reading:
                self.orthos.pop(i)
                return
            else:
                for inflgrp_name, inflgrp_values in list(ortho.inflgrps.items()):
                    if reading in inflgrp_values:
                        inflgrp_values.discard(reading)
                        if not inflgrp:
                            del ortho.inflgrps[inflgrp_name]


def sort_function(entry):
    if len(entry.kanjis) > 0:
        k_rank = entry.kanjis[0].rank
    else:
        k_rank = 100
    if len(entry.readings) > 0:
        r_rank = entry.readings[0].rank
    else:
        r_rank = 100
    rank = min(k_rank, r_rank)
    if entry.entry_type == VOCAB_ENTRY:
        return f"1-{rank}-{entry.headword}"
    else:
        return f"2-{rank}-{entry.headword}"


def write_index(
    entries,
    dictionary_name,
    title,
    glossary: Glossary,
    respect_re_restr=True,
    default_index=VOCAB_INDEX,
    add_entry_info=True,
):

    # Sort entries alphabetically
    # entries.sort(key=sort_function)

    dictionary_file_name = dictionary_name.replace(" ", "_")

    for entry in entries:

        # Write HTML into a text buffer
        stream = StringIO()

        assert entry.readings
        if respect_re_restr:
            special_readings = {}
            readings = []
            for reading in entry.readings:
                if reading.re_restr:
                    if not reading.re_restr in special_readings:
                        special_readings[reading.re_restr] = []
                    special_readings[reading.re_restr].append(reading)
                readings.append(format_pronunciations(reading))
            label = SEP.join(readings)
            if entry.kanjis:
                label += (
                    "【"
                    + SEP.join(
                        [escape(kanji.keb, quote=False) for kanji in entry.kanjis]
                    )
                    + "】"
                )

            stream.write(f"<p class=lab>{label}</p>\n")

            if len(special_readings.keys()) > 0:
                for kanji in special_readings:
                    label = ""
                    readings = []
                    for reading in special_readings[kanji]:
                        readings.append(format_pronunciations(reading))
                    label = SEP.join(readings)
                    label += "【" + escape(kanji, quote=False) + "】"
                    stream.write(f"<p class=lab>{label}</p>\n")
        else:
            label = SEP.join([reading.reb for reading in entry.readings])
            if entry.kanjis:
                label += "【" + SEP.join([kanji.keb for kanji in entry.kanjis]) + "】"

        assert entry.senses

        if len(entry.senses) > 0:
            stream.write(" <ul>\n")
            for sense in entry.senses:
                stream.write("   <li>")
                if sense.pos or sense.dial or sense.misc:
                    stream.write(
                        f"      <span class=pos>{escape(', '.join(sense.pos + sense.dial + sense.misc))}</span>\n"
                    )
                stream.write(f"      {escape('; '.join(sense.gloss), quote=False)}")
                if len(sense.s_inf) > 0 and add_entry_info:
                    stream.write("<br>\n")
                    stream.write(
                        f"      《{escape('; '.join(sense.s_inf), quote=True)}》"
                    )
                stream.write("    </li>\n")
            stream.write(" </ul>\n")

        if entry.entry_type == VOCAB_ENTRY and len(entry.sentences) > 0:
            stream.write("<div class=ex>\n")
            stream.write(' <span class="exh">Examples:</span>\n')
            entry.sentences.sort(
                reverse=True, key=lambda sentence: sentence.good_sentence
            )
            for sentence in entry.sentences:
                stream.write(' <blockquote>\n')
                stream.write(f"  <span>{sentence.japanese}</span>\n")
                stream.write("  <br>\n")
                stream.write(f"  <span>{sentence.english}</span>\n")
                stream.write(" </blockquote>\n")
            stream.write("</div>\n")

        gl_entry = glossary.newEntry(word=[o.value for o in entry.orthos], defi=stream.getvalue(), defiFormat="h")
        glossary.addEntry(gl_entry)
        stream.close()

    # Write out resulting dictionary
    glossary.setInfo('name', title)
    glossary.setInfo('version', date.today().isoformat())
    glossary.setInfo('wordcount', str(len(entries)))

    output_dir = f'./out/{dictionary_file_name}'
    makedirs(output_dir, exist_ok=True)

    glossary.write(f'{output_dir}/{dictionary_file_name}.ifo', format='StardictMergeSyns')
    copy('style.css', f'{output_dir}/{dictionary_file_name}.css')

