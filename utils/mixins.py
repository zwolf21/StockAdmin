from django.db.models import Q


class SearchFilterMixin(object):
	filter_arg_postfix = 'icontains'
	keyword_field_name = 'q'
	search_fields = tuple()

	def get_queryset(self):
		query_set = super(SearchFilterMixin, self).get_queryset()
		query = self.request.GET.get(self.keyword_field_name)
		if query:
			q = Q()
			for field in self.search_fields:
				q |= Q(**{'{}__{}'.format(field, self.filter_arg_postfix):query})
			return query_set.filter(q)
		return query_set