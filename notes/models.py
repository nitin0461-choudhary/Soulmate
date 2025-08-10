from django.db import models

# Create your models here.
from authentication.models import Login_model
from django.utils import timezone
class Note(models.Model):
    user=models.ForeignKey(Login_model,on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    content=models.TextField()
    created_at=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title