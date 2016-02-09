# -*- coding: utf-8 -*-
"""Interface definitions for z3c.formwidget.autocomplete."""

# zope imports
from z3c.form.interfaces import IRadioWidget


class IAutocompleteWidget(IRadioWidget):
    """Marker interface for the autocomplete widget
    """

    def bound_source():
        """The bound QuerySource vocabulary as defined in z3c.formwidget.query
        """
