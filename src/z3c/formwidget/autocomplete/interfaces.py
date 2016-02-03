# -*- coding: utf-8 -*-
"""Interface definitions for z3c.formwidget.autocomplete."""

# zope imports
from zope.schema.interfaces import IVocabularyTokenized


class IQuerySource(IVocabularyTokenized):
    """A source that supports searching
    """

    def search(query_string):
        """Return values that match query."""
