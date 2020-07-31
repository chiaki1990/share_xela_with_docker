from django.test import TestCase, Client
from django.urls import reverse_lazy, reverse
#from config.settings.base import LOGIN_URL
from django.contrib.auth.models import User
from profiles.models import Profile
from profiles.forms  import ProfileForm
from allauth.account.models import EmailAddress
from config.tests.utils import *
from config.constants import TemplateName
from config.constants import ViewName


# Create your tests here.


class ProfileViewGetTest(TestCase):
    """テスト目的
    """
    """テスト対象
    profiles.views.py ProfileView#get
    endpoint: 'my_account/'
    name: 'profiles:profile'    
    """
    """テスト項目
    済 ユーザー認証されていないユーザーのアクセスにはログインページのリダイレクトが実行される
    済 ユーザー認証されていないユーザーのアクセスにはログインページのhtmlが表示される

    済 認証済みユーザーのアクセスであるが、Profileオブジェクトがない場合には'profiles/profile.html'が使用される
    済 認証済みユーザーのアクセスであるが、Profileオブジェクトがない場合にはcontextに"user_obj"キーが存在する
    済 認証済みユーザーのアクセスであるが、Profileオブジェクトがない場合にはcontextに"form"キーが存在する
    済 認証済みユーザーのアクセスであるが、Profileオブジェクトがない場合の"form"はProfileFormクラスである
    済 認証済みユーザーのアクセスであるが、Profileオブジェクトがない場合にはcontextに"profile_obj"キーが存在しない

    済 認証済みユーザーのアクセスの場合contextに"profile_obj"キーが存在する
    済 認証済みユーザーのアクセスの場合contextに"user_obj"キーが存在する
    済 認証済みユーザーのアクセスの場合contextに"form"キーが存在する
    済 認証済みユーザーかつスーパーユーザ以外のアクセスの場合contextに"email_obj"キーが存在する
    """

    def setUp(self):
        """テスト環境
        アクセスユーザーを生成する

        """        
        access_user_obj, access_user_profile_obj = create_user_for_test(create_user_data("access_user"))



    def test_ユーザー認証されていないユーザーのアクセスにはログインページのリダイレクトが実行される(self):
        expected_url = "/accounts/login/"

        self.client = Client()
        login_status = self.client.logout()
        self.assertFalse(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url=expected_url)


    def test_ユーザー認証されていないユーザーのアクセスにはログインページのhtmlが表示される(self):

        self.client = Client()
        login_status = self.client.logout()
        self.assertFalse(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='account/login.html')
        self.assertTemplateNotUsed(response, template_name='profiles/profile.html')


    def test_認証済みユーザーのアクセスであるが_Profileオブジェクトがない場合には_profiles_profile_html_が使用される(self):
        expected_template_name = 'profiles/profile.html'

        Profile.objects.get(user__username="access_user").delete()

        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTemplateUsed(response, template_name=expected_template_name)


    def test_認証済みユーザーのアクセスであるが_Profileオブジェクトがない場合にはcontextに_user_obj_キーが存在する(self):

        Profile.objects.get(user__username="access_user").delete()
        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("user_obj" in response.context)


    def test_認証済みユーザーのアクセスであるが_Profileオブジェクトがない場合にはcontextに_form_キーが存在する(self):

        Profile.objects.get(user__username="access_user").delete()
        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("form" in response.context)


    def test_認証済みユーザーのアクセスであるが_Profileオブジェクトがない場合の_form_はProfileFormクラスである(self):

        Profile.objects.get(user__username="access_user").delete()
        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(type(response.context["form"]), ProfileForm)


    def test_認証済みユーザーのアクセスであるが_Profileオブジェクトがない場合にはcontextにprofile_objキーが存在しない(self):

        Profile.objects.get(user__username="access_user").delete()
        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("profile_obj" not in response.context)


    def test_認証済みユーザーのアクセスの場合contextにprofile_objキーが存在する(self):

        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("profile_obj" in response.context)


    def test_認証済みユーザーのアクセスの場合contextにuser_objキーが存在する(self):

        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("user_obj" in response.context)


    def test_認証済みユーザーのアクセスの場合contextにformキーが存在する(self):

        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("form" in response.context)


    def test_認証済みユーザーかつスーパーユーザ以外のアクセスの場合contextにemail_objキーが存在する(self):

        self.client = Client()
        login_status = self.client.login(username="access_user", password=TestConstants.DEFAULT_PASSWOD)
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy('profiles:profile'), follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("email_obj" in response.context)



#class ProfileViewPostTest(TestCase): #patchで修正するべき?







