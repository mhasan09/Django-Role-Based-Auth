from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from .models import Post


@login_required(login_url='/login')
def home(request):
    POSTS = Post.objects.all()
    if request.method == 'POST':
        post_id = request.POST.get('post-id')
        print(post_id)
        post = Post.objects.filter(id=post_id).first()
        if post and (post.author == request.user or request.user.has_perm('Authenticate.delete_post')):
            post.delete()
    return render(request, 'Pages/home.html', {'posts': POSTS})


@login_required(login_url='/login')
@permission_required('Authentication.add_post',login_url='/login', raise_exception=True)
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            print("POST CREATED ___________")
            return redirect('/home')
    else:
        form = PostForm()
    return render(request, 'Pages/create_post.html', {'form': form})


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'Registration/sign_up.html', {'form': form})
