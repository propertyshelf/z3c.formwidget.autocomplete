Introduction
============

z3c.formwidget.autocomplete is a z3c.form widget that is based on
plone.formwidget.autocomplete but is stripped of all its Plone and Zope2
dependencies.

It uses the jQuery Autocomplete widget, and has graceful fallback for non-
Javascript browsers. There is a single-select version
(AutocompleteFieldWidget) for Choice fields, and a multi-select one
(AutocompleteMultiFieldWidget) for collection fields (e.g. List, Tuple)
with a value_type of Choice.

When using this widget, the vocabulary/source has to provide the IQuerySource
interface from z3c.formwidget.query and have a search() method.

