from django.db import models


# kind_choice_set = ('nut_fluid', '영양수액'), ('label', '라벨'), 




# def handle_upload(instance, filename):
#     return "collect/{}".format(instance.title)


# class CollectManager(models.Manager):

#     def create_today(self, types, kind):
#         from datetime import datetime, date
#         today = date.today()
        
#         pass

# class Collect(models.Model):

#     class Meta:
#         verbose_name = "집계"
#         verbose_name_plural = "집계"
#         ordering = '-created',

#     title = models.CharField('집계이름', max_length=50, blank=True, null=True)
#     kind = models.CharField('종류', max_length=10, choices=kind_choice_set, blank=True, null=True)
#     types = models.CharField('구분', max_length=50, default='정기,')
#     seq = models.IntegerField('차시', default=0)
#     file = models.FileField('집계파일', upload_to=handle_upload, blank=True, null=True)
#     date = models.DateField('집계일자', auto_now_add=True)
#     date_start = models.DateField(blank=True, null=True)
#     date_end = models.DateField(blank=True, null=True)

#     updated = models.DateTimeField('수정일시', auto_now=True)
#     created = models.DateTimeField('생성일시', auto_now_add=True)

#     def __str__(self):
#         return self.title
    
#     def save(self, **kwargs):
#         super(Collect, self).save(**kwargs)

