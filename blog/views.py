# from PIL.Image import Image
# from PIL import Image
import PIL as Image
from django.shortcuts import render

# Create your views here.
# def login(request):
#     return render(request, 'templates/blog/login.html')

from blog.models import User


# 未登录
def index_unlogin(request):
    return render(request, 'blog/index_unlogin1.html')


# 登录
def login(request):
    if request.method == 'POST':
        # 有值的时候赋值,没有取到的时候默认赋空值
        user_name = request.POST.get('username', '')
        pass_word = request.POST.get('password', '')
        user = User.objects.filter(username=user_name)
        if user:
            user = User.objects.filter(username=user_name)
            if pass_word == user.password:
                request.session['IS_LOGIN'] = True
                request.session['nickname'] = user.nickname
                request.session['username'] = user_name
                return render(request, 'blog/index.html', {'user': user})
            else:
                return render(request, "blog/login.html", {'error': "密码错误!"})
        else:
            return render(request, 'blog/login.html', {'error': '用户名不存在!'})
    else:
        return render(request, 'blog/login.html')


# 登录成功,返回首页
def login_success(request):
    return render(request, 'blog/index.html')


# 注册:没有注册成功,继续返回注册页面,成功返回未登录页面
def register(request):
    # pass
    if request.method == "POST":
        user_name = request.POST.get('username', '')
        pass_word_1 = request.POST.get('password_1', '')
        pass_word_2 = request.POST.get('password_2', '')
        nick_name = request.POST.get('nickname', '')
        email = request.POST.get('email', '')
        avatar = request.FILES.get('avatar')
        if User.objects.filter(username=user_name):
            return render(request, 'blog/register.html', {'error': '用户已存在'})
        if (pass_word_1 != pass_word_2):
            return render(request, 'blog/register.html', {'error': '两次密码输入不一致'})
        user = User()

        # 将头像设置为圆形
        if avatar:
            user.avatar = 'media/' + user_name + '.png'
            img = Image.open(avatar)
            size = img.size
            r2 = min(size[0], size(1))
            if size[0] != size[1]:
                img = img.resize((r2, r2), Image.ANTIALIAS)
            r3 = int(r2 / 2)
            img_circle = Image.new('RGBA', (r3 * 2, r3 * 2), (255, 255, 255, 0))
            pima = img.load()
            pimb = img_circle.load()
            r = float(r2 / 2)
            for i in range(r2):
                for j in range(r2):
                    lx = abs(i - r)
                    ly = abs(j - r)
                    l = (pow(lx, 2) + pow(ly, 2)) ** 0.5
                    if l < r3:
                        pimb[i - (r - r3), j - (r - r3)] = pima[i, j]
            img_circle.save('static/media/' + user_name + '.png')
        user.username = user_name
        user.password = pass_word_1
        user.email = email
        user.nickname = nick_name
        user.save()
        return render(request, 'blog/index_unlogin.html')
    else:
        return render(request, 'blog/register.html')


# 登录时忘记密码
def forget_password(request):
    if request.method == "POST":
        user_name = request.POST.get('username', '')
        email = request.POST.get('email', '')
        user = User.objects.filter(username=user_name)
        if user:
            user = User.objects.filter(username=user_name)
            if user.email == email:
                request.session['user_name'] = user_name
                return render(request, 'blog/reset.html')
            else:
                return render(request, 'blog/forget.html', {'error': '用户名和邮箱不匹配'})
        else:
            return render(request, 'blog/forget.html', {'error': '请输入正确的用户名'})
    else:
        return render(request, 'blog/forget.html')


# 重置密码
def reset_possword(request):
    if request.method == 'POST':
        user_name = request.session['user_name']
        pass_word_1 = request.POST.get('password_1', '')
        pass_word_2 = request.POST.get('password_2', '')
        user = User.objects.get(username=user_name)
        if pass_word_1 == pass_word_2:
            user.password = pass_word_1
            user.save()
            return render(request, 'blog/login.html')
        else:
            return render(request, 'blog/reset.html', {'error': '两次输入密码不一致!'})
    else:
        return render(request, 'blog/reset.html')
