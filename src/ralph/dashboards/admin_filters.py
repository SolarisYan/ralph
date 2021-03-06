from dj.choices.fields import ChoiceField
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from ralph.admin.helpers import get_field_by_relation_path
from ralph.dashboards.models import Graph
from ralph.dashboards.renderers import GRAPH_QUERY_SEP


class ByGraphFilter(admin.SimpleListFilter):
    title = _('Graph ID')
    parameter_name = 'graph-query'
    sep = GRAPH_QUERY_SEP
    template = 'admin/filters/by-graph.html'

    def lookups(self, request, model_admin):
        return (
            ('', ''),
        )

    def tokenize(self, query_value):
        return query_value.split(self.sep) if self.sep in query_value else (
            None, None
        )

    def queryset(self, request, queryset):
        graph_pk, graph_item = self.tokenize(self.value() or '')
        if graph_pk and graph_item:
            if graph_item == 'None':
                graph_item = None
            graph = get_object_or_404(Graph, pk=graph_pk)

            queryset = graph.apply_parital_filtering(queryset).distinct()

            field = get_field_by_relation_path(
                queryset.model,
                graph.params['labels']
            )

            if isinstance(field, ChoiceField):
                choices = field.choice_class()

                try:
                    graph_item = [
                        i[0] for i in choices if i[1] == graph_item
                    ].pop()
                except IndexError:
                    # NOTE(romcheg): Choice not found for the filter value.
                    #                Leaving it as is.
                    pass

            if not graph.has_grouping:
                queryset = queryset.filter(
                    **{graph.params['labels']: graph_item}
                )

        return queryset
