import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.security import checkPermission

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import ISource, IContextSourceBinder

import z3c.form.interfaces
import z3c.form.button
import z3c.form.form
import z3c.form.field
import z3c.form.widget
import z3c.form.term
import z3c.form.browser.radio
import z3c.form.browser.checkbox

HAS_AC = True
try:
    from AccessControl.interfaces import IRoleManager
except ImportError:
    HAS_AC = False


class SourceTerms(z3c.form.term.Terms):

    def __init__(self, context, request, form, field, widget, source):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

        self.terms = source


class QueryTerms(z3c.form.term.Terms):

    def __init__(self, context, request, form, field, widget, terms):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

        self.terms = SimpleVocabulary(terms)


class QuerySourceRadioWidget(z3c.form.browser.radio.RadioWidget):
    """Query source widget that allows single selection."""

    _radio = True
    _queryform = None
    _resultsform = None
    _bound_source = None
    ignoreMissing = False

    noValueLabel = u'(nothing)'

    @property
    def source(self):
        """We need to bind the field to the context so that vocabularies
        appear as sources"""
        return self.field.bind(self.context).source

    @property
    def bound_source(self):
        if self._bound_source is None:
            source = self.source
            if IContextSourceBinder.providedBy(source):
                source = source(self.context)
            assert ISource.providedBy(source)
            self._bound_source = source
        return self._bound_source

    def update(self):

        # Allow the source to provide terms until we have more specific ones
        # from the query. Things do not go well if self.terms is None

        self._bound_source = None
        source = self.bound_source

        self.terms = SourceTerms(
            self.context,
            self.request,
            self.form,
            self.field,
            self,
            source,
        )

        # If we have values in the request, use these to get the terms.
        # Otherwise, take the value from the current saved value.

        terms = []

        request_values = z3c.form.interfaces.NOVALUE
        if not self.ignoreRequest:
            request_values = self.extract(default=z3c.form.interfaces.NOVALUE)

        if request_values is not z3c.form.interfaces.NOVALUE:
            if not isinstance(request_values, (tuple, set, list)):
                request_values = (request_values,)

            for token in request_values:
                if not token or token == self.noValueToken:
                    continue
                try:
                    terms.append(source.getTermByToken(token))
                except LookupError:
                    # Term no longer available
                    if not self.ignoreMissing:
                        raise

        elif not self.ignoreContext:

            selection = zope.component.getMultiAdapter(
                (self.context, self.field),
                z3c.form.interfaces.IDataManager,
            ).query()

            if selection is z3c.form.interfaces.NOVALUE:
                selection = []
            elif not isinstance(selection, (tuple, set, list)):
                selection = [selection]

            for value in selection:
                if not value:
                    continue
                if HAS_AC and IRoleManager.providedBy(value):
                    if not checkPermission('zope2.View', value):
                        continue
                try:
                    # NOTE: Changed by zcashero from source.getTerm
                    terms.append(source.getTermByToken(value))
                except LookupError:
                    # Term no longer available
                    if not self.ignoreMissing:
                        raise

        # set terms
        self.terms = QueryTerms(
            self.context,
            self.request,
            self.form,
            self.field,
            self,
            terms,
        )

        # update widget - will set self.value
        self.updateQueryWidget()

        # add "novalue" option
        if self._radio and not self.required:
            self.items.insert(0, {
                'id': self.id + '-novalue',
                'name': self.name,
                'value': self.noValueToken,
                'label': self.noValueLabel,
                'checked': not self.value or self.value[0] == self.noValueToken,
            })

    def extract(self, default=z3c.form.interfaces.NOVALUE):
        return self.extractQueryWidget(default)

    def render(self):
        return self.renderQueryWidget()

    def __call__(self):
        self.update()
        return self.render()

    # For subclasses to override

    def updateQueryWidget(self):
        z3c.form.browser.radio.RadioWidget.update(self)

    def renderQueryWidget(self):
        return z3c.form.browser.radio.RadioWidget.render(self)

    def extractQueryWidget(self, default=z3c.form.interfaces.NOVALUE):
        return z3c.form.browser.radio.RadioWidget.extract(self, default)


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def QuerySourceFieldRadioWidget(field, request):
    return z3c.form.widget.FieldWidget(field, QuerySourceRadioWidget(request))


class IgnoreMissingQuerySourceRadioWidget(QuerySourceRadioWidget):
    """Query source widget that allows single selection and ignores missing
    values."""
    ignoreMissing = True


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def IgnoreMissingQuerySourceFieldRadioWidget(field, request):
    return z3c.form.widget.FieldWidget(
        field,
        IgnoreMissingQuerySourceRadioWidget(request),
    )
