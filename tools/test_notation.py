#!/usr/bin/env python3
"""Regression checks for accidentals in MusicXML and the engraved SVG.

Run with .venv/bin/python tools/test_notation.py.
"""
import unittest
import xml.etree.ElementTree as ET

import build
import verovio


def notation(bars, key="C", other_hand=None, complete=False):
    voices = [{"id": "rh", "staff": 1, "clef": "treble", "bars": bars}]
    if other_hand:
        voices.append({"id": "lh", "staff": 2, "clef": "bass",
                       "bars": other_hand})
    doc = {
        "meta": {"complete": complete},
        "settings": {"key": key},
        "_derived": {"meter": "4/4", "beats": 4, "beat_type": 4,
                     "unit": "eighth", "per_unit": 12, "units_per_bar": 8},
        "part": [{"id": "pf", "name": "Piano", "program": 0,
                  "staves": 2 if other_hand else 1, "voice": voices}],
    }
    parts = build.build_parts(doc)
    return build.emit_musicxml(doc, parts, [96] * len(bars),
                               [["mf"] * len(bars)])


def symbols(xml):
    return [a.text for a in ET.fromstring(xml).iter("accidental")]


class Accidentals(unittest.TestCase):
    def test_final_barline_only_for_complete_score(self):
        xml = ET.fromstring(notation(["C4:8", "C4:8"], complete=True))
        measures = xml.findall("./part/measure")
        self.assertIsNone(measures[0].find("barline"))
        self.assertEqual(measures[1].findtext("barline/bar-style"), "light-heavy")
        draft = ET.fromstring(notation(["C4:8", "C4:8"]))
        self.assertEqual(draft.findall(".//barline"), [])

    def test_repeat_cancellation_and_bar_reset(self):
        xml = notation(["Ab4:2 Ab4:2 A4:2 Ab4:2", "Ab4:8"])
        self.assertEqual(symbols(xml), ["flat", "natural", "flat", "flat"])

    def test_key_signature_and_cancellation(self):
        xml = notation(["F#4:2 F4:2 F#4:2 F#4:2"], key="G")
        self.assertEqual(symbols(xml), ["natural", "sharp"])
        xml = notation(["Bb4:2 B4:2 Bb4:4"], key="F")
        self.assertEqual(symbols(xml), ["natural", "flat"])

    def test_octaves_and_staves_are_independent(self):
        xml = notation(["Ab4:4 Ab5:4"], other_hand=["Ab4:8"])
        self.assertEqual(symbols(xml), ["flat", "flat", "flat"])

    def test_svg_contains_visible_accidental_glyphs(self):
        toolkit = verovio.toolkit()
        self.assertTrue(toolkit.loadData(notation(["Ab4:4 A4:4"])))
        svg = ET.fromstring(toolkit.renderToSVG(1))
        printed = [g for g in svg.iter() if g.get("class") == "accid"
                   and list(g)]
        self.assertEqual(len(printed), 2)


if __name__ == "__main__":
    unittest.main()
