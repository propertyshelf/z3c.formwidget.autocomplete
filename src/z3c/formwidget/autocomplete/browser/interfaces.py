# -*- coding: utf-8 -*-
"""Interface definitions for z3c.formwidget.autocomplete."""

# zope imports
from zope.interface import Interface
from z3c.form.interfaces import IRadioWidget, ICheckBoxWidget


class IAutocompleteWidget(Interface):
    """Marker interface for the autocomplete widget
    """

    def bound_source():
        """The bound QuerySource vocabulary as defined in
        z3c.formwidget.query"""


class IAutocompleteSelectionWidget(IAutocompleteWidget, IRadioWidget):
    """Interface for the autocomplete selection widget based of the radio
    widget."""


class IAutocompleteMultiSelectionWidget(IAutocompleteWidget, ICheckBoxWidget):
    """Interface for the autocomplete multi selection widget based of the
    checkbox widget."""
