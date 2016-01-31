from django.shortcuts import render
from django.http import JsonResponse

from .models import CustomUser

# Create your views here.

def index(request):
	""" Create new user or return all users. """
	if not request.user.is_authenticated:
		return JsonError("Not logged in")
	if request.method == 'POST':
		# Validate request
		if request.user.is_authenticated() and not request.user.is_superuser:
			return JsonError('Already logged in.')
		# Create new user
		email = request.POST['email']
		password = request.POST['password']
		new_user = CustomUser.create(email, password)
		CustomUser.login(request, email, password)
		return JsonResponse(new_user.json)
	
	elif request.method == 'GET':
		# Validate request
		if not request.user.is_authenticated():
			return JsonError('Not logged in.')
		users = [ user.json for user in CustomUser.objects.all() ]
		return JsonResponse({'users': users})

def record(request, user_id):
	""" Read, Update, or Delete a user record """
	# Validate request
	if not request.user.is_authenticated():
		return JsonError('Not Logged In')
	if request.user.id != int(user_id) and not request.user.is_superuser:
		return JsonError('Unauthorized')
	
	# Process request
	if request.method == 'GET':
		return JsonResponse(request.user.json)
	elif request.method == 'PUT':
		for attr in request.user.mutable_attrs:
			if attr in request.PUT and hasattr(request.user, attr):
				value = request.PUT[attr]
				setattr(CustomUser, attr, value)
		request.user.save()
		return request.user
	elif request.method == 'DELETE':
		request.user.delete()
		return JsonResponse({'status': 200})

def login(request):
	""" Login a user based on provided credentials """
	if request.method != 'POST':
		return JsonError('Login request method must be POST')
	if not request.user.is_anonymous():
		return JsonError('Already Logged in.')
	email = request.POST['email']
	password = request.POST['password']
	user = CustomUser.login(request, email, password)
	return JsonResponse(user.json)

def logout(request):
	""" Logout current user and delete associated session """
	if request.user.is_anonymous():
		return JsonError("Not logged in")
	CustomUser.logout(request)
	return JsonResponse({'status': 200})

def current(request):
	""" Return current user """
	if request.user.is_anonymous():
		return JsonError('Not logged in.')
	return JsonResponse(request.user.json)

def JsonError(msg):
	""" Shortcut wrapper for returning error message """
	return JsonResponse({'error': msg})