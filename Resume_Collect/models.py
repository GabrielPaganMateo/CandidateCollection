from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
import uuid
from .utils import *

# Create your models here.
class Opening(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.localtime)
    name = models.CharField(max_length=200, null=True)


    def __str__(self):
        return f'{self.name}'
    
    def create(self, name):
        return Opening.objects.create(name=name)

class Candidate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.localtime)
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    education = models.TextField(null=True, blank=True)
    experience = models.TextField(null=True, blank=True)
    text_list = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    opening = models.ForeignKey(Opening, null=True, blank=True, related_name='candidates', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/')

    

    def __str__(self):
        return f'{self.__class__.__name__}: {self.name} ({self.id}) created_at: {self.created_at}'