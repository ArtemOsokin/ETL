from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork, PersonRoleType


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    @classmethod
    def _aggregate_person(cls, role):
        return ArrayAgg(
            'persons__full_name',
            filter=Q(filmworkperson__role=role),
            distinct=True
        )

    def get_queryset(self):
        qset = self.model.objects.values(
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type'
        ).annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=MoviesApiMixin._aggregate_person(role=PersonRoleType.ACTOR),
            writers=MoviesApiMixin._aggregate_person(role=PersonRoleType.WRITER),
            directors=MoviesApiMixin._aggregate_person(role=PersonRoleType.DIRECTOR),
        )
        return qset

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        qset = self.get_queryset()
        paginator, page, qset, is_paginated = self.paginate_queryset(
            qset,
            self.paginate_by
        )
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(qset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return kwargs['object']
