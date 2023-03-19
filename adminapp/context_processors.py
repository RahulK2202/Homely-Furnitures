from userapp.models import Customer

def user_context(request):
    user = Customer.objects.get(username=request.user)
    return {'current_user': user}
