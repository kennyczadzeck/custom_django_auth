import datetime
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as _logout

from django.db import models
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser, PermissionsMixin
)

# Create your models here.

class CustomUserManager(BaseUserManager):
	def _create_user(self, email, password, is_staff, is_superuser, **kwargs):
		""" Creates and saves a User with the given email and password. """
		now = timezone.now()
		if not email:
			raise ValueError("Users must have an email address")

		email = self.normalize_email(email)
		user = self.model(email=email, is_staff=is_staff, is_active=True, 
						is_superuser=is_superuser, last_login=now, 
						date_joined=now, **kwargs
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **kwargs):
		return self._create_user(email, password, False, False, **kwargs)

	def create_superuser(self, email, password, **kwargs):
		""" Creates and saves a superuser with the given email and password """
		return self._create_user(email, password, True, True, **kwargs)


class CustomUser(AbstractBaseUser, PermissionsMixin):
	""" Custom User model which forgoes username for email address """
	email = models.EmailField(_('email_address'), max_length=254, unique=True)
	first_name = models.CharField(_('first name'), max_length=30, blank=True)
	last_name = models.CharField(_('last name'), max_length=30, blank=True)
	date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
	is_staff = models.BooleanField(_('staff status'), default=False,
		help_text=('Designates whether the user can log into this admin site.'))
	is_active = models.BooleanField(_('is active'), default=True,
		help_text=_('Designates whether this user should be treated as '
					'active. Unselect this instead of deleting accounts.'))

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = CustomUserManager()

	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')

	def __unicode__(self):
		return self.email

	def get_absolute_url(self):
		return "/users/{0}/".format(urlquote(self.email))

	def get_full_name(self):
		full_name = '{0} {1}'.format(self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		return self.first_name

	@property
	def mutable_attrs(self):
	    return ('email', 'password', 'first_name', 'last_name')

	@property
	def json(self):
		""" serialize a CustomUser object into json """
		return {
			'email': self.email,
			'id': str(self.id),
			'first_name': self.first_name,
			'last_name': self.last_name,
			'date_joined': self.date_joined,
			'last_login': self.last_login
		}

	def update(self, attr, value):
		if hasattr(self, attr):
			setattr(self, attr, value)
		else:
			_class = self.__class__
			attr_err = '{0} has no attribute, {1}'.format(_class, value)
			raise AttributeError(attr_err)
		return self

	@classmethod
	def create(cls, email, password, is_super=False):
		user = cls(email=email)
		if is_super:
			user.is_staff = True
			user.is_superuser = True
		user.set_password(password)
		user.save()
		return user

	@classmethod
	def login(cls, request, email, password):
		user = authenticate(email=email, password=password)
		if user and user.is_active:
			login(request, user)
			user.last_login = timezone.now()
			user.save()
		return user

	@staticmethod
	def logout(request):
		_logout(request)

