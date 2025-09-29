from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, JsonResponse
from .models import Transaction, Profile, Account, KYCDocument
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db.models import Q

# Create your views here.
def loginView(request : HttpRequest) :
    error,message = None, None
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not password or len(password) < 8 :
            return render(request, 'login.html', {"error":True, "message":"password is required and must meet minimun length to login"})
        user_returned = authenticate(request, username=email, password=password)
        if not user_returned :
            return render(request, 'login.html',{"error": True, "message": "Invalid Credentials"})
        login(request, user_returned)
        return redirect("client_dashboard")
    
    return render(request, 'login.html', {"error": error, "message": message})
    # return HttpResponse('''
    #     <a href="http://127.0.0.1:5500/Gidex/BOA.html">come here</a>
    #     <h2>Logins</h2>
    #     <p>LOGIN PAGE FORM</p>
    #     '''
    
def signUp(request : HttpRequest) :
    error = None
    if request.method == "POST":
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2 or len(password1) < 8 :
            error = 'ensure both passwords match and length is greater than 7'
        else : 
            try :
                user_exist = User.objects.filter(username = email).first()
                if user_exist :
                    error = 'User already exists for this account'
                else:
                    user = User.objects.create_user(username=email, password=password1)
                    #we can now generate an acct number for the user
                    account = Account.objects.create(user=user)
                    user.save()
                    account.save()
                    return redirect("client_login")
            except Exception as e :
                error = str (e)
    return render(request, 'signup.html', {"error" : error})

@login_required(login_url='client_login')
def TransferPage(request: HttpRequest):
    error = None
    owner_account = Account.objects.get(user=request.user)
    if request.method == "POST":
        reciever_account_number = request.POST.get("account_number")
        amount_to_send = request.POST.get("amount")
        sender_pin = request.POST.get("pin")

        #first check amount is valid then check if the balance is enough
        if not amount_to_send or not amount_to_send.isdigit():
            return render (request, 'transfer.html', {"error":"Amount to send must be a valid number", "account":owner_account})
        
        user_balance = owner_account.balance
        amount_in_decimal = Decimal(amount_to_send)
        #user balance must not be less than amount he or she is to send
        if user_balance < amount_in_decimal :
          return render (request, 'transfer.html', {"error":"Bobo u no get money!!!", "account":owner_account})

        #check if the user sends in the pin
        if not sender_pin  or not sender_pin.isdigit() or len(sender_pin) != 4:
            return render (request, 'transfer.html', {"error":"You must enter your pin and must be a 4 digit pin", "account":owner_account})
        #next confirm the user pin
        is_pin_correct = owner_account.verifyPass(sender_pin)
        if not is_pin_correct :
           return render (request, 'transfer.html', {"error":"Invalid pin entered!", "account":owner_account})
        # next is for checking the account number of the reciever etc 
        if not reciever_account_number or not reciever_account_number.isdigit() or len(reciever_account_number) !=10:
            return render (request, 'transfer.html', {"error":"Reciever Account number must exist and must be a 10 digit number!", "account":owner_account})
        
        try :
            reciever_account = Account.objects.get(account_number = reciever_account_number)
            # increase the reciever balance and decrease the sender balance
            reciever_account.balance += amount_in_decimal
            owner_account.balance -= amount_in_decimal

            owner_account.save()
            reciever_account.save()
            #document the transfer into transaction model....
            transaction = Transaction.objects.create(from_account = owner_account, to_account = reciever_account, 
            amount = amount_in_decimal, status = 'success', transaction_type = 'Transfer')
            transaction.save()
            #here u redirect instead of going to the same page
            return render (request, 'transfer.html', {"success": f'Transfer of NGN {amount_to_send} succesfully sent to {reciever_account.user.username}',"account":owner_account, "transaction_ref": transaction.ref})
        except Account.DoesNotExist:
            return render (request, 'transfer.html', {"error": f'Account Number {reciever_account_number} not found!', "account":owner_account})
        
    return render (request, 'transfer.html', {"error":error, "account":owner_account})


@login_required(login_url='client_login')
def PinPage(request: HttpRequest):
    user_has_pin = False
    account = Account.objects.get(user = request.user)
    if account.pin_hash :
        user_has_pin = True

    if request.method == "POST":
        new_pin = request.POST.get("new_pin")
        confirm_pin = request.POST.get("confirm_pin")

        if new_pin != confirm_pin or  len(new_pin) != 4 or not new_pin.isdigit() :
                return render(request, 'pin.html', {"user_has_pin": user_has_pin, "error" :"Pin must be digit and length must not be less than 4"})
        if user_has_pin :
            current_pin = request.POST.get("current_pin")
            if not current_pin or len(current_pin) !=4 or not current_pin.isdigit():
                return render(request, 'pin.html', {"user_has_pin": user_has_pin, "error" :"you must enter your current pin and must be a 4 digit pin"})
            #now we vefify the old password if it matches the one stored in our hash
            is_correct = account.verifyPass(current_pin)
            if not is_correct:
               return render(request, 'pin.html', {"user_has_pin": user_has_pin, "error" :"Wrong pin entered"})
            account.createPin(new_pin)
            return render(request, 'pin.html', {"user_has_pin": True, "success":"Pin updated succesfully"})

            #if we doing update we process them all in here
        # if it gets down here means  the user have not set a password before
        # at this stage it means all validation for setting a new password
        account.createPin(new_pin)
        return render(request, 'pin.html', {"user_has_pin": True, "success":"Pin created succesfully"})
    return render(request, 'pin.html', {"user_has_pin": user_has_pin})


@login_required(login_url='client_login')
def ProfilePage(request: HttpRequest):
    return render (request, 'profile.html', {})

@login_required(login_url='client_login')
def DashboardPage(request: HttpRequest):
    user = request.user
    account = Account.objects.get(user=user)
    return render (request, 'dashboard.html', {"account":account})

@login_required(login_url='client_login')
def TransactionPage(request: HttpRequest):
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(Q(from_account = account) | Q(to_account=account))
    return render(request, 'transactions.html', {"transactions":transactions})


@login_required(login_url='client_login')
def Logout_Page(request:HttpRequest):
    logout(request)
    return redirect("client_login")


# return HttpResponse('''
    #     <h2>SIGN UP</h2>/b
    #     <p>SIGN UP PAGE FORM</p>
    #     '''
    
    
# def cardPurchaseEndpoint(request):
#     description = {
#         "buy card" : "/card/purchase",
#         "amount" : [500,1000,2000,5000],
#         "method" : "POST"
#     }
#     return JsonResponse(
#         data = description
#     )
# def getAllProfile(request: HttpRequest) -> JsonResponse:
#     profiles = Profile.objects.all()
#     data = {}
#     count = 0
#     for profile in profiles:
#         data[count] = {
#             "username" : profile.user.username,
#             "phone" : profile.phone
#         }
#         count +=1

#     return JsonResponse(
#         data= data,
#         safe = False
#     )

# @login_required(login_url='client_login')
# def profilePage(request):
#     user : User = request.user 
#     try:
#         pass
#     except Exception :
#         return  render(request, 'profiles.html', {"username":None})
#     return render(request, 'profiles.html',{"username": user.username})