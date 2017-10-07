from django.db import models
from django.dispatch import receiver
import os, datetime

from .utils import get_item_count
from utils.mixins import DeleteWithFileMixin

# OCS Mastr 백업 파일 관리 앱
UPLOAD_DIR = 'ocsxl'

from pprint import pprint


# DB Instance 삭제시 파일도 같이 삭제
class OcsFileManager(DeleteWithFileMixin, models.Manager): pass



class OcsFile(models.Model):
    excel = models.FileField(upload_to=UPLOAD_DIR)
    description = models.CharField('요약', max_length=100, blank=True, null=True)
    created = models.DateTimeField('생성일시', auto_now_add=True)
    updated = models.DateTimeField('수정일시', auto_now=True)

    objects = OcsFileManager()

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'OCS마스터파일관리'
        verbose_name_plural = 'OCS마스터파일관리'
        ordering = '-created',

    @property
    def filename(self):
        path = self.excel.name
        return os.path.basename(path)











