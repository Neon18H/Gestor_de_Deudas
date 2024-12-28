from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Task
from django.http import JsonResponse
from .models import User
from django.contrib.auth.decorators import login_required, user_passes_test



from .forms import TaskForm

# Create your views here.


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:

        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {"form": UserCreationForm, "error": "Username already exists."})

        return render(request, 'signup.html', {"form": UserCreationForm, "error": "Passwords did not match."})


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {"tasks": tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {"tasks": tasks})


@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, 'create_task.html', {"form": TaskForm})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {"form": TaskForm, "error": "Error creating task."})


def home(request):
    return render(request, 'home.html')



@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})

        login(request, user)
        return redirect('home')

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task.'})
#######
def is_superuser(user):
    return user.is_superuser
######
@login_required
@user_passes_test(is_superuser)
def complete_task(request, task_id):
    # Obtener la tarea
    task = get_object_or_404(Task, pk=task_id)

    # Si es una solicitud POST, marcar la tarea como completada
    if request.method == 'POST':
        task.datecompleted = timezone.now()  # Establecer la fecha de completado
        task.save()  # Guardar los cambios en la base de datos
        return redirect('assign_task_to_user')  # Redirigir a la vista de tareas asignadas

    # Si es GET, mostrar la página de confirmación
    return render(request, 'confirm_complete_task.html', {'task': task})


#####
@login_required
@user_passes_test(is_superuser)
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)  # Obtener la tarea con el ID

    if request.method == 'POST':  # Si es una solicitud POST, eliminar la tarea
        task.delete()
        return redirect('assign_task_to_user')  # Redirigir a la vista de asignar tareas

    # Si es una solicitud GET, mostrar una confirmación
    return render(request, 'confirm_delete_task.html', {'task': task})



@login_required
@user_passes_test(is_superuser)  # Asegura que solo los superusuarios accedan a esta vista
def assign_task_to_user(request):
    if request.method == 'GET':
        # Obtener todos los usuarios registrados
        users = User.objects.all()

        # Obtener todas las tareas, sin importar el usuario
        tasks = Task.objects.all()  # Todos los usuarios, todas las tareas

        form = TaskForm()

        return render(request, 'assign_task.html', {
            'users': users,
            'form': form,
            'tasks': tasks,  # Agregar las tareas a la plantilla
        })

    elif request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            new_task = form.save(commit=False)
            selected_user = User.objects.get(id=request.POST['user_id'])
            new_task.user = selected_user
            new_task.save()

            return redirect('assign_task_to_user')

        return render(request, 'assign_task.html', {
            'form': form,
            'error': 'Error al asignar la tarea.',
            'users': User.objects.all()
        })
        ###
from .forms import PreguntaForm

@login_required
def enviar_pregunta(request):
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.usuario = request.user  # Asignar el usuario que hace la pregunta
            pregunta.save()
            return redirect('home')  # Redirigir a una página donde se vean las preguntas
    else:
        form = PreguntaForm()

    return render(request, 'enviar_pregunta.html', {'form': form})

# views.py

from django.contrib.admin.views.decorators import staff_member_required
from .models import Pregunta
# views.py

from django.shortcuts import render
from .models import Pregunta

def ver_preguntas(request):
    preguntas = Pregunta.objects.all()  # Obtener todas las preguntas
    return render(request, 'ver_preguntas.html', {'preguntas': preguntas})

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            # Redirige a donde desees después de guardar
            return redirect('tasks')  # Por ejemplo, volver a la lista de tareas
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'task_detail.html', {'task': task, 'form': form})