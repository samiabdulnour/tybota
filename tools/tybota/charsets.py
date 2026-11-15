"""Character sets an audit checks coverage against. Add a language by adding a line."""

ASCII = "".join(chr(c) for c in range(0x20, 0x7F))

LANGUAGES = {
    "english": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "czech": "ÁČĎÉĚÍŇÓŘŠŤÚŮÝŽáčďéěíňóřšťúůýž",
    "slovak": "ÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽáäčďéíĺľňóôŕšťúýž",
    "german": "ÄÖÜẞäöüß",
    "polish": "ĄĆĘŁŃÓŚŹŻąćęłńóśźż",
    "hungarian": "ÁÉÍÓÖŐÚÜŰáéíóöőúüű",
    "french": "ÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸàâæçéèêëîïôœùûüÿ",
    "spanish": "ÁÉÍÑÓÚÜáéíñóúü¿¡",
}

# Punctuation and symbols a text face needs for Czech and English setting.
TYPOGRAPHIC = "„“”‚‘’»«›‹–—…§°×%‰€&@*†©®™•·" + " "

# Worth having, not required.
NICE_TO_HAVE = "′″­‑  −±÷¼½¾¹²³"
