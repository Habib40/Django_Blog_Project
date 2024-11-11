from django.shortcuts import render,redirect
from.forms import RegistrationForm,LoginForm
from django.contrib.auth import authenticate,login
from .models import Account
from django.contrib import messages,auth
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# for email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import requests

Account = get_user_model()




class RegisterView(View):
    def get(self, request):
        forms = RegistrationForm()
        return render(request, 'accounts/register.html', {'forms': forms})

    def post(self, request):
        forms = RegistrationForm(request.POST)
        if forms.is_valid():
            first_name = forms.cleaned_data['first_name']
            last_name = forms.cleaned_data['last_name']
            phone_number = forms.cleaned_data['phone_number']
            email = forms.cleaned_data['email']
            password = forms.cleaned_data['password']
            
            # Create the user using the custom manager
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=email.split('@')[0],  # Assuming email before @ as username
                email=email,
                password=password
            )
            user.phone_number = phone_number
           
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            mail_body = render_to_string('accounts/account_activate_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)             
            })
            to_email = email
            from_email = 'habibkb5080@gmail.com'  # Replace with your sender email
            send_mail(mail_subject, mail_body, from_email, [to_email], fail_silently=False)

            return redirect("/accounts/login/?commands=verification&email=" +email)
        else:
            # If the form is not valid, show error messages
            for error in forms.errors.values():
                messages.error(request, error)

        return render(request, 'accounts/register.html', {'forms': forms})

   
def Activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        
        
def login_view(request):
    if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(request, email=email, password=password)
            if user is not None:
                
              
                auth.login(request, user)
                messages.success(request, 'You are logged in!')
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                     nextPage = params['next']
                    return redirect(nextPage)
                except:
                  return redirect('index') # Redirect to a success page after login
               
            else:
             messages.error(request, 'Invalid login credential.')
             return redirect('login')
    return render(request, 'accounts/login.html')