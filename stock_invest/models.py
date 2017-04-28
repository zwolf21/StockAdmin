import datetime
from django.db import models
from django.utils.text import slugify
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
# Create your models here.

class Invest(models.Model):
	slug = models.SlugField('재고조사번호', unique=True, editable=False)
	date = models.DateField('재고조사일자', default=datetime.date.today())
	commiter = models.ForeignKey(User, verbose_name='확인자', null=True, blank=True)

	class Meta:
		verbose_name = '재고조사'
		verbose_name_plural = '재고조사'
		ordering = ('-slug', )

	def __str__(self):
		return self.slug

	def get_absolute_url(self):
		return reverse('stock_invest:invest-detail', args=(self.slug, ))

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

	@property
	def description(self):
		first_item = self.investitem_set.first()
		count = self.investitem_set.count()
		return '{} 등 {}건'.format(first_item.drug, count) if first_item else '내역 없음'

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


	def __init__(self, *args, **kwargs):
		super(InvestItem, self).__init__(*args, **kwargs)
		self.before_updated = self.updated

	class Meta:
		verbose_name = '재고항목'
		verbose_name_plural = '재고항목'
		ordering = ('drug__name', )

	def __str__(self):
		return self.drug.name

	def save(self, *args, **kwargs):
		self.total = sum(filter(None, [self.pkg, self.rest1, self.rest2, self.rest3]))

		if not self.id:
			self.price = self.drug.price

		if self.id:
			self.pre_updated = self.before_updated
			self.completed = self.updated if self.complete else None

		return super(InvestItem, self).save(*args, **kwargs)

