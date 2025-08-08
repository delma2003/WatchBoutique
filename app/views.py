from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
# Create your views here.

def index(request):
   # return HttpResponse("Welcome")
   return render(request,"index.html")
# Create your views here.
def shop(request):
   return render(request,"shop.html")
def detail(request):
   return render(request,"detail.html")
def contact(request):
   return render(request,"contact.html")   
from django.shortcuts import render
from .models import Watch

from django.shortcuts import render
from .models import Watch
from django.db.models import Q

from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import Watch

from django.shortcuts import render
from django.db.models import Q
from django.utils.html import escape
import re
from django.db import connection
from .models import Watch  # Ensure Watch model is correctly imported

from django.shortcuts import render
from django.db.models import Q
from django.db import connection
import re
from .models import Watch

from django.shortcuts import render
from django.db.models import Q
from django.db import connection
import re
from .models import Watch

from django.shortcuts import render
from django.db.models import Q
from django.db import connection
import re
from functools import reduce

from .models import Watch  # Ensure Watch model is imported

from django.shortcuts import render
from django.db.models import Q
from django.db import connection
import re
from functools import reduce

from .models import Watch  # Ensure Watch model is imported

from django.shortcuts import render
from django.db.models import Q
from django.db import connection
import re
from functools import reduce

 # Ensure you import your model

import re
from functools import reduce
from django.db.models import Q
from django.shortcuts import render
from .models import Watch

# Define relevant attributes
RELEVANT_ATTRIBUTES = {
    "dial_color": ["black", "blue", "white", "gold", "silver"],
    "dial_shape": ["round", "square", "rectangle", "oval"],
    "movement": ["automatic", "quartz", "mechanical", "solar"],
    "model": ["sports", "classic", "luxury", "casual"],
    "strap_color": ["brown", "black", "gold", "silver"],
    "case_size": ["small", "medium", "large"],
    "price_range": {"under-10000": (0, 9999), "10000-25000": (10000, 25000), "25000-50000": (25000, 50000)}
}

def men(request):
    # Initialize variables
    search_query = request.GET.get('search', '').strip()
    filtered_keywords = []
    matched_filters = {}
    applied_filters = {}
    
    # Start with all men's watches or search results
    if search_query:
        # If there's a search query, start with search results
        watches = Watch.objects.filter(category="men")
        search_query = re.sub(r'[^\w\s]', '', search_query)  # Remove special characters
        search_keywords = search_query.lower().split()

        for word in search_keywords:
            match_found = False

            # Check against predefined attributes
            for attr, values in RELEVANT_ATTRIBUTES.items():
                if isinstance(values, list) and word in values:
                    watches = watches.filter(**{f"{attr}__icontains": word})
                    matched_filters[attr] = word
                    match_found = True
                    break
                elif isinstance(values, dict):  # Handle price ranges
                    for key, (min_price, max_price) in values.items():
                        if word in key:
                            watches = watches.filter(price__gte=min_price, price__lt=max_price)
                            matched_filters["price_range"] = key
                            match_found = True
                            break

            if not match_found:
                filtered_keywords.append(word)

        # If no matches found with predefined attributes, search in name and description
        if filtered_keywords:
            search_filter = reduce(
                lambda q, word: q & (Q(name__icontains=word) | Q(descriptions__title__icontains=word) | Q(descriptions__description__icontains=word)),
                filtered_keywords, Q()
            )
            watches = watches.filter(search_filter).distinct()
    else:
        # If no search, start with all men's watches
        watches = Watch.objects.filter(category="men")

    # Store the base queryset (either search results or all products)
    base_queryset = watches

    # Apply user-selected filters from URL parameters to the base queryset
    filter_params = {
        'model': request.GET.get('model'),
        'case_size': request.GET.get('case_size'),
        'dial_color': request.GET.get('dial_color'),
        'strap_color': request.GET.get('strap_color'),
        'dial_shape': request.GET.get('dial_shape'),
        'movement': request.GET.get('movement'),
        'price': request.GET.get('price'),
        'wrist_size': request.GET.get('wrist_size')  # Added wrist_size filter
    }

    for key, value in filter_params.items():
        if value:
            if key == 'price':
                if value in RELEVANT_ATTRIBUTES["price_range"]:
                    min_price, max_price = RELEVANT_ATTRIBUTES["price_range"][value]
                    watches = watches.filter(price__gte=min_price, price__lt=max_price)
                    applied_filters[key] = value
            else:
                watches = watches.filter(**{key: value})
                applied_filters[key] = value
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user)\
                                          .values_list('watch_id', flat=True)

    # Sorting logic - applied to the filtered queryset
    sort_option = request.GET.get('sort')
    sort_dict = {
        'price-asc': 'price',
        'price-desc': '-price',
        'new-launch': '-created_at',
        'popular': '-quantity',  # Assuming quantity represents popularity
        'user_wishlist_ids': user_wishlist_ids  # Add this line

    }
    
    if sort_option in sort_dict:
        watches = watches.order_by(sort_dict[sort_option])
    else:
        watches = watches.order_by('-created_at')  # Default sorting

    # Prepare filter options for template
    filter_options = {
        'models': Watch.MODEL_CHOICES,
        'case_sizes': Watch.CASE_SIZE_CHOICES,
        'dial_colors': Watch.DIAL_COLOR_CHOICES,
        'strap_colors': Watch.STRAP_COLOR_CHOICES,
        'dial_shapes': Watch.DIAL_SHAPE_CHOICES,
        'movements': Watch.MOVEMENT_CHOICES,
        'price_ranges': [
            ('under-10000', 'Under ₹10,000'),
            ('10000-25000', '₹10,000 to ₹25,000'),
            ('25000-50000', '₹25,000 to ₹50,000'),
        ],
        'wrist_sizes': [  # Added wrist size options
            ('xs', 'Extra Small (5-6 inches)'),
            ('s', 'Small (6-6.5 inches)'),
            ('m', 'Medium (6.5-7 inches)'),
            ('l', 'Large (7-7.5 inches)'),
            ('xl', 'Extra Large (7.5+ inches)'),
        ]
    }

    return render(request, "men.html", {
        'watches': watches, 
        'search_query': search_query,
        'applied_filters': applied_filters,
        'filter_options': filter_options,
        'sort_option': sort_option,
        'has_search': bool(search_query)  # Add this to indicate if we're in search mode
    }) 

 

def women(request):
    # Initialize variables
    search_query = request.GET.get('search', '').strip()
    filtered_keywords = []
    matched_filters = {}
    applied_filters = {}
    
    # Start with all women's watches or search results
    if search_query:
        # If there's a search query, start with search results
        watches = Watch.objects.filter(category="women")
        search_query = re.sub(r'[^\w\s]', '', search_query)  # Remove special characters
        search_keywords = search_query.lower().split()

        for word in search_keywords:
            match_found = False

            # Check against predefined attributes
            for attr, values in RELEVANT_ATTRIBUTES.items():
                if isinstance(values, list) and word in values:
                    watches = watches.filter(**{f"{attr}__icontains": word})
                    matched_filters[attr] = word
                    match_found = True
                    break
                elif isinstance(values, dict):  # Handle price ranges
                    for key, (min_price, max_price) in values.items():
                        if word in key:
                            watches = watches.filter(price__gte=min_price, price__lt=max_price)
                            matched_filters["price_range"] = key
                            match_found = True
                            break

            if not match_found:
                filtered_keywords.append(word)

        # If no matches found with predefined attributes, search in name and description
        if filtered_keywords:
            search_filter = reduce(
                lambda q, word: q & (Q(name__icontains=word) | Q(descriptions__title__icontains=word) | Q(descriptions__description__icontains=word)),
                filtered_keywords, Q()
            )
            watches = watches.filter(search_filter).distinct()
    else:
        # If no search, start with all women's watches
        watches = Watch.objects.filter(category="women")

    # Store the base queryset (either search results or all products)
    base_queryset = watches

    # Apply user-selected filters from URL parameters to the base queryset
    filter_params = {
        'model': request.GET.get('model'),
        'case_size': request.GET.get('case_size'),
        'dial_color': request.GET.get('dial_color'),
        'strap_color': request.GET.get('strap_color'),
        'dial_shape': request.GET.get('dial_shape'),
        'movement': request.GET.get('movement'),
        'price': request.GET.get('price')
    }

    for key, value in filter_params.items():
        if value:
            if key == 'price':
                if value in RELEVANT_ATTRIBUTES["price_range"]:
                    min_price, max_price = RELEVANT_ATTRIBUTES["price_range"][value]
                    watches = watches.filter(price__gte=min_price, price__lt=max_price)
                    applied_filters[key] = value
            else:
                watches = watches.filter(**{key: value})
                applied_filters[key] = value

    # Sorting logic - applied to the filtered queryset
    sort_option = request.GET.get('sort')
    sort_dict = {
        'price-asc': 'price',
        'price-desc': '-price',
        'new-launch': '-created_at',
        'popular': '-quantity'  # Assuming quantity represents popularity
    }
    
    if sort_option in sort_dict:
        watches = watches.order_by(sort_dict[sort_option])
    else:
        watches = watches.order_by('-created_at')  # Default sorting

    # Prepare filter options for template
    filter_options = {
        'models': Watch.MODEL_CHOICES,
        'case_sizes': Watch.CASE_SIZE_CHOICES,
        'dial_colors': Watch.DIAL_COLOR_CHOICES,
        'strap_colors': Watch.STRAP_COLOR_CHOICES,
        'dial_shapes': Watch.DIAL_SHAPE_CHOICES,
        'movements': Watch.MOVEMENT_CHOICES,
        'price_ranges': [
            ('under-10000', 'Under ₹10,000'),
            ('10000-25000', '₹10,000 to ₹25,000'),
            ('25000-50000', '₹25,000 to ₹50,000'),
        ]
    }

    return render(request, "women.html", {
        'watches': watches, 
        'search_query': search_query,
        'applied_filters': applied_filters,
        'filter_options': filter_options,
        'sort_option': sort_option,
        'has_search': bool(search_query)  # Add this to indicate if we're in search mode
    })



def kid(request):
    # Initialize variables
    search_query = request.GET.get('search', '').strip()
    filtered_keywords = []
    matched_filters = {}
    applied_filters = {}
    
    # Start with all women's watches or search results
    if search_query:
        # If there's a search query, start with search results
        watches = Watch.objects.filter(category="kids")
        search_query = re.sub(r'[^\w\s]', '', search_query)  # Remove special characters
        search_keywords = search_query.lower().split()

        for word in search_keywords:
            match_found = False

            # Check against predefined attributes
            for attr, values in RELEVANT_ATTRIBUTES.items():
                if isinstance(values, list) and word in values:
                    watches = watches.filter(**{f"{attr}__icontains": word})
                    matched_filters[attr] = word
                    match_found = True
                    break
                elif isinstance(values, dict):  # Handle price ranges
                    for key, (min_price, max_price) in values.items():
                        if word in key:
                            watches = watches.filter(price__gte=min_price, price__lt=max_price)
                            matched_filters["price_range"] = key
                            match_found = True
                            break

            if not match_found:
                filtered_keywords.append(word)

        # If no matches found with predefined attributes, search in name and description
        if filtered_keywords:
            search_filter = reduce(
                lambda q, word: q & (Q(name__icontains=word) | Q(descriptions__title__icontains=word) | Q(descriptions__description__icontains=word)),
                filtered_keywords, Q()
            )
            watches = watches.filter(search_filter).distinct()
    else:
        # If no search, start with all women's watches
        watches = Watch.objects.filter(category="kids")

    # Store the base queryset (either search results or all products)
    base_queryset = watches

    # Apply user-selected filters from URL parameters to the base queryset
    filter_params = {
        'model': request.GET.get('model'),
        'case_size': request.GET.get('case_size'),
        'dial_color': request.GET.get('dial_color'),
        'strap_color': request.GET.get('strap_color'),
        'dial_shape': request.GET.get('dial_shape'),
        'movement': request.GET.get('movement'),
        'price': request.GET.get('price')
    }

    for key, value in filter_params.items():
        if value:
            if key == 'price':
                if value in RELEVANT_ATTRIBUTES["price_range"]:
                    min_price, max_price = RELEVANT_ATTRIBUTES["price_range"][value]
                    watches = watches.filter(price__gte=min_price, price__lt=max_price)
                    applied_filters[key] = value
            else:
                watches = watches.filter(**{key: value})
                applied_filters[key] = value

    # Sorting logic - applied to the filtered queryset
    sort_option = request.GET.get('sort')
    sort_dict = {
        'price-asc': 'price',
        'price-desc': '-price',
        'new-launch': '-created_at',
        'popular': '-quantity'  # Assuming quantity represents popularity
    }
    
    if sort_option in sort_dict:
        watches = watches.order_by(sort_dict[sort_option])
    else:
        watches = watches.order_by('-created_at')  # Default sorting

    # Prepare filter options for template
    filter_options = {
        'models': Watch.MODEL_CHOICES,
        'case_sizes': Watch.CASE_SIZE_CHOICES,
        'dial_colors': Watch.DIAL_COLOR_CHOICES,
        'strap_colors': Watch.STRAP_COLOR_CHOICES,
        'dial_shapes': Watch.DIAL_SHAPE_CHOICES,
        'movements': Watch.MOVEMENT_CHOICES,
        'price_ranges': [
            ('under-10000', 'Under ₹10,000'),
            ('10000-25000', '₹10,000 to ₹25,000'),
            ('25000-50000', '₹25,000 to ₹50,000'),
        ]
    }

    return render(request, "kid.html", {
        'watches': watches, 
        'search_query': search_query,
        'applied_filters': applied_filters,
        'filter_options': filter_options,
        'sort_option': sort_option,
        'has_search': bool(search_query)  # Add this to indicate if we're in search mode
    })


from django.shortcuts import get_object_or_404

def product_detail(request, product_id):
    product = get_object_or_404(Watch, id=product_id)
    additional_images = product.images.all()
    return render(request, "product_detail.html", {
        'product': product,
        'additional_images': additional_images
    })
# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Watch, Wishlist

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# views.py (additional code for handling toggle)
from django.http import JsonResponse
@login_required
def toggle_wishlist(request, watch_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'unauthenticated'}, status=401)

    watch = Watch.objects.get(id=watch_id)
    if request.method == 'POST':
        # Check if product is already in wishlist
        if Wishlist.objects.filter(user=request.user, watch=watch).exists():
            Wishlist.objects.filter(user=request.user, watch=watch).delete()
            return JsonResponse({'status': 'removed'})
        else:
            Wishlist.objects.create(user=request.user, watch=watch)
            return JsonResponse({'status': 'added'})


import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

# For OTP sending (e.g., use Twilio API or SMS provider)
def send_otp(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        otp = random.randint(1000, 9999)
        # Store OTP in session or database
        request.session['otp'] = otp
        request.session['phone'] = phone
        # Send the OTP using a provider
        print(f"OTP for {phone} is {otp}")  # Replace with SMS sending logic
        messages.success(request, "OTP sent successfully!")
        return render(request, 'login.html')
    return redirect('login')

def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        phone = request.session.get('phone')
        session_otp = request.session.get('otp')

        if str(user_otp) == str(session_otp):
            # OTP is valid, proceed with login/signup
            del request.session['otp']  # Clear OTP after use
            return redirect('home')  # Replace with your desired redirect
        else:
            messages.error(request, "Invalid OTP, please try again.")
            return render(request, 'login.html')
    return redirect('login')
from django.shortcuts import redirect

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

import re

import re
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    next_url = request.GET.get('next', '/')  # Capture the URL the user was trying to visit
    print(f"Captured next_url: {next_url}")  # Debugging print

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print("User authenticated successfully.")  # Debugging print

            # ✅ Handle redirection for product detail pages
            match = re.match(r'^/product(?:_login)?/(\d+)/$', next_url)  # Supports both `/product/` and `/product_login/`
            if match:
                watch_id = match.group(1)  # Extract `watch_id`
                print(f"Redirecting to product_detail_login with Watch ID: {watch_id}")  # Debugging print
                return redirect('app:product_detail_login', watch_id=int(watch_id))

            # ✅ Redirecting based on page
            elif 'women' in next_url:
                return redirect('app:women_loggedin')
            elif 'men' in next_url:
                return redirect('app:men_loggedin')
            else:
                return redirect('app:kid_loggedin')  # Default page after login

        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html", {'next': next_url})







from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm  # Import the new form
from .models import Address  # Import Address model

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            address = form.cleaned_data['address']  # Get the address input
            Address.objects.create(user=user, address=address)  # Save address

            messages.success(request, f"Account created for {user.username}!")
            return redirect('app:login')  # Adjust to your login URL name
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

from django.contrib.auth.decorators import login_required

@login_required
def men_loggedin(request):
    # Initialize variables
    search_query = request.GET.get('search', '').strip()
    filtered_keywords = []
    matched_filters = {}
    applied_filters = {}
    
    # Start with all men's watches or search results
    if search_query:
        # If there's a search query, start with search results
        watches = Watch.objects.filter(category="men")
        search_query = re.sub(r'[^\w\s]', '', search_query)  # Remove special characters
        search_keywords = search_query.lower().split()

        for word in search_keywords:
            match_found = False

            # Check against predefined attributes
            for attr, values in RELEVANT_ATTRIBUTES.items():
                if isinstance(values, list) and word in values:
                    watches = watches.filter(**{f"{attr}__icontains": word})
                    matched_filters[attr] = word
                    match_found = True
                    break
                elif isinstance(values, dict):  # Handle price ranges
                    for key, (min_price, max_price) in values.items():
                        if word in key:
                            watches = watches.filter(price__gte=min_price, price__lt=max_price)
                            matched_filters["price_range"] = key
                            match_found = True
                            break

            if not match_found:
                filtered_keywords.append(word)

        # If no matches found with predefined attributes, search in name and description
        if filtered_keywords:
            search_filter = reduce(
                lambda q, word: q & (Q(name__icontains=word) | Q(descriptions__title__icontains=word) | Q(descriptions__description__icontains=word)),
                filtered_keywords, Q()
            )
            watches = watches.filter(search_filter).distinct()
    else:
        # If no search, start with all men's watches
        watches = Watch.objects.filter(category="men")

    # Store the base queryset (either search results or all products)
    base_queryset = watches

    # Apply user-selected filters from URL parameters to the base queryset
    filter_params = {
        'model': request.GET.get('model'),
        'case_size': request.GET.get('case_size'),
        'dial_color': request.GET.get('dial_color'),
        'strap_color': request.GET.get('strap_color'),
        'dial_shape': request.GET.get('dial_shape'),
        'movement': request.GET.get('movement'),
        'price': request.GET.get('price'),
        'wrist_size': request.GET.get('wrist_size')  # Added wrist_size filter
    }

    for key, value in filter_params.items():
        if value:
            if key == 'price':
                if value in RELEVANT_ATTRIBUTES["price_range"]:
                    min_price, max_price = RELEVANT_ATTRIBUTES["price_range"][value]
                    watches = watches.filter(price__gte=min_price, price__lt=max_price)
                    applied_filters[key] = value
            else:
                watches = watches.filter(**{key: value})
                applied_filters[key] = value

    # Sorting logic - applied to the filtered queryset
    sort_option = request.GET.get('sort')
    sort_dict = {
        'price-asc': 'price',
        'price-desc': '-price',
        'new-launch': '-created_at',
        'popular': '-quantity'  # Assuming quantity represents popularity
    }
    
    if sort_option in sort_dict:
        watches = watches.order_by(sort_dict[sort_option])
    else:
        watches = watches.order_by('-created_at')  # Default sorting

    # Get user's wishlist IDs
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('watch_id', flat=True)

    # Prepare filter options for template
    filter_options = {
        'models': Watch.MODEL_CHOICES,
        'case_sizes': Watch.CASE_SIZE_CHOICES,
        'dial_colors': Watch.DIAL_COLOR_CHOICES,
        'strap_colors': Watch.STRAP_COLOR_CHOICES,
        'dial_shapes': Watch.DIAL_SHAPE_CHOICES,
        'movements': Watch.MOVEMENT_CHOICES,
        'price_ranges': [
            ('under-10000', 'Under ₹10,000'),
            ('10000-25000', '₹10,000 to ₹25,000'),
            ('25000-50000', '₹25,000 to ₹50,000'),
        ],
        'wrist_sizes': [  # Added wrist size options
            ('xs', 'Extra Small (5-6 inches)'),
            ('s', 'Small (6-6.5 inches)'),
            ('m', 'Medium (6.5-7 inches)'),
            ('l', 'Large (7-7.5 inches)'),
            ('xl', 'Extra Large (7.5+ inches)'),
        ]
    }

    return render(request, "men_loggedin.html", {
        'watches': watches, 
        'search_query': search_query,
        'applied_filters': applied_filters,
        'filter_options': filter_options,
        'sort_option': sort_option,
        'has_search': bool(search_query),  # Add this to indicate if we're in search mode
        'user_wishlist_ids': user_wishlist_ids  # Keep wishlist functionality
    })

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('watch')
    return render(request, "wishlist.html", {'wishlist_items': wishlist_items})

    
@login_required
def women_loggedin(request):
    
    search_query = request.GET.get('search', '').strip()
    filtered_keywords = []
    matched_filters = {}
    applied_filters = {}
    
    # Start with all men's watches or search results
    if search_query:
        # If there's a search query, start with search results
        watches = Watch.objects.filter(category="women")
        search_query = re.sub(r'[^\w\s]', '', search_query)  # Remove special characters
        search_keywords = search_query.lower().split()

        for word in search_keywords:
            match_found = False

            # Check against predefined attributes
            for attr, values in RELEVANT_ATTRIBUTES.items():
                if isinstance(values, list) and word in values:
                    watches = watches.filter(**{f"{attr}__icontains": word})
                    matched_filters[attr] = word
                    match_found = True
                    break
                elif isinstance(values, dict):  # Handle price ranges
                    for key, (min_price, max_price) in values.items():
                        if word in key:
                            watches = watches.filter(price__gte=min_price, price__lt=max_price)
                            matched_filters["price_range"] = key
                            match_found = True
                            break

            if not match_found:
                filtered_keywords.append(word)

        # If no matches found with predefined attributes, search in name and description
        if filtered_keywords:
            search_filter = reduce(
                lambda q, word: q & (Q(name__icontains=word) | Q(descriptions__title__icontains=word) | Q(descriptions__description__icontains=word)),
                filtered_keywords, Q()
            )
            watches = watches.filter(search_filter).distinct()
    else:
        # If no search, start with all men's watches
        watches = Watch.objects.filter(category="women")

    # Store the base queryset (either search results or all products)
    base_queryset = watches

    # Apply user-selected filters from URL parameters to the base queryset
    filter_params = {
        'model': request.GET.get('model'),
        'case_size': request.GET.get('case_size'),
        'dial_color': request.GET.get('dial_color'),
        'strap_color': request.GET.get('strap_color'),
        'dial_shape': request.GET.get('dial_shape'),
        'movement': request.GET.get('movement'),
        'price': request.GET.get('price')
    }

    for key, value in filter_params.items():
        if value:
            if key == 'price':
                if value in RELEVANT_ATTRIBUTES["price_range"]:
                    min_price, max_price = RELEVANT_ATTRIBUTES["price_range"][value]
                    watches = watches.filter(price__gte=min_price, price__lt=max_price)
                    applied_filters[key] = value
            else:
                watches = watches.filter(**{key: value})
                applied_filters[key] = value

    # Sorting logic - applied to the filtered queryset
    sort_option = request.GET.get('sort')
    sort_dict = {
        'price-asc': 'price',
        'price-desc': '-price',
        'new-launch': '-created_at',
        'popular': '-quantity'  # Assuming quantity represents popularity
    }
    
    if sort_option in sort_dict:
        watches = watches.order_by(sort_dict[sort_option])
    else:
        watches = watches.order_by('-created_at')  # Default sorting

    # Get user's wishlist IDs
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('watch_id', flat=True)

    # Prepare filter options for template
    filter_options = {
        'models': Watch.MODEL_CHOICES,
        'case_sizes': Watch.CASE_SIZE_CHOICES,
        'dial_colors': Watch.DIAL_COLOR_CHOICES,
        'strap_colors': Watch.STRAP_COLOR_CHOICES,
        'dial_shapes': Watch.DIAL_SHAPE_CHOICES,
        'movements': Watch.MOVEMENT_CHOICES,
        'price_ranges': [
            ('under-10000', 'Under ₹10,000'),
            ('10000-25000', '₹10,000 to ₹25,000'),
            ('25000-50000', '₹25,000 to ₹50,000'),
        ]
    }

    return render(request, "women_loggedin.html", {
        'watches': watches, 
        'search_query': search_query,
        'applied_filters': applied_filters,
        'filter_options': filter_options,
        'sort_option': sort_option,
        'has_search': bool(search_query),  # Add this to indicate if we're in search mode
        'user_wishlist_ids': user_wishlist_ids
    })
@login_required
def kid_loggedin(request):
    
    search_query = request.GET.get('search', '').strip()
    filtered_keywords = []
    matched_filters = {}
    applied_filters = {}
    
    # Start with all men's watches or search results
    if search_query:
        # If there's a search query, start with search results
        watches = Watch.objects.filter(category="kids")
        search_query = re.sub(r'[^\w\s]', '', search_query)  # Remove special characters
        search_keywords = search_query.lower().split()

        for word in search_keywords:
            match_found = False

            # Check against predefined attributes
            for attr, values in RELEVANT_ATTRIBUTES.items():
                if isinstance(values, list) and word in values:
                    watches = watches.filter(**{f"{attr}__icontains": word})
                    matched_filters[attr] = word
                    match_found = True
                    break
                elif isinstance(values, dict):  # Handle price ranges
                    for key, (min_price, max_price) in values.items():
                        if word in key:
                            watches = watches.filter(price__gte=min_price, price__lt=max_price)
                            matched_filters["price_range"] = key
                            match_found = True
                            break

            if not match_found:
                filtered_keywords.append(word)

        # If no matches found with predefined attributes, search in name and description
        if filtered_keywords:
            search_filter = reduce(
                lambda q, word: q & (Q(name__icontains=word) | Q(descriptions__title__icontains=word) | Q(descriptions__description__icontains=word)),
                filtered_keywords, Q()
            )
            watches = watches.filter(search_filter).distinct()
    else:
        # If no search, start with all men's watches
        watches = Watch.objects.filter(category="kids")

    # Store the base queryset (either search results or all products)
    base_queryset = watches

    # Apply user-selected filters from URL parameters to the base queryset
    filter_params = {
        'model': request.GET.get('model'),
        'case_size': request.GET.get('case_size'),
        'dial_color': request.GET.get('dial_color'),
        'strap_color': request.GET.get('strap_color'),
        'dial_shape': request.GET.get('dial_shape'),
        'movement': request.GET.get('movement'),
        'price': request.GET.get('price')
    }

    for key, value in filter_params.items():
        if value:
            if key == 'price':
                if value in RELEVANT_ATTRIBUTES["price_range"]:
                    min_price, max_price = RELEVANT_ATTRIBUTES["price_range"][value]
                    watches = watches.filter(price__gte=min_price, price__lt=max_price)
                    applied_filters[key] = value
            else:
                watches = watches.filter(**{key: value})
                applied_filters[key] = value

    # Sorting logic - applied to the filtered queryset
    sort_option = request.GET.get('sort')
    sort_dict = {
        'price-asc': 'price',
        'price-desc': '-price',
        'new-launch': '-created_at',
        'popular': '-quantity'  # Assuming quantity represents popularity
    }
    
    if sort_option in sort_dict:
        watches = watches.order_by(sort_dict[sort_option])
    else:
        watches = watches.order_by('-created_at')  # Default sorting

    # Get user's wishlist IDs
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('watch_id', flat=True)

    # Prepare filter options for template
    filter_options = {
        'models': Watch.MODEL_CHOICES,
        'case_sizes': Watch.CASE_SIZE_CHOICES,
        'dial_colors': Watch.DIAL_COLOR_CHOICES,
        'strap_colors': Watch.STRAP_COLOR_CHOICES,
        'dial_shapes': Watch.DIAL_SHAPE_CHOICES,
        'movements': Watch.MOVEMENT_CHOICES,
        'price_ranges': [
            ('under-10000', 'Under ₹10,000'),
            ('10000-25000', '₹10,000 to ₹25,000'),
            ('25000-50000', '₹25,000 to ₹50,000'),
        ]
    }

    return render(request, "kid_loggedin.html", {
        'watches': watches, 
        'search_query': search_query,
        'applied_filters': applied_filters,
        'filter_options': filter_options,
        'sort_option': sort_option,
        'has_search': bool(search_query),  # Add this to indicate if we're in search mode
        'user_wishlist_ids': user_wishlist_ids
    })
from django.shortcuts import render, get_object_or_404
from .models import Watch, Wishlist


from django.shortcuts import render, get_object_or_404
from .models import Watch, Wishlist

from django.shortcuts import render, get_object_or_404
from .models import Watch, WatchImage
from .models import Watch, WatchImage, WatchDescription

def product_detail(request, watch_id):
    watch = get_object_or_404(Watch, id=watch_id)
    images = WatchImage.objects.filter(watch=watch)  # Fetch related images
    descriptions = WatchDescription.objects.filter(watch=watch)  # Fetch descriptions
    user_authenticated = request.user.is_authenticated

    return render(request, 'product_detail.html', {
        'watch': watch,
        'images': images,
        'user_authenticated': user_authenticated,
        'descriptions': descriptions,
    })


from django.shortcuts import render, get_object_or_404
from .models import Watch, WatchImage

from django.shortcuts import render, get_object_or_404
from .models import Watch, Cart, CartItem, Wishlist

def product_detail_login(request, watch_id):
    watch = get_object_or_404(Watch, id=watch_id)
    
    # Fetch images (if applicable)
    images = WatchImage.objects.filter(watch=watch)
    reviews = Review.objects.filter(watch=watch)

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the item exists in the cart
    cart_item = CartItem.objects.filter(cart=cart, watch=watch).first()
    descriptions = WatchDescription.objects.filter(watch=watch)

    # Check if the item exists in the wishlist
    wishlist_items = Wishlist.objects.filter(user=request.user).values_list('watch_id', flat=True)

    return render(request, 'product_detail_login.html', {
        'watch': watch,
        'images': images,
        'reviews': reviews,
        'cart_item': cart_item,
        'descriptions': descriptions,  # Will be None if not in cart
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Watch, Cart
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Watch
from django.urls import reverse
from decimal import Decimal

# Simulating a session-based cart (could be replaced with a database model)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Watch, Cart, CartItem

from django.shortcuts import redirect

@login_required
def add_to_cart(request, watch_id):
    watch = get_object_or_404(Watch, id=watch_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add to cart or increase quantity
    cart_item, created = CartItem.objects.get_or_create(cart=cart, watch=watch)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('app:product_detail_login', watch_id=watch.id)  # Reload product page




@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)  # Get the cart for the logged-in user
    cart_items = CartItem.objects.filter(cart=cart)  # Get only the items of the logged-in user
    total_price = sum(item.watch.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {"cart_items": cart_items, "total_price": total_price})



@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    watch_id = cart_item.watch.id  # Get the watch ID before deleting
    cart_item.delete()

    return redirect('app:product_detail_login', watch_id=watch_id)  # Reload product page



from django.shortcuts import redirect, get_object_or_404

@login_required
def update_cart(request, cart_item_id, action):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    available_stock = cart_item.watch.quantity  # Assuming "stock" is a field in Watch model

    if action == "increase":
        if cart_item.quantity < available_stock:  # Prevent exceeding stock
            cart_item.quantity += 1
            cart_item.save()
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

    # Determine the next page
    next_page = request.GET.get('next', 'app:view_cart')  # Default to view_cart
    return redirect(next_page)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CartItem, Cart

@login_required
def some_view(request):
    cart_count = CartItem.objects.filter(cart__user=request.user).count()
    
    return render(request, 'your_template.html', {'cart_count': cart_count})



from django.shortcuts import render
from .models import Cart, CartItem

def order_summary(request):
    
    try:
        cart = Cart.objects.get(user=request.user)  # Get cart for the logged-in user
        cart_items = CartItem.objects.filter(cart=cart)  # Get items in the cart
        total_price = sum(item.watch.price * item.quantity for item in cart_items)  # Calculate total price
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'order_summary.html', context)
from django.shortcuts import redirect
from django.contrib import messages
from .models import Address  # Ensure you have an Address model
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Address

@login_required
def save_address(request):
    if request.method == 'POST':
        address_text = request.POST.get('address')
        next_page = request.POST.get('next_page')  # Get the next page from the form

        if address_text:
            address, created = Address.objects.get_or_create(user=request.user)
            address.address = address_text
            address.save()
            messages.success(request, "Address saved successfully!")
        else:
            messages.error(request, "Please enter a valid address.")

        # Redirect based on the next_page value
        if next_page == "buy_now":
            # Get the watch ID from the buy now item
            cart = Cart.objects.get(user=request.user)
            buy_now_item = CartItem.objects.filter(cart=cart, is_buy_now=True).first()
            if buy_now_item:
                return redirect('app:buy_now', watch_id=buy_now_item.watch.id)
            return redirect('app:index')
        return redirect('app:order_summary')  # Default redirection


import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, HttpResponse


# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
@login_required
def order_payment(request):
    if request.method == "POST":
        try:
            cart = Cart.objects.get(user=request.user)
            
            # Check if user is buying a single item using "Buy Now"
            buy_now_item = CartItem.objects.filter(cart=cart, is_buy_now=True).first()

            if buy_now_item:
                total_price = buy_now_item.watch.price * buy_now_item.quantity
            else:
                # Otherwise, calculate total price from cart items
                cart_items = CartItem.objects.filter(cart=cart, is_buy_now=False)
                total_price = sum(item.watch.price * item.quantity for item in cart_items)

            # Get user's address
            address = Address.objects.filter(user=request.user).first()
            amount = int(total_price) * 100  # Convert to paise
            
            # Create Razorpay Order
            razorpay_order = client.order.create(
                dict(amount=amount, currency="INR", payment_capture="0")
            )
            
            # Prepare context
            context = {
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_merchant_key": settings.RAZORPAY_KEY_ID,
                "razorpay_amount": amount,
                "currency": "INR",
                "callback_url": "http://" + request.get_host() + "/paymenthandler/",
                "total_price": total_price,
                "cart_items": [buy_now_item] if buy_now_item else cart_items,
                "address": address.address if address else None,
                "username": request.user.username,
    "email": request.user.email,
            }
            
            return render(request, "payment.html", context)
            
        except Cart.DoesNotExist:
            return redirect('app:order_summary')
    
    return redirect('app:order_summary')





import traceback
import razorpay
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.mail import mail_admins
from .models import Cart, CartItem, Order, OrderItem, Watch

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Cart, CartItem
import razorpay

# Razorpay API keys (ensure they're configured in settings.py)
RAZORPAY_KEY_ID = "rzp_test_d5VCv4MOwkIpcU"
RAZORPAY_KEY_SECRET = "OXxDDHSLPDiM9yvqbd1SAFdN"
@login_required
@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            client.utility.verify_payment_signature(params_dict)
            
            with transaction.atomic():
                user = request.user
                cart = Cart.objects.get(user=user)
                address = Address.objects.filter(user=user).first()
                if not address:
                    return render(request, "paymentfail.html", {"message": "No delivery address found."})
                
                buy_now_item = CartItem.objects.filter(cart=cart, is_buy_now=True).first()
                
                # Changed this part to use QuerySet instead of Python list
                if buy_now_item:
                    cart_items = CartItem.objects.filter(id=buy_now_item.id)
                else:
                    cart_items = CartItem.objects.filter(cart=cart, is_buy_now=False)
                
                # Validate stock
                for item in cart_items:
                    if item.quantity > item.watch.quantity:
                        return render(request, "paymentfail.html", {
                            "message": f"Only {item.watch.quantity} items left for {item.watch.name}."
                        })
                
                # Calculate total price
                total_price = sum(item.watch.price * item.quantity for item in cart_items)
                
                # Create order
                order = Order.objects.create(
                    user=user,
                    address=address.address,
                    total_amount=total_price,
                    payment_method='razorpay',
                    payment_id=payment_id,
                    razorpay_order_id=razorpay_order_id,
                    status='Confirmed'
                )
                
                # Create order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        watch=item.watch,
                        quantity=item.quantity,
                        price=item.watch.price
                    )
                    item.watch.quantity -= item.quantity
                    item.watch.save()
                
                # Clear cart - now this will work because cart_items is a QuerySet
                cart_items.delete()
                cart.delete()
            
            return render(request, "paymentsuccess.html", {
                "message": "Payment successful! Your order has been placed."
            })
        
        except razorpay.errors.SignatureVerificationError:
            return render(request, "paymentfail.html", {"message": "Payment verification failed."})
    
    return JsonResponse({"error": "Invalid request method."}, status=400)




from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Watch, Cart, CartItem

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Watch, Cart, CartItem  # Make sure to import Order models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Watch, Cart, CartItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Watch
from datetime import datetime, timedelta


from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Watch, Cart, CartItem
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.urls import reverse

@login_required
def buy_now(request, watch_id):
    watch = get_object_or_404(Watch, id=watch_id)
    
    # Get or create cart
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    # Delete any existing buy_now items
    CartItem.objects.filter(cart=cart, is_buy_now=True).delete()
    
    # Create new buy_now item
    cart_item = CartItem.objects.create(
        cart=cart,
        watch=watch,
        quantity=1,
        is_buy_now=True
    )
    
    # Calculate delivery date
    delivery_date = (datetime.now() + timedelta(days=3)).strftime('%a %b %d')
    
    return render(request, 'buynow.html', {
        'cart_items': [cart_item],
        'total_price': watch.price * cart_item.quantity,
        'delivery_date': delivery_date,
        'is_buy_now': True
    })

@login_required
def update_buy_now(request, cart_item_id, action):
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                cart__user=request.user,
                is_buy_now=True
            )
            
            if action == "increase":
                if cart_item.quantity < cart_item.watch.quantity:
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'Only {cart_item.watch.quantity} items available in stock'
                    }, status=400)
                    
            elif action == "decrease":
                # Prevent quantity from going below 1
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    # If quantity is already 1, just return current values
                    return JsonResponse({
                        'success': True,
                        'new_quantity': 1,  # Keep quantity at 1
                        'item_price': float(cart_item.watch.price) * 1,
                        'total_price': float(cart_item.watch.price) * 1 + 3
                    })
            
            # Calculate prices
            item_price = float(cart_item.watch.price) * cart_item.quantity
            total_price = item_price + 3  # Including platform fee
            
            return JsonResponse({
                'success': True,
                'new_quantity': cart_item.quantity,
                'item_price': item_price,
                'total_price': total_price
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Item not found',
                'redirect': reverse('app:index')
            }, status=404)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=400)

@login_required
def process_buy_now_payment(request):
    try:
        cart = Cart.objects.get(user=request.user)
        buy_now_item = CartItem.objects.filter(cart=cart, is_buy_now=True).first()
        
        if not buy_now_item:
            return redirect('app:index')
            
        # Check if the watch still has sufficient quantity
        if buy_now_item.quantity > buy_now_item.watch.quantity:
            messages.error(request, 'Sorry, the requested quantity is no longer available')
            return redirect('app:buy_now', watch_id=buy_now_item.watch.id)
            
        total_price = buy_now_item.watch.price * buy_now_item.quantity
        
        # Process payment here (placeholder)
        
        # After successful payment, update the watch quantity
        buy_now_item.watch.quantity -= buy_now_item.quantity
        buy_now_item.watch.save()
        
        # Delete the buy now item
        buy_now_item.delete()
        
        return redirect('app:payment_success')
        
    except Cart.DoesNotExist:
        return redirect('app:index')
from django.shortcuts import render

def order_confirmation(request):
    return render(request, 'order_confirmation.html')
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})
from django.shortcuts import render
# views.py
def wrist_size_guide(request):
    return render(request, "wrist_size_guide.html")

def measure_wrist(request):
    if request.method == 'POST':
        wrist_size = request.POST.get('wrist_size')
        # You can store this in session if you want to filter watches
        request.session['wrist_size'] = wrist_size
        return JsonResponse({'status': 'success', 'wrist_size': wrist_size})
    return JsonResponse({'status': 'error'}, status=400)
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
@login_required
def process_cod_order(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                cart = Cart.objects.get(user=request.user)
                address = Address.objects.filter(user=request.user).first()
                if not address:
                    messages.error(request, "Please save a delivery address.")
                    return redirect('app:order_summary')

                buy_now_item = CartItem.objects.filter(cart=cart, is_buy_now=True).first()
                
                # Fix: Make sure cart_items is always a QuerySet, not a Python list
                if buy_now_item:
                    cart_items = CartItem.objects.filter(id=buy_now_item.id)
                else:
                    cart_items = CartItem.objects.filter(cart=cart, is_buy_now=False)

                if not cart_items.exists():
                    messages.error(request, 'Your cart is empty')
                    return redirect('app:order_summary')

                # Validate stock
                for item in cart_items:
                    if item.quantity > item.watch.quantity:
                        messages.error(request, f'Sorry, only {item.watch.quantity} items available for {item.watch.name}')
                        # Fixed redirect - don't pass watch_id to order_summary
                        if buy_now_item:
                            return redirect('app:buy_now', watch_id=item.watch.id)
                        else:
                            return redirect('app:order_summary')

                # Calculate total price
                total_price = sum(item.watch.price * item.quantity for item in cart_items)

                # Create order
                order = Order.objects.create(
                    user=request.user,
                    address=address.address,
                    total_amount=total_price,
                    payment_method='cod',
                    status='Pending'
                )

                # Create order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        watch=item.watch,
                        quantity=item.quantity,
                        price=item.watch.price
                    )
                    item.watch.quantity -= item.quantity
                    item.watch.save()

                # Clear cart - now this works because cart_items is a QuerySet
                cart_items.delete()
                cart.delete()

            messages.success(request, '')
            return redirect('app:order_confirmation')

        except Cart.DoesNotExist:
            messages.error(request, 'Cart not found')
            return redirect('app:index')

    return redirect('app:index')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Watch, Review  # Adjust based on your models

@login_required
def submit_review(request, watch_id):
    watch = get_object_or_404(Watch, id=watch_id)
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        # Create a new review
        Review.objects.create(
            watch=watch,
            user=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Your review has been submitted successfully!")
        return redirect("app:product_detail_login", watch_id=watch.id)
    return redirect("app:product_detail_login", watch_id=watch.id)









