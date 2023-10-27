from typing import Any
from django import http
from django.shortcuts import render,redirect,get_object_or_404,get_list_or_404
from django.views import View
from .forms import UserRegistrationForm,UserLoginForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import Relation

# Create your views here.

class UserRegisterView(View):
    form_class=UserRegistrationForm
    template_name='account/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request):
        form=self.form_class()
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form=self.form_class(request.POST)
        if form.is_valid():
            cd= form.cleaned_data
            User.objects.create_user(cd['username'],cd['email'],cd['password1'])
            messages.success(request,' YOU REGISTED SUCCESSFULLY','success')
            return redirect('home:home')
        return render(request,self.template_name,{'form':form})
    
class UserLoginView(View):
    form_class=UserLoginForm
    template_name='account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next= request.GET.get('next')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request):
        form=self.form_class()
        return render(request,self.template_name,{'form':form})


    def post(self,request):
        form=self.form_class(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            user=authenticate(request,username=cd['username'],password=cd['password'])
            if user is not None:
                login(request,user)
                messages.success(request,'YOU LOGGED IN SUCCESSFULLY','success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request,'USERNAME OR PASSWORD ISS WRONG','warning')
        return render(request,self.template_name,{'form':form})    
           

class UserLogoutView(LoginRequiredMixin,View):
    def get(self,request):
        logout(request)
        messages.success(request,'YOU LOGOUT SECCESSFULLY','success')
        return redirect('home:home')


class UserProfileView(LoginRequiredMixin,View):
    template_name='account/profile.html'
    def get(self,request,user_id):
        #user_id=request.user.id
        is_following= False
        user= get_object_or_404(User,id=user_id)
        posts= user.posts.all()
        relation= Relation.objects.filter(from_user=request.user ,to_user=user)
        if relation.exists():
            is_following= True
        return render(request,self.template_name,{'user':user , 'posts':posts ,'is_following':is_following})
    

class UserPasswordResetView(auth_views.PasswordResetView):
    template_name= 'account/password_reset_from.html'
    success_url=  reverse_lazy('account:password_reset_done')
    email_template_name= 'account/password_reset_email.html'  


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name= 'account/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name= 'account/password_reset_confirm.html'
    success_url= reverse_lazy('account:password_reset_complete') 


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name= 'account/password_reset_complete.html'     


class UserFollowView(LoginRequiredMixin,View):   
    def get(self,request,user_id):
        user= User.objects.get(id=user_id)
        relation= Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request,'YOU ARE ALREADY FOLLOWIND THIS USER','danger')
        else:
            Relation(from_user=request.user ,to_user=user).save()
            messages.success(request,'YOU FOLLOWED THIS USER','success')
        return redirect('account:user_profile', user.id)           


class UserUnfollowView(LoginRequiredMixin,View):   
    def get(self,request,user_id):
        user= User.objects.get(id=user_id)
        relation= Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request,'YOU UNFOLLOWED THIS USER','success')
        else:
            messages.error(request,'YOU ARE NOT FOLLOWING THIS USER','danger')
        return redirect('account:user_profile', user.id)  