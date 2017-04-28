from django.db import models
from django.db.models import Sum, Max, Q, Min
from django.contrib.auth.models import User
from datetime import date, timedelta

# Create your models here.


class Account(models.Model):
	name = models.CharField('도매상명', unique=True, max_length=50)
	tel = models.CharField('전화', max_length=50, null=True)
	fax = models.CharField('팩스', max_length=50, null=True, blank=True)
	email = models.EmailField('담당자 E-mail', null=True, blank=True)
	address = models.CharField('위치', max_length=100, null=True, blank=True)

	class Meta:
		verbose_name='도매상'
		verbose_name_plural='도매상'

	def __str__(self):
		return self.name


status_choices = [('폐기','폐기'),('사용중','사용중'),('생성대기','생성대기')]
etc_class_choices = [('일반','일반'),('처치약품','처치약품'),('항암제','항암제'),('직송','직송'),('수액','수액'),('영양수액','영양수액'),('인슐린주사','인슐린주사'),('백신','백신'),('조영제','조영제'),('마약','마약'),('향정','향정'),('소모품', '소모품')]
narcotic_class_choices = [(0,'일반'),(1,'마약'),(2,'향정')]
standard_unit_choices = [('VIAL','VIAL'),('BTL','BTL'),('AMP','AMP'),('SYR','SYR'),('TAB','TAB'),('CAP','CAP'),('PACK','PACK'),('KIT','KIT'),('VIAL','VIAL'),('BAG','BAG'),('PEN','PEN'),('매','매'),('TUBE','TUBE'),('EA','EA'),('포','포'),('BOX','BOX')]
invest_class_choices = [('경구', '경구'), ('주사', '주사'), ('외용', '외용'), ('냉장', '냉장'), ('마약류', '마약류'), ('해당없음', '해당없음')]


class InfoManager(models.Manager):
	def weekly_predict_set(self):
		queryset = Info.objects.all()
		return (inst for inst in queryset if inst.predict_weekly)
		

class Info(models.Model):

	def __str__(self):
		return self.name

	objects = InfoManager()

	class Meta:
		verbose_name='약품정보'
		verbose_name_plural='약품정보'
		ordering = ['name_as']

	edi = models.IntegerField('EDI 코드', primary_key=True)
	name = models.CharField('약품명', max_length=100)
	name_as = models.CharField('약품거래명', max_length=100, null=True)
	code = models.CharField('약품코드', max_length=20, null=True, editable=False)
	firm = models.CharField('제약회사명', max_length=50, null=True)
	price = models.PositiveIntegerField('단가', default=0)
	pkg_amount = models.PositiveIntegerField('포장수량', default=1, blank=True)
	purchase_standard = models.CharField('구매규격', max_length=50, null=True, blank=True)
	standard_unit = models.CharField('규격단위', choices=standard_unit_choices, max_length=50, null=True)
	narcotic_class = models.IntegerField('마약류구분', choices=narcotic_class_choices, default=0)
	account = models.ForeignKey(Account, null=True, default=1, verbose_name='도매상')
	base_amount = models.IntegerField('기초재고', default=0)
	create_date = models.DateTimeField('생성시간', auto_now_add=True)
	modify_date = models.DateTimeField('수정시간', auto_now=True)
	by = models.ForeignKey(User, default=1, verbose_name='정보생성인')
	status = models.CharField('현재상태', max_length=10, choices=status_choices, default='사용중')
	etc_class = models.CharField('기타구분', max_length=10, choices=etc_class_choices, default='일반')
	invest_class = models.CharField('재고분류', choices=invest_class_choices, max_length=10, default='해당없음')
	


	@property
	def current_stock(self):
		dynamic_amount = self.stockrec_set.filter(frozen=False).aggregate(Sum('amount'))['amount__sum'] or 0
		return dynamic_amount + self.base_amount

	@property
	def total_incomplete_amount(self):
		incomplete = 0
		for item in self.buyitem_set.filter(buy__isnull=False, buy__commiter__isnull=False):
			incomplete += item.incomplete_amount
		return incomplete

	@property
	def total_incomplete_amount_all(self):
		incomplete = 0
		for item in self.buyitem_set.all():
			incomplete += item.incomplete_amount
		return incomplete

	@property
	def total_stockin_amount(self):
		return self.stockrec_set.aggregate(Sum('amount'))['amount__sum'] or 0


	@property
	def last_stockin_date(self):
		return self.stockrec_set.aggregate(Max('date'))['date__max']

	@property
	def first_stockin_date(self):
		if self.stockrec_set.exists():
			return self.stockrec_set.aggregate(Min('date'))['date__min']
		return 0

	@property
	def last_stockin_amount(self):
		if self.stockrec_set.exists():
			return self.stockrec_set.values('amount').annotate(Max('date')).first()['amount']
		return 0



	@property
	def predict_weekly(self):
		incomplete = self.total_incomplete_amount_all
		
		if incomplete:
			last_date =  date.today()
		else:
			last_date = self.last_stockin_date

		if not last_date:
			return 0

		if self.first_stockin_date and self.first_stockin_date > date.today() - timedelta(30):
			return 0
		
		stock_amount = self.stockrec_set.filter(date__range=[last_date-timedelta(7), last_date]).aggregate(Sum('amount'))['amount__sum'] or 0	

		nWeek_elapsed = (date.today() - last_date).days // 7
		weekly_avg = self.weekly_avg_stockin
			
		if (incomplete + stock_amount - nWeek_elapsed*weekly_avg) < weekly_avg /2:
			return (weekly_avg // self.pkg_amount) * self.pkg_amount or self.pkg_amount
		return 0




	@property
	def monthly_avg_stockin(self):
		first_stockin_date = self.first_stockin_date
		cur_date = date.today()
		period = round((cur_date-first_stockin_date).days/30) or 1
		total_stockin_amount = self.total_stockin_amount
		return (total_stockin_amount//period)

	@property
	def weekly_avg_stockin(self):
		first_stockin_date = self.first_stockin_date
		if not first_stockin_date:
			return 0
		cur_date = date.today()
		period = round((cur_date-first_stockin_date).days/7) or 1
		total_stockin_amount = self.total_stockin_amount
		return (total_stockin_amount//period)
