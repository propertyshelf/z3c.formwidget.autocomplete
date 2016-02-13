# -*- coding: utf-8 -*-
"""Location-specific autocomplete widget definition."""

# zope imports
from z3c.form.interfaces import DISPLAY_MODE, IFieldWidget, NO_VALUE
from z3c.form.widget import FieldWidget
from zope.browserpage import ViewPageTemplateFile
from zope.component import queryUtility
from zope.interface import implementer

# mls imports
from propertyshelf.lib.location import utils

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
    fallback_js_template = """
(function($) {{
  $("#{id}-fallback").hide();
  $("#{id}-fallback_enabled").change(function() {{
    if ($(this).is(":checked")) {{
      $("#{id}-fallback").slideDown();
    }} else {{
      $("#{id}-fallback").slideUp();
    }}
  }})
  if ($("form select#{id}-country").length > 0) {{
    var $form = $('form select#{id}-country').closest('form');
    var $loc_0 = $('#{id}-country').find("option:selected").attr('value');
    var $loc_1 = $('#{id}-subdivision').find("option:selected").attr('value');
    var $loc_2 = $('#{id}-region').find("option:selected").attr('value');
    var $loc_3 = $('#{id}-district').find("option:selected").attr('value');
    $('#{id}-country').attr({{'data-selected': $loc_0}});
    $('#{id}-subdivision').attr({{'data-selected': $loc_1}}).empty();
    $('#{id}-region').attr({{'data-selected': $loc_2}}).empty();
    $('#{id}-district').attr({{'data-selected': $loc_3}}).empty();
    $form.relatedSelects({{
      "{id}-subdivision": {{
        depends: "{id}-country",
        loadingMessage: "...",
        source: "@@location-subdivisions?loc_field_id={name}.country",
        onLoadingStart: function() {{
          $(this).empty();
          $("<option/>").val("").text("---").prependTo($(this));
        }},
        onLoadingEnd: function() {{
          // $("<option/>").val("").text("---").prependTo($(this));
        }}
      }},
      "{id}-region": {{
        depends: "{id}-subdivision",
        loadingMessage: "...",
        source: "@@location-regions?loc_field_id={name}.subdivision",
        onLoadingStart: function() {{
          $(this).empty();
          $("<option/>").val("").text("---").prependTo($(this));
        }},
        onLoadingEnd: function() {{
          // $("<option/>").val("").text("---").prependTo($(this));
        }},
        onDependencyChanged: function(satisfied, dependencies) {{
          $('#{id}-district').find("option:selected").removeAttr('selected');
          $("#{id}-district option[value='']").attr('selected', 'selected');
          $('#{id}-district').attr({{'disabled': 'disabled'}});
        }}
      }},
      "{id}-district": {{
        disableIfEmpty: true,
        depends: "{id}-region",
        loadingMessage: "...",
        source: "@@location-districts?loc_field_id={name}.region",
        onLoadingStart: function() {{
          $(this).empty();
          $("<option/>").val("").text("---").prependTo($(this));
        }},
        onLoadingEnd: function() {{
          // $("<option/>").val("").text("---").prependTo($(this));
        }}
      }}
    }}).find('#{id}-country').change();
  }}
}})(jQuery)
    """

    def __init__(self, request):
        super(LocationAutocompleteWidget, self).__init__(request)
        self.location_data = queryUtility(utils.ILocationData)
        self.current_subdivision_code = self.noValueToken
        self.current_region_code = self.noValueToken
        self.current_district_code = self.noValueToken
        self.current_city = u''

    def render(self):
        resources.autocomplete_js.need()
        resources.autocomplete_css.need()
        if self.mode == DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)

    def update(self):
        self.current_subdivision_code = self.noValueToken
        self.current_region_code = self.noValueToken
        self.current_district_code = self.noValueToken
        self.current_city = u''
        try:
            super(AutocompleteSelectionWidget, self).update()
        except LookupError:
            if self.missing_token is not None:
                data = utils.get_location_codes_from_key(self.missing_token)
                self.current_subdivision_code = data.get(
                    'loc_subdivision',
                    self.noValueToken,
                )
                self.current_region_code = data.get(
                    'loc_region',
                    self.noValueToken,
                )
                self.current_district_code = data.get(
                    'loc_district',
                    self.noValueToken,
                )
                self.current_city = data.get('city', u'')

    def extract(self, default=NO_VALUE):
        checkbox_id = '{0}.fallback_enabled'.format(self.name)
        fb_enabled = self.request.form.get(checkbox_id) == u'fallback_enabled'
        if not fb_enabled:
            return super(LocationAutocompleteWidget, self).extract(default)

        loc_country_id = '{0}.country'.format(self.name)
        loc_subdivision_id = '{0}.subdivision'.format(self.name)
        loc_region_id = '{0}.region'.format(self.name)
        loc_district_id = '{0}.district'.format(self.name)
        city_id = '{0}.city'.format(self.name)
        loc_country = self.request.form.get(loc_country_id, None)
        loc_subdivision = self.request.form.get(loc_subdivision_id, None)
        loc_region = self.request.form.get(loc_region_id, None)
        loc_district = self.request.form.get(loc_district_id, None)
        city = self.request.form.get(city_id, None)

        if loc_region is not None and len(loc_region) > 0:
            loc_region = loc_region[0]
            if not loc_region:
                loc_region = None
        if loc_district is not None and len(loc_district) > 0:
            loc_district = loc_district[0]
            if not loc_district:
                loc_district = None
        key, value = utils.get_location_key_value(
            loc_region,
            loc_district,
            city,
        )
        if key is not None:
            tool = queryUtility(utils.ILocations)
            key = tool.register(key, value)
            return (key,)
        else:
            return (self.noValueToken,)

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
        return self.fallback_js_template.format(
            id=self.id,
            name=self.name,
        )


@implementer(IFieldWidget)
def LocationAutocompleteFieldWidget(field, request):
    return FieldWidget(field, LocationAutocompleteWidget(request))
