from django.db import models
from django.db.models import Sum, Max, Q
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
# Create your models here.
from info.models import Info




class Buy(models.Model):
	slug = models.SlugField('발주번호', unique=True, editable=False)
	date = models.DateField('발주일자')
	commiter = models.ForeignKey(User, verbose_name='발주승인자', null=True)


	class Meta:
		verbose_name='발주'
		verbose_name_plural='발주'
		ordering = ('-slug',)

	def __str__(self):
		return self.slug

	def save(self, *args, **kwargs):
		if not self.id:
			str_date = self.date.strftime("%Y%m%d")
			number = Buy.objects.filter(date=self.date).count() + 1

			while True:
				slug = slugify('{} {:03d}'.format(str_date, number))
				if Buy.objects.filter(slug=slug).exists():
					number+=1
				else:
					self.slug = slug
					break
		return super(Buy, self).save(*args, **kwargs)

	@property
	def description(self):
		first_item = self.buyitem_set.first()
		count = self.buyitem_set.count()
		return '{} 등 {}건'.format(first_item.drug, count) if first_item else '내역 없음'

	def get_total_price(self):
		ret = 0
		for item in self.buyitem_set.all():
			ret += item.get_buy_price()
		return ret

	@property
	def complete_late(self):
		items = self.buyitem_set.filter(end=False)
		nCompletes = len([item for item in items if item.is_completed])
		nTotal = items.count()
		if nTotal:
			return '{:2.0%}'.format(nCompletes/nTotal)
		else:
			return '-'


class BuyItemManager(models.Manager):
	def filter_by_date(self, *args):
		start_date, end_date = args
		return  BuyItem.objects.filter(buy__date__range=args)


class BuyItem(models.Model):
	drug = models.ForeignKey(Info, verbose_name='구매약품')
	buy = models.ForeignKey(Buy, verbose_name='발주번호', null=True, blank=True)
	amount = models.PositiveIntegerField('구매수량', help_text='위아래 방향키로 수량 조절')
	end = models.BooleanField('마감여부', default=False)
	comment = models.CharField('비고', max_length=50, blank=True)
	# status = models.IntegerField('구매상태',  choices=[(1,'발주대기'),(2,'발주'),(3,'마감')], default=1)
	create_date = models.DateField('입력일자', auto_now_add=True)
	modify_date = models.DateField('변경일자', auto_now=True)
	by = models.ForeignKey(User, verbose_name='구매자', default=1)

	objects = BuyItemManager()
	class Meta:
		verbose_name='구매품목'
		verbose_name_plural='구매품목'

	def __str__(self):
		return self.drug.name
		
	@property
	def incomplete_amount(self):
		if self.end == False:
			stockin = self.stockrec_set.aggregate(Sum('amount'))['amount__sum'] or 0
			return self.amount - stockin
		else:
			return 0

	@property
	def stockin_amount(self):
		return self.stockrec_set.aggregate(Sum('amount'))['amount__sum'] or 0

	@property
	def is_completed(self):
		return self.incomplete_amount == 0

	@property
	def is_over_stockin(self):
		return self.incomplete_amount < 0
	
	def get_nowbuying(self):
		return BuyItem.objects.filter(buy__isnull=True)

	def get_buy_price(self):
		return self.amount * self.drug.price

	@property
	def complete_amount(self):
		stockin = self.stockrec_set.aggregate(Sum('amount'))['amount__sum'] or 0
		return stockin

	@property
	def end_amount(self):
		if self.end:
			stockin = self.stockrec_set.aggregate(Sum('amount'))['amount__sum'] or 0
			return self.amount - stockin
		else:
			return 0






