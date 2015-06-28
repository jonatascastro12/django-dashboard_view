from django.forms.models import ModelChoiceIterator
from django_select2.fields import ChoiceMixin


class FilterableAdvancedModelChoiceIterator(ModelChoiceIterator):
    """
    Extends ModelChoiceIterator to add the capability to apply additional
    filter on the passed queryset and also return the obj instance.
    """
    def choice(self, obj):
        return (self.field.prepare_value(obj), self.field.label_from_instance(obj), obj)

    def set_extra_filter(self, **filter_map):
        """
        Applies additional filter on the queryset. This can be called multiple times.

        :param filter_map: The ``**kwargs`` to pass to :py:meth:`django.db.models.query.QuerySet.filter`.
            If this is not set then additional filter (if) applied before is removed.
        """
        if not hasattr(self, '_original_queryset'):
            import copy
            self._original_queryset = copy.deepcopy(self.queryset)
        if filter_map:
            self.queryset = self._original_queryset.filter(**filter_map)
        else:
            self.queryset = self._original_queryset

class QuerysetAdvancedChoiceMixin(ChoiceMixin):
    """
    Overrides ``choices``' getter to return instance of :py:class:`.FilterableAdvancedModelChoiceIterator`
    instead.
    """

    def _get_choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, '_choices'):
            return self._choices

        # Otherwise, execute the QuerySet in self.queryset to determine the
        # choices dynamically. Return a fresh ModelChoiceIterator that has not been
        # consumed. Note that we're instantiating a new ModelChoiceIterator *each*
        # time _get_choices() is called (and, thus, each time self.choices is
        # accessed) so that we can ensure the QuerySet has not been consumed. This
        # construct might look complicated but it allows for lazy evaluation of
        # the queryset.
        return FilterableAdvancedModelChoiceIterator(self)

    choices = property(_get_choices, ChoiceMixin._set_choices)

    def __deepcopy__(self, memo):
        result = super(QuerysetAdvancedChoiceMixin, self).__deepcopy__(memo)
        # Need to force a new ModelChoiceIterator to be created, bug #11183
        result.queryset = result.queryset
        return result
