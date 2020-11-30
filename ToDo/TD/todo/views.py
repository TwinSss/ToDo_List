import datetime
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Todo, Client
from .forms import TodoForm, CreateUserForm
from .decorators import unauthenticated_user, allowed_users, admin_only


#@admin_only
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'client'])
def index(request):

    todo_list = Todo.objects.filter(client_id=Client.objects.get(name=request.user))
    form = TodoForm()
    date_created = datetime.datetime.now()

    context = {'todo_list': todo_list, 'form': form, 'date_created': date_created }

    return render(request, 'todo/index.html', context)


@require_POST
@allowed_users(allowed_roles=['admin', 'client'])
def addTodo(request):

    form = TodoForm(request.POST)
    if form.is_valid():
       new_todo = Todo(text=request.POST['text'],make_up=request.POST['make_up'], client=Client.objects.get(name=request.user))
       new_todo.save()

    return redirect('index')


@allowed_users(allowed_roles=['admin', 'client'])
def completeTodo(request, todo_id):

    todo = Todo.objects.get(pk=todo_id)
    todo.complete = True
    todo.save()

    return redirect('index')


@allowed_users(allowed_roles=['admin', 'client'])
def dateComplete(request):
    
    todo = Todo.objects.filter(client_id=Client.objects.get(name=request.user))
    for i in todo:
        if datetime.date.today() >= i.make_up:
            i.date_completed = True
            i.save()

    return redirect('index')    


@allowed_users(allowed_roles=['admin', 'client'])
def deleteCompleted(request):

    Todo.objects.filter(complete__exact=True).delete()

    return redirect('index')


@allowed_users(allowed_roles=['admin', 'client'])
def deleteAll(request):

    Todo.objects.all().delete()

    return redirect('index')


@unauthenticated_user
def registerPage(request):
   
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='client')
            user.groups.add(group)
            Client.objects.create(
                user=user,
				name=user.username,)

            messages.success(request, 'Account was created for' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'todo/register.html', context)


@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request,'Username OR password is incorrect')  

    context = {}
    return render(request, 'todo/login.html', context)


def logoutUser(request):

    logout(request)
    return redirect('login')


@allowed_users(allowed_roles=['admin','client'])
def client(request):

    client = Client.objects.get(name=request.user)
    clients = Client.objects.all()
    todos = Todo.objects.all()

    total_clients = clients.count()
    total_todos = todos.filter(client_id=Client.objects.get(name=request.user)).count() 

    context = {'total_clients': total_clients, 'client': client, 'total_todos': total_todos}
    return render(request, 'todo/client.html', context)


