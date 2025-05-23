from django.shortcuts import render
from .forms import ContactForm
from django.core.mail import send_mail


# Create your views here.
def home_view(request):
    return render(request, 'pages/home.html')

def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    return render(request, 'pages/contact.html')

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        #Collect data of form
        if form.is_valid():
            print("Data is valid")

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            # This is the email
            message_body = (
                f"You have a new smail from your portfolio \n"
                f"Name: {name} \n"
                f"Email: {email} \n"
                f"Message: {message}"
            )

            # Try to send email

            try:
                #send_mail <-- Django Core Email
                send_mail(
                    "Email from Portfolio",              #Subject
                    message_body,                       #Message body -> what the user typed
                    email,                              #From email -> the user's email
                    ['nick.a.greenfield@gmail.com']     #To email
                )

                print("Email sent successfully")

                #render and redirect
                return render(request, 'pages/contact.html', {
                    'form':form
                    })

            except Exception as e:

                print(f"Error sending the email:{e}")
                return render(request, 'pages/contact.html', {
                    'form':form,
                    'error': str(e)
                    })

        else:
            print("Invalid Data")

    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {"form": form})