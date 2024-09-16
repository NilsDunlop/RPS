from datetime import date
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Game, User, Image, DeepModel
from .forms import CreateUserForm
import json
import base64
import random
import string
import numpy as np
from PIL import Image as aiImage
from keras.models import load_model


# Create your views here.
def home(request):
    return render(request, 'rps/home.html')


@csrf_exempt
def player(request):
    """Retrieve user image, save it to database and pass it to AI model"""
    prediction = ''
    if request.method == "POST":
        data = request.body
        data = json.loads(data[0:len(data)])
        temp = len('data:image/jpeg;base64,')
        for d in data:
            d = d[temp:len(d)]
            imgdata = base64.b64decode(d)
            filename = random_string() + '.jpg'
            with open('media/' + filename, 'wb') as f:
                f.write(imgdata)
            prediction = guess_gesture('media/' + filename)
            i = Image.objects.create(file=filename, predict=prediction)
            i.save()
        return JsonResponse({'result': prediction})
    # retrieve score and call function to update the registered users score
    score = request.GET.get('score', None)
    update_score(request, score)
    return render(request, 'rps/player.html')


def random_string(string_length=5):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def guess_gesture(user_gesture_image):
    """Pass user image into AI model to predict gesture"""
    result = ""
    im = aiImage.open(user_gesture_image)
    new_size = (150, 150)
    im = im.resize(new_size)
    # filter deepmodels check is there is an object which current attribute set to true
    find_deepmodel = DeepModel.objects.filter(current=True)
    if find_deepmodel.exists():
        # get the object if it exists
        current_deep_model = DeepModel.objects.get(current=True)
        # assign filename with the current deep models name
        filename = current_deep_model.name
        # set the path with the filename
        path = './media/uploaded_models/' + filename
    else:
        path = './fin_model.h5'  # model to be used if there isn't an uploaded model that is current
    image_as_array = np.expand_dims(im, axis=0)
    loaded_model = load_model(path)  # load the model
    predict = loaded_model.predict(image_as_array)

    if predict[0][0] == 1:
        result = "✋"
    elif predict[0][1] == 1:
        result = "👊"
    elif predict[0][2] == 1:
        result = "✌"
    return result


def register(request):
    # call the form to create users
    signup_form = CreateUserForm()
    # retrieve form values through http post request
    if request.method == 'POST':
        signup_form = CreateUserForm(request.POST)
        if signup_form.is_valid():  # check if it's valid
            # save user using form values and lower case the username string
            user = signup_form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, "Registration successful.")
        else:
            # reset the form if the form is not valid and show message to user
            messages.error(request, "Unsuccessful registration. Invalid information.")
            signup_form = CreateUserForm()
            # pass the form to the html view as context
    context = {'signup_form': signup_form}
    return render(request, 'rps/registration.html', context)


def login_request(request):
    # retrieve all game object and order by score in descending order. Show only the first 3
    games = Game.objects.all().order_by('-score').values()[:3]
    # retrieve all user objects
    users = User.objects.all()
    # retrieve form through http post request
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # check if the form is valid and authenticate user with password and username
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            # if user exists call login function and redirect to player view
            if user is not None:
                login(request, user)
                return redirect("player")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    # pass the form, games and users to the html view as context
    return render(request=request, template_name='rps/home.html',
                  context={"login_form": form, 'games': games, 'users': users})


def update_score(request, score):
    # execute below is the user is authenticated
    if request.user.is_authenticated:
        # check if there is a game object with the authenticated user
        game_user = Game.objects.filter(game_user_info_id=request.user.id)
        if game_user.exists():
            # if the game exists update date attribute with local date
            game_data = Game.objects.get(game_user_info_id=request.user.id)
            game_data.date = date.today()
            # if the score is 1 update score attribute by incrementing by 1
            if score == '1':
                game_data.score = int(game_data.score) + 1
                # elif decrement by 1
            elif score == '-1':
                game_data.score = int(game_data.score) - 1
                # else update the score with recent score
            else:
                game_data.score = int(game_data.score)
            game_data.save()
        else:
            # else create a new game with the logged-in user
            new_game_user = Game.objects.create(game_user_info_id=request.user.id)
            new_game_user.save()


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('login')
