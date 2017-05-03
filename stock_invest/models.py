import datetime
from collections import Counter
from django.db import models
from django.db.models import Q, Count, Sum, Min, Max
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib.auth.models import User
# Create your models here.

class Invest(models.Model):
	slug = models.SlugField('재고조사번호', unique=True, editable=False)
	date = models.DateField('재고조사일자', default=datetime.date.today())
	commiter = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='담당자', null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	class Meta:
		verbose_name = '재고조사'
		verbose_name_plural = '재고조사'
		ordering = ('-created', )

	def __str__(self):
		return self.slug

	def get_absolute_url(self):
		return reverse('stock_invest:invest-update', args=(self.slug, ))


	def save(self, *args, **kwargs):
		if not self.id:
			str_date = self.date.strftime("%Y%m%d")
			number = Invest.objects.filter(date=self.date).count() + 1

			while True:
				slug = slugify('{} {:03d}'.format(str_date, number))
				if Invest.objects.filter(slug=slug).exists():
					number+=1
				else:
					self.slug = slug
					break
		return super(Invest, self).save(*args, **kwargs)

	def previous_invest(self):
		return self.get_previous_by_created()

	def next_invest(self):
		return self.get_next_by_created()

	@property
	def description(self):
		first_item = self.investitem_set.first()
		count = self.investitem_set.count()
		count_set = self.investitem_set.values('drug__invest_class').annotate(cnt=Count('drug__invest_class'))
		c = Counter(map(lambda d: d.get('drug__invest_class'), count_set))
		return str(dict(c)).strip("{}").replace("'", "")

	@property
	def complete_late(self):
		if self.investitem_set.count() == 0:
			return '-'

		completed_items = self.investitem_set.filter(complete=True)
		total_items = self.investitem_set.all()

		return '{:2.0%}'.format(completed_items.count()/total_items.count())
	


class InvestItem(models.Model):
	invest = models.ForeignKey(Invest, verbose_name='재고조사번호', null=True, blank=True)
	drug = models.ForeignKey('info.Info', verbose_name='재고항목')
	price = models.IntegerField('재고가격', null=True, default=0, blank=True)
	doc_amount = models.IntegerField('전산재고', default=0, blank=True)
	pkg = models.IntegerField('포장', null=True, blank=True)
	rest1 = models.IntegerField('낱개1', null=True, blank=True)
	rest2 = models.IntegerField('낱개2', null=True, blank=True)
	rest3 = models.FloatField('소수점', null=True, blank=True)
	total = models.FloatField('종합', default=0.0, blank=True)
	expire = models.DateField('유효기한', null=True, blank=True)
	complete = models.BooleanField('조사완료', default=False)
	created = models.DateTimeField('생성일시', auto_now_add=True)
	updated = models.DateTimeField('변경일시', auto_now=True)
	completed = models.DateTimeField('완료일시', null=True, blank=True)
	pre_updated = models.DateTimeField('이전변경일시', null=True, blank=True)

	class Meta:
		verbose_name = '재고항목'
		verbose_name_plural = '재고항목'
		ordering = ('completed', 'drug__invest_class','drug__name', )

	def __str__(self):
		return self.drug.name

	def save(self, *args, **kwargs):
		self.total = sum(filter(None, [self.pkg, self.rest1, self.rest2, self.rest3]))

		if not self.id:
			self.price = self.drug.price

		if self.id:
			self.pre_updated = self.updated
			self.completed = datetime.datetime.now() if self.complete else None

		return super(InvestItem, self).save(*args, **kwargs)


	def previous_item(self):
		prev_dt = self.__class__.objects.filter(drug=self.drug, created__lt=self.created).aggregate(Max('created'))['created__max']
		return self.__class__.objects.get(drug=self.drug, created=prev_dt)

	def next_item(self):
		return self.get_next_by_created()

	@property
	def stock_diff(self):
		return self.total - self.doc_amount

	@property
	def diff_with_previous(self):
		prev_item = self.get_previous_item()
		if prev_item:
			return self.stock_diff - prev_item.stock_diff