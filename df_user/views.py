from hashlib import sha1
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from . import models


def register(request):
    context = {
        'title': '天天生鲜-注册'
    }
    return render(request, 'df_user/register.html', context)


def register_exist(request):
    user_name = request.GET.get('user_name')
    count = models.UserInfo.objects.filter(user_name=user_name).count()

    return JsonResponse({'count': count})


def register_handle(request):
    # 接受用户信息
    post = request.POST
    user_name = post.get('user_name')
    user_pwd = post.get('pwd')
    user_cpwd = post.get('cpwd')
    user_email = post.get('email')

    if user_cpwd != user_pwd:
        return redirect('/user/register/')

    # 密码加密
    s = sha1()
    s.update(user_pwd.encode(encoding='utf-8'))
    user_pwd_sha1 = s.hexdigest()

    user = models.UserInfo()
    user.user_name = user_name
    user.user_pwd = user_pwd_sha1
    user.user_email = user_email

    user.save()

    # 注册成功， 转到登陆页面
    return redirect('/user/login/')


def login(request):
    user_name = request.COOKIES.get('user_name', '')
    context = {
        "title": '天天生鲜-登陆',
        'error_name': 0,
        'error_pwd': 0,
        'user_name': user_name,
    }
    return render(request, 'df_user/login.html', context)


def login_handle(request):
    post = request.POST
    user_name_input = post.get('username')
    user_pwd_input = post.get('pwd')
    remember_pwd_input = post.get('remember_pwd', 0)

    user_info = models.UserInfo.objects.filter(user_name=user_name_input)
    if len(user_info) == 1:
        s = sha1()
        s.update(user_pwd_input.encode(encoding='utf-8'))
        if s.hexdigest() == user_info[0].user_pwd:
            # 定义重定向
            red = HttpResponseRedirect('/user/user_info/')
            if remember_pwd_input:
                red.set_cookie('user_name', user_name_input)
            else:
                # 未记住用户名的情况下， 清除用户名，并将过期时间设置为立即过期
                red.set_cookie('user_name', '', max_age=-1)
            request.session['user_id'] = user_info[0].id
            request.session['user_name'] = user_name_input
            return red
        else:
            context = {
                'title': '天天生鲜-登陆',
                'error_name': 0,
                'error_pwd': 1,
                'user_name': user_name_input,
                'user_pwd': user_pwd_input,
            }
            return render(request, 'df_user/login.html', context)
    else:
        context = {
            'title': '天天生鲜-登陆',
            'error_name': 1,
            'error_pwd': 0,
            'user_name': user_name_input,
            'user_pwd': user_pwd_input,
        }
    return render(request, 'df_user/login.html', context)


def user_info(request):
    user_email = models.UserInfo.objects.get(id=request.session['user_id']).user_email
    user_addr = models.UserInfo.objects.get(id=request.session['user_id']).accepter_address
    context = {
        'title': '天天生鲜-用户中心',
        'user_name': request.session['user_name'],
        'user_email': user_email,
        'user_addr': user_addr,
    }
    return render(request, 'df_user/user_center_info.html', context)


def user_order(request):
    context = {
        'title': '用户中心',
    }
    return render(request, 'df_user/user_center_order.html', context)


def user_site(request):
    user = models.UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.accepter_name = post.get('accepter_name')
        user.accepter_address = post.get('accepter_address')
        user.accepter_postcode = post.get('accepter_postcode')
        user.accepter_phone_number = post.get('accepter_phone_number')
        user.save()
    context = {
        'title': '用户中心',
        'user': user,
        'accepter_name': '(%s 收)' % user.accepter_name if user.accepter_name != '' else '',
        'accepter_address': user.accepter_address,
        'accepter_postcode': user.accepter_postcode,
        'accepter_phone_number': user.accepter_phone_number,
        'accepter_name_blow': user.accepter_name,
    }
    return render(request, 'df_user/user_center_site.html', context)