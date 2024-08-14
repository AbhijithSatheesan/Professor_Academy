from django.db import models
from django.contrib.auth.models import User,AbstractUser



# Create your models here.



class UserType(models.TextChoices):
    STUDENT = 'student', 'Student'
    STAFF = 'staff', 'Staff'
    ADMIN = 'admin', 'Admin'

class MyUsers(AbstractUser):
    email = models.EmailField(unique=True)
    image = models.ImageField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.STUDENT)

    def __str__(self):
        return self.username

class MarkedColleges(models.Model):
    student = models.ForeignKey(MyUsers, on_delete=models.CASCADE, null= True, blank= True, related_name= 'marked_colleges')
    marked_college= models.ForeignKey('colleges.Colleges', on_delete= models.CASCADE, null= True, blank= True)
    fee = models.IntegerField(null= True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.marked_college.name}"
    
    class Meta:
        unique_together = ('student', 'marked_college')
