from django.shortcuts import render
from .forms import ContactForm
from django.core.mail import send_mail

# Create your views here.
def home_view(request):
    return render(request, 'pages/home.html')

def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        # Collect data from form
        if form.is_valid():
            print("Data is valid")

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            # This is the email body
            message_body = (
                f"You have a new message from your portfolio \n"
                f"Name: {name} \n"
                f"Email: {email} \n"
                f"Message: {message}"
            )

            # Try to send the email
            try:
                send_mail(
                    "Email from Portfolio",  # Subject
                    message_body,            # Message body
                    email,                   # From email
                    ['nick.a.greenfield@gmail.com'],  # To email
                )

                print("Email sent successfully")

                # Return the form with a success message
                return render(request, 'pages/contact.html', {
                    'form': form,
                    'success': 'Your message has been sent successfully!'
                })

            except Exception as e:
                print(f"Error sending the email: {e}")
                return render(request, 'pages/contact.html', {
                    'form': form,
                    'error': f'Error sending the email: {e}'
                })

        else:
            print("Invalid Data")
            return render(request, 'pages/contact.html', {
                'form': form,
                'error': 'Please correct the errors below.'
            })
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {"form": form})