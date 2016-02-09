# -*- coding: utf-8 -*-
"""Autocomplete widget definition."""

# zope imports
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import ISource, IContextSourceBinder

from z3c.form import interfaces, widget, term
from z3c.form.browser import radio


class SourceTerms(term.Terms):

    def __init__(self, context, request, form, field, widget, source):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = source


class QueryTerms(term.Terms):

    def __init__(self, context, request, form, field, widget, terms):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = SimpleVocabulary(terms)


class QuerySourceRadioWidget(radio.RadioWidget):
    """Query source widget that allows single selection."""

    _radio = True
    _bound_source = None
    ignoreMissing = False

    noValueLabel = u'(nothing)'

    def __call__(self):
        self.update()
        return self.render()

    @property
    def source(self):
        """We need to bind the field to the context so that vocabularies appear
        as sources
        """
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
        request_values = interfaces.NOVALUE
        if not self.ignoreRequest:
            request_values = self.extract(default=interfaces.NOVALUE)

        if request_values is not interfaces.NOVALUE:
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
            dm = getMultiAdapter(
                (self.context, self.field),
                interfaces.IDataManager,
            )
            selection = dm.query()

            if selection is interfaces.NOVALUE:
                selection = []
            elif not isinstance(selection, (tuple, set, list)):
                selection = [selection]

            for value in selection:
                if not value:
                    continue
                try:
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
            checked = not self.value or self.value[0] == self.noValueToken
            self.items.insert(0, {
                'id': self.id + '-novalue',
                'name': self.name,
                'value': self.noValueToken,
                'label': self.noValueLabel,
                'checked': checked,
            })

    def extract(self, default=interfaces.NOVALUE):
        return self.extractQueryWidget(default)

    def render(self):
        return self.renderQueryWidget()

    def updateQueryWidget(self):
        radio.RadioWidget.update(self)

    def renderQueryWidget(self):
        return radio.RadioWidget.render(self)

    def extractQueryWidget(self, default=interfaces.NOVALUE):
        return radio.RadioWidget.extract(self, default)


@implementer(interfaces.IFieldWidget)
def QuerySourceFieldRadioWidget(field, request):
    return widget.FieldWidget(field, QuerySourceRadioWidget(request))


class IgnoreMissingQuerySourceRadioWidget(QuerySourceRadioWidget):
    """Query source widget that allows single selection and ignores missing
    values.
    """
    ignoreMissing = True


@implementer(interfaces.IFieldWidget)
def IgnoreMissingQuerySourceFieldRadioWidget(field, request):
    return widget.FieldWidget(
        field,
        IgnoreMissingQuerySourceRadioWidget(request),
    )
