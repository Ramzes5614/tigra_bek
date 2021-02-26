from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager

class AccountManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, phone_number, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not phone_number:
            raise ValueError('The given phone must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)


class Account(AbstractUser):
    username = None
    email = None

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=False,unique=True,verbose_name='Телефон')
    objects = AccountManager()

class Profile(models.Model):
    account = models.OneToOneField(Account,on_delete=models.CASCADE,verbose_name='Аккаунт')
    visit_counter = models.IntegerField(default=0,blank=False,verbose_name='Количество посещений')
    child_name = models.CharField(blank=True,max_length=40,verbose_name="Имя ребенка")
    class Meta:
        verbose_name='Профиль'
        verbose_name_plural = 'Профили'
    def __str__(self):
        return (f"{self.account.first_name} {self.account.last_name} {self.child_name} {self.account.phone_number} {self.visit_counter}")

class TigraAdmin(models.Model):
    username = models.CharField(max_length=40,verbose_name="Имя пользователя", unique=True)
    password = models.CharField(max_length=40,verbose_name="Пароль")
    class Meta:
        verbose_name='Тигра Админ'
        verbose_name_plural='Тигра Админы'
    def __str__(self):
        return (f"{self.username} {self.password}")
