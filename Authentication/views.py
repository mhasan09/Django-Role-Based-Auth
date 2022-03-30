from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from .models import Post
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType


@login_required(login_url='/login')
def home(request):
    #getting all the post objects
    POSTS = Post.objects.all()
    if request.method == 'POST':

        post_id = request.POST.get('post-id')
        user_id = request.POST.get('user-id')

        if post_id:
            print(post_id)
            post = Post.objects.filter(id=post_id).first()
            #deleting a post by the author or by the superUser
            if post and (post.author == request.user or request.user.has_perm('Authenticate.delete_post')):
                post.delete()
        elif user_id:
            user = User.objects.filter(id=user_id).first()
            if user and request.user.is_staff:
                try:
                    #banning a user from the default group which doesn't allow user to post anything
                    group = Group.objects.get(name='default')
                    group.user_set.remove(user)
                except:
                    pass
                try:
                    # banning a user from the moderator group
                    group = Group.objects.get(name='mod')
                    group.user_set.remove(user)
                except:
                    pass

    return render(request, 'Pages/home.html', {'posts': POSTS})


@login_required(login_url='/login')
@permission_required('Authentication.add_post', login_url='/login', raise_exception=True)
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


def change_permission(request):
    # creating a moderator
    mod = Group.objects.get_or_create(name="mod")
    # get the contentType
    ct = ContentType.objects.get_for_model(model=Post)
    # get the permissions
    perms = Permission.objects.filter(content_type=ct)
    # adding the permissions
    mod.permissions.add(*perms)
    # then get a user
    user = User.objects.filter(username="samiha")
    # setting up the user as a moderator
    mod.user_set.add(user.first())
