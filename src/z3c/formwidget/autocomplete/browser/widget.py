# -*- coding: utf-8 -*-
"""Autocomplete widget definition."""

# zope imports
from z3c.form.interfaces import DISPLAY_MODE, IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.formwidget.query.widget import QuerySourceRadioWidget
from z3c.formwidget.query.widget import QuerySourceCheckboxWidget
from z3c.pagelet.browser import BrowserPagelet
from zope.browserpage import ViewPageTemplateFile
from zope.interface import implementsOnly, implementer
from zope.security.proxy import removeSecurityProxy

# local imports
from z3c.formwidget.autocomplete.browser import interfaces, resources


class AutocompleteSearch(BrowserPagelet):

    def validate_access(self):
        return

        # content = self.context.form.context

        # # If the object is not wrapped in an acquisition chain
        # # we cannot check any permission.
        # if not IAcquirer.providedBy(content):
        #     return

        # url = self.request.getURL()
        # view_name = url[len(content.absolute_url()):].split('/')[1]

        # # May raise Unauthorized

        # # If the view is 'edit', then traversal prefers the view and
        # # restrictedTraverse prefers the edit() method present on most CMF
        # # content. Sigh...
        # if not view_name.startswith('@@') and not view_name.startswith('++'):
        #     view_name = '@@' + view_name

        # view_instance = content.restrictedTraverse(view_name)
        # sm = getSecurityManager()
        # sm.validate(content, content, view_name, view_instance)

    def __call__(self):

        # We want to check that the user was indeed allowed to access the
        # form for this widget. We can only this now, since security isn't
        # applied yet during traversal.
        self.validate_access()

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
    autoFill = True
    minChars = 2
    maxResults = 10
    mustMatch = False
    matchContains = True
    formatItem = 'function(row, idx, count, value) { return row[1]; }'
    formatResult = 'function(row, idx, count) { return ""; }'
    parseFunction = 'formwidget_autocomplete_parser(' + formatResult + ', 1)'
    multiple = False

    # JavaScript template
    js_template = """\
    (function($) {
        $().ready(function() {
            $('#%(id)s-input-fields').data('klass','%(klass)s').data('title','%(title)s').data('input_type','%(input_type)s').data('multiple', %(multiple)s);
            $('#%(id)s-buttons-search').remove();
            $('#%(id)s-widgets-query').autocomplete('%(url)s', {
                autoFill: %(autoFill)s,
                minChars: %(minChars)d,
                max: %(maxResults)d,
                mustMatch: %(mustMatch)s,
                matchContains: %(matchContains)s,
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


class AutocompleteMultiSelectionWidget(AutocompleteBase,
                                       QuerySourceCheckboxWidget):
    """Autocomplete widget that allows multiple selection
    """

    klass = u'autocomplete-multiselection-widget'
    input_type = 'checkbox'
    multiple = True


@implementer(IFieldWidget)
def AutocompleteFieldWidget(field, request):
    return FieldWidget(field, AutocompleteSelectionWidget(request))


@implementer(IFieldWidget)
def AutocompleteMultiFieldWidget(field, request):
    return FieldWidget(field, AutocompleteMultiSelectionWidget(request))
