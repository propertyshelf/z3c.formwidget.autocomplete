# -*- coding: utf-8 -*-
"""Location-specific autocomplete widget definition."""

# zope imports
from z3c.form.interfaces import DISPLAY_MODE, IFieldWidget
from z3c.form.widget import FieldWidget
from zope.browserpage import ViewPageTemplateFile
from zope.component import queryUtility
from zope.interface import implementer

# mls imports
from propertyshelf.lib.location.utils import ILocationData

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

    # JavaScript template
    fallback_js_template = """\
    $(document).ready(function() {
      if ($("form select#%(id)s-country").length > 0) {
        var $form = $('form select#%(id)s-country').closest('form');
        var $country = $('#%(id)s-country').find("option:selected").attr('value');
        var $subdivision = $('#%(id)s-subdivision').find("option:selected").attr('value');
        var $region = $('#%(id)s-region').find("option:selected").attr('value');
        var $district = $('#%(id)s-district').find("option:selected").attr('value');
        $('#%(id)s-country').attr({'data-selected': $country});
        $('#%(id)s-subdivision').attr({'data-selected': $subdivision}).empty();
        $('#%(id)s-region').attr({'data-selected': $region}).empty();
        $('#%(id)s-district').attr({'data-selected': $district}).empty();
        $form.relatedSelects({
          "%(id)s-subdivision": {
            depends: "%(id)s-country",
            loadingMessage: "...",
            source: "@@location-subdivisions",
            onLoadingStart: function() {
              $(this).empty();
              $("<option/>").val("").text("---").prependTo($(this));
            },
            onLoadingEnd: function() {
              // $("<option/>").val("").text("---").prependTo($(this));
            }
          },
          "%(id)s-region": {
            depends: "%(id)s-subdivision",
            loadingMessage: "...",
            source: "@@location-regions",
            onLoadingStart: function() {
              $(this).empty();
              $("<option/>").val("").text("---").prependTo($(this));
            },
            onLoadingEnd: function() {
              // $("<option/>").val("").text("---").prependTo($(this));
            },
            onDependencyChanged: function(satisfied, dependencies) {
              $('#%(id)s-district').find("option:selected").removeAttr('selected');
              $("#%(id)s-district option[value='']").attr('selected', 'selected');
              $('#%(id)s-district').attr({'disabled': 'disabled'});
            }
          },
          "%(id)s-district": {
            disableIfEmpty: true,
            depends: "%(id)s-region",
            loadingMessage: "...",
            source: "@@location-districts",
            onLoadingStart: function() {
              $(this).empty();
              $("<option/>").val("").text("---").prependTo($(this));
            },
            onLoadingEnd: function() {
              // $("<option/>").val("").text("---").prependTo($(this));
            }
          }
        }).find('#%(id)s-country').change();
      }
    });
    """

    def __init__(self, request):
        super(LocationAutocompleteWidget, self).__init__(request)
        self.location_data = queryUtility(ILocationData)

    def render(self):
        resources.autocomplete_js.need()
        resources.autocomplete_css.need()
        if self.mode == DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)

    @property
    def current_country_name(self):
        """Return the name of the currently selected country."""
        return self.location_data.country.name

    @property
    def current_country_code(self):
        """Return the country code of the currently selected country."""
        return self.location_data.country.token

    def fallback_js(self):
        """Return the generated javascript code for populating the select
        boxes.
        """
        return self.fallback_js_template % dict(
            id=self.id,
        )


@implementer(IFieldWidget)
def LocationAutocompleteFieldWidget(field, request):
    return FieldWidget(field, LocationAutocompleteWidget(request))
