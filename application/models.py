from django.db import models
from authentication.models import Login_model
from django.utils import timezone
class new_notes(models.Model):
    user_notes=models.ForeignKey(Login_model,on_delete=models.CASCADE)  
    date=models.DateField(default=timezone.now)
    note_title=models.CharField(max_length=255)
    note_description=models.CharField(max_length=400) 
    def __str__(self):
         return f"{self.note_title}"
# Create your models here.
class general_agent(models.Model):
    general_notes=models.ForeignKey(new_notes,on_delete=models.CASCADE)
    gen_info=models.CharField(max_length=255)
    def __str__(self):
         return f"{self.general_notes.note_title} - {self.gen_info[:30]}"
class Happy_agent(models.Model):
    general_notes=models.ForeignKey(new_notes,on_delete=models.CASCADE)
    hap_info=models.CharField(max_length=255)
    def __str__(self):
         return f"{self.general_notes.note_title} - {self.hap_info[:30]}"
class Hopeful_agent(models.Model):
    general_notes=models.ForeignKey(new_notes,on_delete=models.CASCADE)
    hop_info=models.CharField(max_length=255)
    def __str__(self):
         return f"{self.general_notes.note_title} - {self.hop_info[:30]}"
class Reflective_agent(models.Model):
    general_notes=models.ForeignKey(new_notes,on_delete=models.CASCADE)
    ref_info=models.CharField(max_length=255)
    def __str__(self):
         return f"{self.general_notes.note_title} - {self.ref_info[:30]}"
class motivation_agent(models.Model):
    general_notes=models.ForeignKey(new_notes,on_delete=models.CASCADE)
    mot_info=models.CharField(max_length=255)
    def __str__(self):
         return f"{self.general_notes.note_title} - {self.mot_info[:30]}"
class calm_agent(models.Model):
    general_notes=models.ForeignKey(new_notes,on_delete=models.CASCADE)
    calm_info=models.CharField(max_length=255)
    def __str__(self):
         return f"{self.general_notes.note_title} - {self.calm_info[:30]}"


class Dramatic_agent(models.Model):
    general_notes=models.ForeignKey(new_notes,on_delete=models.CASCADE)
    dram_info=models.CharField(max_length=255)
    def __str__(self):
         return f"{self.general_notes.note_title} - {self.dram_info[:30]}"
class Funny_agent(models.Model):
    general_notes=models.ForeignKey(new_notes,on_delete=models.CASCADE)
    fun_info=models.CharField(max_length=255)
    def __str__(self):
         return f"{self.general_notes.note_title} - {self.fun_info[:30]}"                       
