from django.shortcuts import render, redirect
from django.views.generic import View
from budget.models import Transaction
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.cache import never_cache
# Create your views here.


def signin_required(fn):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Invalid session")
            return redirect("signin")
        else:
            return fn(request,*args, **kwargs)
    return wrapper



decs = [signin_required, never_cache]

#to list all transactions
#url:localhost:8000/all/
#get method
@method_decorator(decs, name="dispatch")
class TransactionListView(View):
    def get(self, request, *args, **kwargs):
        qs =Transaction.objects.filter(user=request.user)
        curr_month = timezone.now().month
        curr_year = timezone.now().year
        data = Transaction.objects.filter(
        user = request.user,
        created_date__month = curr_month,
        created_date__year = curr_year,



        ).values("type").annotate(type_sum = Sum("amount"))
        print(data)

        cat_data = Transaction.objects.filter(
        user = request.user,
        created_date__month = curr_month,
        created_date__year = curr_year,



        ).values("category").annotate(cat_sum = Sum("amount"))
      




        # expense_tot = Transaction.objects.filter(
        #     user = request.user,
        #     type = "expense",
        #     created_date__month = curr_month,
        #     created_date__year = curr_year).aggregate(Sum("amount"))
        # income_tot = Transaction.objects.filter(
        #     user = request.user,
        #     type = "income",
        #     created_date__month = curr_month,
        #     created_date__year = curr_year).aggregate(Sum("amount"))
        # print(income_tot)
        return render(request, "transaction_list.html", {"data":qs, "type_total":data, "cat_total": cat_data})
    
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ("created_date", "user")           # to generate a form with all fields from the model except the cureent one in exclude 
        # fields = ["tiitle", "amount", "type"] to generate a form with all fields from the model with the current fields
        #         # fields = "__all__"  to generate a form with all fields from the model

        widgets= {
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
            "type": forms.Select(attrs={"class":"form-control form-select"}),
            "category": forms.Select(attrs={"class":"form-control form-select"})


        }








class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username","email" ,"password"]
        widgets = {
           "username": forms.TextInput(attrs={"class":"form-control"}),
           "email": forms.EmailInput(attrs={"class":"form-control"}),
           "password": forms.PasswordInput(attrs={"class":"form-control"})

        }




class LoginForm(forms.Form):
    username= forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    password= forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))



#to create a transaction
#url:localhost:8000/add/
#get and post method
@method_decorator(decs, name="dispatch")
class TransactionCreateView(View):
    def get(self, request, *args, **kwargs):
         form = TransactionForm()
         return render(request,"transaction_add.html",{"form":form})
    
    def post(self, request, *args, **kwargs):
        form = TransactionForm(request.POST)
        if form.is_valid():
            # form.save()
            data = form.cleaned_data
            Transaction.objects.create(**data, user = request.user)
            messages.success(request, "transaction has been added successfully")

            return redirect("transaction-list")
        else:
            messages.error(request, "failed to add transaction")
            return render(request,"transaction_add.html",{"form":form})


#to View a single  transaction
#url:localhost:8000/<int:pk>/detail/
#get method
@method_decorator(decs, name="dispatch")
class TransactionDetailView(View):
    def get(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return redirect("signin")
        id = kwargs.get("pk")
        qs = Transaction.objects.get(id = id)
        return render(request, "transaction_detail.html", {"data":qs})
        
#to delete a single  transaction
#url:localhost:8000transactions/<int:pk>/remove/
#get method
@method_decorator(decs, name="dispatch")    
class TransactionDeleteView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        Transaction.objects.filter(id=id).delete()
        messages.success(request, "transaction has successfully been removed")
        return redirect("transaction-list")

    
    
#to update a single  transaction
#url:localhost:8000transactions/<int:pk>/change/
#get and post method 
    
@method_decorator(decs, name="dispatch")
class TransactionUpdateView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        transaction_object = Transaction.objects.get(id=id)
        form = TransactionForm(instance=transaction_object)
        return render(request, "transaction_update.html", {"form": form})
    def post(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        transaction_object = Transaction.objects.get(id=id)
        form = TransactionForm(request.POST, instance=transaction_object)
        if form.is_valid():
            form.save()
            messages.success(request, "transaction has successfully been updated")
            return redirect("transaction-list")
        else:
            return render(request, "transaction_update.html", {"form": form})


    
# signup
        

class SignupView(View):
    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return render(request, "signup.html", {"form":form})
    
    def post(self, request, *args, **kwargs):
        form  = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            print("record added")
            return redirect("signin")
        else:
            print("failed")
            return render(request, "signup.html", {"form":form})


class SignInView(View):
    def get(self, request, *args, **Kwargs):
        form = LoginForm()
        return render(request, "signin.html", {"form":form})
        
    def post(self, request, *args, **kwargs):
        form  = LoginForm(request.POST)
        if form.is_valid():
            u_name = form.cleaned_data.get("username")
            pwd = form.cleaned_data.get("password")
            user_auth = authenticate(request, username = u_name, password = pwd)
            if user_auth:
                login(request, user_auth)
                print("credentials is valid")
                return redirect("transaction-list")
        print("invalid credentials")
        return render(request, "signin.html", {"form":form})


#to signout
#url:localhost:8000transactions/signout/
#get method 

@method_decorator(decs, name="dispatch")
class SignoutView(View):
    def get(self, request, *args, **Kwargs):
        logout(request)
        messages.success(request, "You've logged out")
        return redirect("signin")

        


    
















