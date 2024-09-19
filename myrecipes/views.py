from django.shortcuts import render
from .models import Recipe, Rating, Comment, UserProfile
from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Define views for the application

def home(request):
    """Render the home page with the latest 4 recipes"""
    queryset = Recipe.objects.all()[:4]
    context = {'recipes': queryset}
    return render(request, "index.html", context)

@login_required
def add_recipe(request):
    """Handle the addition of a new recipe"""
    if request.method == 'POST':
        data = request.POST
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')
        recipe_ingredients = data.get('recipe_ingredients')
        instructions = data.get('instructions')
        cooking_time = data.get('cooking_time')
        recipe_image = request.FILES.get('recipe_image')

        Recipe.objects.create(
            user=request.user,
            recipe_image=recipe_image,
            recipe_name=recipe_name,
            recipe_ingredients=recipe_ingredients,
            recipe_description=recipe_description,
            instructions=instructions,
            cooking_time=cooking_time,
        )
        return redirect('/addrecipe')
    return render(request, "addrecipe.html")

def viewrecipe(request):
    """Render the page with all recipes, ordered by creation date"""
    queryset = Recipe.objects.order_by('-created_at')
    context = {'recipes': queryset}
    return render(request, "view.html", context)

@login_required
def delete_recipe(request, id):
    """Handle the deletion of a specific recipe"""
    queryset = Recipe.objects.get(id=id)
    queryset.delete()
    return redirect('/viewrecipe')

@login_required  
def update_recipe(request, id):
    """Handle the update of a specific recipe"""
    queryset = Recipe.objects.get(id=id)
    if request.method == 'POST':
        data = request.POST
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')
        recipe_ingredients = data.get('recipe_ingredients')
        instructions = data.get('instructions')
        cooking_time = data.get('cooking_time')
        recipe_image = request.FILES.get('recipe_image')

        queryset.recipe_name = recipe_name
        queryset.recipe_description = recipe_description
        queryset.recipe_ingredients = recipe_ingredients
        queryset.instructions = instructions
        queryset.cooking_time = cooking_time

        if recipe_image:
            queryset.recipe_image = recipe_image

        queryset.save()
        return redirect('/viewrecipe/')
    context = {'recipe': queryset}
    return render(request, "update_recipe.html", context)

def recipe_detail(request, id):
    """Render detailed view of a specific recipe, including ratings and comments"""
    queryset = Recipe.objects.get(id=id)
    ingredients = queryset.recipe_ingredients.split('\n')
    instructions = queryset.instructions.split('.')

    if request.method == 'POST':
        if request.user.is_authenticated:
            # Handle rating
            score = request.POST.get('score')
            existing_rating = Rating.objects.filter(user=request.user, recipe_name=queryset).first()
            if score is not None:
                if existing_rating is not None:
                    # Update existing rating
                    score = int(score)
                    existing_rating.score = score
                    existing_rating.save()
                else:
                    score = int(score)
                    rating = Rating(user=request.user, recipe_name=queryset, score=score)
                    rating.save()
            # Handle comment
            content = request.POST.get('content')
            if content:
                comment = Comment(user=request.user, recipe_name=queryset, content=content)
                comment.save()
        else:
            messages.error(request, 'Please login to rate or comment')
        return redirect("recipe_detail", id=id)
    
    comments = Comment.objects.filter(recipe_name=queryset).order_by('-created_at')
    average_rating = Rating.objects.filter(recipe_name=queryset).aggregate(Avg('score'))['score__avg']
    context = {'recipes': queryset,
               'ingredients': ingredients,
               'instructions': instructions,
               'average_rating': average_rating,
               'comments': comments}
    
    return render(request, "recipedetail.html", context)

def login_page(request):
    """Render the login page and handle user authentication"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid username')
            return redirect('/login_page')
        
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid password')
            return redirect('/login_page/')
        else:
            login(request, user)
            return redirect('/viewrecipe/')
        
    return render(request, "login_page.html")

def register(request):
    """Render the registration page and handle new user creation"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)
        if user.exists():
            messages.info(request, 'Username already exists')
            return redirect('/register')
        user = User.objects.create(first_name=first_name,
                                   last_name=last_name,
                                   email=email,
                                   username=username)
        user.set_password(password)
        user.save()
        messages.success(request, 'Account created successfully')
        return redirect('/register/')
    
    return render(request, "register.html")

@login_required
def log_out(request):
    """Handle user logout and redirect to login page"""
    logout(request)
    return redirect('/login_page')

def search(request):
    """Render the search page and filter recipes based on search query"""
    queryset = Recipe.objects.order_by('-created_at')
    if request.GET.get('search'):
        queryset = queryset.filter(recipe_name__icontains=request.GET.get('search'))
    context = {'recipes': queryset}
    return render(request, "search.html", context)

@login_required
def profile(request, id):
    """Render the profile page for a specific user"""
    try:
        queryset = User.objects.get(id=id)
        user_recipes = Recipe.objects.filter(user=queryset)
        recipe_count = user_recipes.count()
        recipe = Recipe.objects.filter(user=queryset)
        userdetails = UserProfile.objects.get(user=queryset)
        context = {'user': queryset, 'recipes': recipe, 'userdetails': userdetails, 'recipe_count': recipe_count}
        return render(request, "profile.html", context)
    except UserProfile.DoesNotExist:
        return redirect("/create_profile/")
    
def create_profile(request):
    """Render the create profile page and handle profile creation"""
    queryset = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        bio = request.POST.get('bio')
        dob = request.POST.get('dob')
        profile_pic = request.FILES.get('profile_pic')
        profile = UserProfile.objects.create(user=queryset,
                                             profile_pic=profile_pic,
                                             bio=bio,
                                             dob=dob)
        messages.success(request, 'Profile created successfully')
        profile.save()
        return redirect('profile', id=request.user.id)
    return render(request, "create_profile.html")

def update_profile(request, id):
    """Render the update profile page and handle profile updates"""
    queryset = UserProfile.objects.get(id=id)
    if request.method == 'POST':
        data = request.POST
        bio = data.get('bio')
        dob = data.get('dob')
        profile_pic = request.FILES.get('profile_pic')
        queryset.dob = dob
        queryset.bio = bio
        if profile_pic:
            queryset.profile_pic = profile_pic
        queryset.save()
        return redirect('profile', id=request.user.id)
    context = {'userprofile': queryset}
    return render(request, "update_profile.html", context)
