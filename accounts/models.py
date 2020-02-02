# Python Tools
import uuid
import math
from datetime import timedelta

# Django  Tools
from django.db import models
from django.utils.timezone import localdate
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager ## A new class is imported. ##




def calculateAge(birthDate):
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) <
         (birthDate.month, birthDate.day))

    return age

def filename(instance, filename):
    return f'{instance.user.email.split("@")[0]}_profile{datetime.now().second}'




class Profile(SafeDeleteModel):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    GENDERS = (
        ("M", "Hombre"),
        ("F", "Mujer"),
        ("U", "No definido")
        )
    gender = models.CharField(default="U", choices=GENDERS, max_length=2, null=True, blank=True)
    abstract = models.TextField(blank=True, default="")
    birth_date = models.DateField(null=True, blank=True)
    nacionality = models.CharField(max_length=120, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)




    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f'{self.user}'



    @property
    def completed(self):
        if (self.gender is not None and
                self.birth_date is not None and
                self.phone is not None and
                self.nacionality is not None):
            return True
        return False

    @property
    def age(self):
        return self.age_in()

    def age_in(self, event=None):
        refdate = event if event is not None else localdate()
        if self.birth_date == None:
            return None
        age =  math.floor( (refdate-self.birth_date).days/365.25)
        if age < 1:
            return None
        return age


class User( AbstractUser):
    """User model."""
    _safedelete_policy = SOFT_DELETE

    ROLES = (
        (0, "Administrador"),
        (1, "Profesor"),
        (2, "Representante"),
        (3, "Estudiante")
        )

    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ( {self.email})'
    
  