from django.shortcuts import render, redirect
from .forms import ContactForm
from django.core.mail import send_mail
from django.contrib import messages

# Create your views here.
def home_view(request):
    return render(request, 'pages/home.html')

def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            print("Data is valid")

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            message_body = (
                f"You have a new message from your portfolio \n"
                f"Name: {name} \n"
                f"Email: {email} \n"
                f"Message: {message}"
            )

            try:
                send_mail(
                    "Email from Portfolio",
                    message_body,
                    email,
                    ['nick.a.greenfield@gmail.com'],
                )

                print("Email sent successfully")
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('contact')  # Prevent resubmission on refresh

            except Exception as e:
                print(f"Error sending the email: {e}")
                messages.error(request, f'Error sending the email: {e}')
                return redirect('contact')

        else:
            print("Invalid Data")
            messages.error(request, 'Please correct the errors below.')

    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {"form": form})