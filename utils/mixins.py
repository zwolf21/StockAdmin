from django.db.models import Q
from django.db import models
from six import string_types
from django.db.models.fields.files import FieldFile


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


# DB 삭제시 파일 필드의 실제 파일도 같이 삭제
class DeleteWithFileMixin(object):
	def get_queryset(self):
		class DeleteQueryset(models.query.QuerySet):
			def delete(self, don_deletes=None):				
				for instance in self:
					for attr in instance.__dict__:
						if attr in [don_deletes] if isinstance(don_deletes, string_types) else don_deletes or []:
							continue
						field = getattr(instance, attr)
						if isinstance(field, FieldFile):
							field.delete()
				return super(DeleteQueryset, self).delete()
		return DeleteQueryset(self.model, using=self._db)