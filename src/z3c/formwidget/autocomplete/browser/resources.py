# -*- coding: utf-8 -*-
"""Fanstatic resource and library definitions."""

# python imports
from fanstatic import Library, Resource
from js.jquery import jquery


library = Library('z3c.formwidget.autocomplete', 'static')

autocomplete_jquery = Resource(
    library,
    'jquery.autocomplete.js',
    minified='jquery.autocomplete.min.js',
    depends=[jquery],
)

autocomplete_js = Resource(
    library,
    'formwidget-autocomplete.js',
    depends=[autocomplete_jquery],
)

autocomplete_css = Resource(
    library,
    'jquery.autocomplete.css',
)
