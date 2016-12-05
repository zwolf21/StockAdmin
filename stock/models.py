from django.db import models
from django.db.models import Sum, Max, Q
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User



# Create your models here.
from info.models import Info
from buy.models import Buy, BuyItem





class StockRec(models.Model):

	buyitem = models.ForeignKey(BuyItem, verbose_name='구매품목', null=True, blank=True)
	drug = models.ForeignKey(Info, verbose_name='약품명', blank=True)
	amount = models.PositiveIntegerField('수량')
	date = models.DateField('발생일자')
	frozen = models.BooleanField('재고마감여부', default=False)
	inout = models.IntegerField('구분', choices=[(1,'구매입고'),(2,'불출')], default=1)

	class Meta:
		verbose_name='입출고 기록'
		verbose_name_plural='입출고 기록'
		ordering = ['-date']

	def __str__(self):
		return self.drug.name

	def save(self, *args, **kwargs):
		if self.buyitem and self.buyitem.stockin_amount+self.amount > self.buyitem.amount:
			return

		if not self.id:
			if self.buyitem:
				self.drug = self.buyitem.drug
		
		return super(StockRec, self).save(*args, **kwargs)
	@property
	def total_price(self):
		return self.amount * self.drug.price

	




def post_delete_stockrec(sender, instance, *args, **kwargs):
	if instance.frozen == True:
		instance.drug.base_amount -= instance.amount
		instance.save()

post_delete.connect(post_delete_stockrec, sender=StockRec)



