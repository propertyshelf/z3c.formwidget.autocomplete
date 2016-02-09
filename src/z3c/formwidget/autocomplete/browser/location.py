# -*- coding: utf-8 -*-
"""Location-specific autocomplete widget definition."""

# zope imports
from z3c.form.interfaces import DISPLAY_MODE, IFieldWidget
from z3c.form.widget import FieldWidget
from zope.browserpage import ViewPageTemplateFile
from zope.interface import implementer

# local imports
from z3c.formwidget.autocomplete.browser import resources
from z3c.formwidget.autocomplete.browser.widget import (
    AutocompleteSelectionWidget)


class LocationAutocompleteWidget(AutocompleteSelectionWidget):
    """Location-specific autocomplete widget that has extra functionality to
    dynamically provide a set of widgets to select the country, state,
    district, county, and city name.
    """

    # XXX: Due to the way the rendering of the QuerySourceRadioWidget works,
    # if we call this 'template' or use a <z3c:widgetTemplate /> directive,
    # we'll get infinite recursion when trying to render the radio buttons.
    input_template = ViewPageTemplateFile('templates/location_input.pt')
    display_template = ViewPageTemplateFile('templates/display.pt')

    def render(self):
        resources.autocomplete_js.need()
        resources.autocomplete_css.need()
        if self.mode == DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)


@implementer(IFieldWidget)
def LocationAutocompleteFieldWidget(field, request):
    return FieldWidget(field, LocationAutocompleteWidget(request))
