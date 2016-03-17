# -*- coding: utf-8 -*-
"""Autocomplete widget definition."""

# zope imports
from z3c.form.interfaces import DISPLAY_MODE, IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.formwidget.autocomplete.browser.query import QuerySourceRadioWidget
from z3c.pagelet.browser import BrowserPagelet
from zope.browserpage import ViewPageTemplateFile
from zope.interface import implementsOnly, implementer
from zope.security.proxy import removeSecurityProxy

# local imports
from z3c.formwidget.autocomplete.browser import interfaces, resources


class AutocompleteSearch(BrowserPagelet):

    def __call__(self):
        query = self.request.get('q', None)
        if not query:
            return ''

        # Update the widget before accessing the source.
        # The source was only bound without security applied
        # during traversal before.
        self.context.update()
        source = self.context.bound_source
        source = removeSecurityProxy(source)
        # TODO: use limit?

        if query:
            terms = set(source.search(query))
        else:
            terms = set()

        return '\n'.join([
            '%s|%s' % (t.token, t.title or t.token)
            for t in sorted(terms, key=lambda t: t.title)
        ])


class AutocompleteBase(object):
    implementsOnly(interfaces.IAutocompleteWidget)

    # XXX: Due to the way the rendering of the QuerySourceRadioWidget works,
    # if we call this 'template' or use a <z3c:widgetTemplate /> directive,
    # we'll get infinite recursion when trying to render the radio buttons.
    input_template = ViewPageTemplateFile('templates/input.pt')
    display_template = ViewPageTemplateFile('templates/display.pt')

    # Options passed to jQuery auto-completer
    autoFill = False
    minChars = 3
    maxResults = 10
    mustMatch = False
    matchContains = True
    matchSubset = False
    formatItem = 'function(row, idx, count, value) { return row[1]; }'
    formatResult = 'function(row, idx, count) { return ""; }'
    parseFunction = 'formwidget_autocomplete_parser(' + formatResult + ', 1)'
    multiple = False

    # JavaScript template
    js_template = """\
    (function($) {
        $().ready(function() {
            $('#%(id)s-input-fields').data('klass','%(klass)s').data('title','%(title)s').data('input_type','%(input_type)s').data('multiple', %(multiple)s);
            $('#%(id)s-input-fields label').attr('class', 'label');
            $('#%(id)s-buttons-search').remove();
            $('#%(id)s-widgets-query').autocomplete('%(url)s', {
                autoFill: %(autoFill)s,
                minChars: %(minChars)d,
                max: %(maxResults)d,
                mustMatch: %(mustMatch)s,
                matchContains: %(matchContains)s,
                matchSubset: %(matchSubset)s,
                formatItem: %(formatItem)s,
                formatResult: %(formatResult)s,
                parse: %(parseFunction)s
            }).result(%(js_callback)s);
            %(js_extra)s
        });
    })(jQuery);
    """

    # Override this to insert additional JavaScript
    def js_extra(self):
        return ""

    def render(self):
        resources.autocomplete_js.need()
        resources.autocomplete_css.need()
        if self.mode == DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)

    def autocomplete_url(self):
        """Generate the URL that returns autocomplete results for this form
        """
        form_url = self.request.getURL()

        return "%s/++widget++%s/@@autocomplete-search" % (
            form_url,
            self.__name__,
        )

    def js(self):
        # Use a template if it exists, in case anything overrode this interface
        js_callback = 'formwidget_autocomplete_ready'
        if hasattr(self, 'js_callback_template'):
            js_callback = self.js_callback_template % dict(
                id=self.id,
                name=self.name,
                klass=self.klass,
                title=self.title,
                termCount=len(self.terms),
            )

        return self.js_template % dict(
            id=self.id,
            url=self.autocomplete_url(),
            autoFill=str(self.autoFill).lower(),
            minChars=self.minChars,
            maxResults=self.maxResults,
            mustMatch=str(self.mustMatch).lower(),
            matchContains=str(self.matchContains).lower(),
            matchSubset=str(self.matchSubset).lower(),
            formatItem=self.formatItem,
            formatResult=self.formatResult,
            parseFunction=self.parseFunction,
            klass=self.klass,
            title=self.title,
            input_type=self.input_type,
            multiple=str(self.multiple).lower(),
            js_callback=js_callback,
            js_extra=self.js_extra(),
        )


class AutocompleteSelectionWidget(AutocompleteBase, QuerySourceRadioWidget):
    """Autocomplete widget that allows single selection.
    """

    klass = u'autocomplete-selection-widget'
    input_type = 'radio'


@implementer(IFieldWidget)
def AutocompleteFieldWidget(field, request):
    return FieldWidget(field, AutocompleteSelectionWidget(request))
