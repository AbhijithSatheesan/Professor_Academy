from django.db import models


# Create your models here.



class Colleges(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    parent_subcategories = models.ManyToManyField('Subcategory', blank=True)  # Changed to ManyToManyField
    courses = models.CharField(max_length=400, null=True, blank=True)
    location = models.CharField(max_length= 25, null= True, blank= True)
    priority = models.IntegerField(blank=True, null=True, default=1)
    main_image = models.ImageField(null=True, blank=True)
    hostel_image = models.ImageField(null=True, blank=True)
    library_image = models.ImageField(null=True, blank=True)
    class_image = models.ImageField(null=True, blank=True)
    lab_image = models.ImageField(null=True, blank=True)
   

    def __str__(self):
        return self.name
    
class OtherImage(models.Model):
    college = models.ForeignKey(Colleges, related_name='other_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='college_images/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.college.name}"
    

class Category(models.Model):
    name= models.CharField(max_length= 100, unique= True)
    image = models.ImageField(blank= True, null= True)
    priority = models.IntegerField(default= 1)

    def __str__(self):
        return self.name



class Subcategory(models.Model):
    parent_category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank= True)
    name = models.CharField(max_length= 100)
    image = models.ImageField(null= True, blank= True)
    priority = models.IntegerField(default= 1)

    def __str__(self):
        return self.name



