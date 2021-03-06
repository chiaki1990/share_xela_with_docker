from django.test import TestCase, RequestFactory
from django.test.utils import setup_test_environment
from django.test import Client
from django.urls import reverse_lazy, reverse
from django.core.files import File
from django.contrib.auth.models import User
from items.forms import ItemModelForm
from items.models           import Item
from categories.models      import Category
from direct_messages.models import DirectMessage
from favorite.models        import Favorite
from profiles.models        import Profile
from solicitudes.models     import Solicitud
from config.tests.utils import *
from config.constants import ViewName
from config.constants import TemplateName
from config.constants import ContextKey
import json




class ItemDetailContextDMObjTest(TestCase):

    """テスト目的
    #item_detailでDirectMessageオブジェクトがあればcontextにdm_objを追加する

    """

    """テスト対象
    items.views.py ItemDetailView (items:item_detail)

    """

    """テスト項目

    済 認証されていないユーザーの場合にはcontext["dm_obj"]のキーが存在しない。
    済 認証されたユーザーがユーザーが出品者の場合でかつそのユーザーを含むDirectMessageオブジェクトが存在する場合にはcontextに"dm_obj"のキーをもつ
    済 認証されたユーザーがユーザーが出品者でない場合かつそのユーザーを含むDirectMessageオブジェクトが存在する場合にはcontextに"dm_obj"のキーをもつ
    済 認証されたユーザーを含まないDirectMessageオブジェクトが存在する場合にはcontextに"dm_obj"のキーを持たない

    """

    ITEM_DETAIL_URL_FORMAT = "/items/item/{}/"
    DM_OBJ = "dm_obj"

    def setUp(self):
        category_obj = Category.objects.create(number="Donar o vender")
        post_user_obj = User.objects.create_user(username="post_user", email="test_post_user@gmail.com", password='12345')
        post_user_profile_obj = Profile.objects.get(user=post_user_obj)

        access_user_obj = User.objects.create_user(username="access_user", email="test_access_user@gmail.com", password='12345')
        #access_user_profile_obj = Profile.objects.get(user=access_user_obj)

        solicitud_user_obj = User.objects.create_user(username="solicitud_user", email="test_solicitud_user@gmail.com", password='12345')
        solicitud_user_profile_obj = Profile.objects.get(user=solicitud_user_obj)

        item_obj1 =  Item.objects.create(user=post_user_obj, id=1, title="テストアイテム１", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")
        dm_obj = DirectMessage.objects.create( owner=post_user_profile_obj, participant=solicitud_user_profile_obj)
        item_obj1.direct_message = dm_obj
        item_obj1.save()

    def test_should_be_NO_KEY_for_AnonymousUser日本語でもテストは通る(self):
        #認証されていないユーザーに対するcontextのキー["dm_obj"]はない。

        url = self.ITEM_DETAIL_URL_FORMAT.format("1")

        self.client = Client()
        client_login_status = self.client.logout()
        self.assertFalse(client_login_status) #未認証状態でアクセス

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200) #status_codeが200
        self.assertTrue(self.DM_OBJ not in response.context) #AnonymousUserの場合にはキーが存在しない
        

    def test_should_be_DM_OBJ_KEY_for_post_user(self):
        #認証されたユーザーがユーザーが出品者の場合でかつDirectMessageが存在する場合にはcontextに"dm_obj"のキーをもつ

        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        self.client = Client()
        client_login_status = self.client.login(username="post_user", password='12345')
        self.assertTrue(client_login_status) #認証状態でアクセス

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200) #status_codeが200
        self.assertTrue(self.DM_OBJ in response.context) #キーが存在する。


    def test_should_be_DM_OBJ_KEY_for_access_user(self):
        #認証されたユーザーがユーザーが出品者でない場合かつDirectMessageが存在する場合にはcontextに"dm_obj"のキーをもつ

        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        self.client = Client()
        client_login_status = self.client.login(username="solicitud_user", password='12345')
        self.assertTrue(client_login_status) #認証状態でアクセス

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200) #status_codeが200
        self.assertTrue(self.DM_OBJ in response.context) # キーが存在する。

    def test_should_be_NO_KEY_for_AuthenticatedUser(self):
        #認証されたユーザーを含まないDirectMessageオブジェクトが存在する場合にはcontextに"dm_obj"のキーを持たない

        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        self.client = Client()
        client_login_status = self.client.login(username="access_user", password='12345')
        self.assertTrue(client_login_status) #認証状態でアクセス

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200) #status_codeが200
        self.assertTrue(self.DM_OBJ not in response.context) # 認証ユーザーでも、当該ユーザーがDirectMessageに含まれていなければキーは存在しない。





class ItemDetailContextBtnFavTest(TestCase):

    """テスト目的
    #item_detailでユーザー認証の状態によってbtn_favが適切に表示されることを担保したい

    """

    """テスト対象
    items.views.py ItemDetailView (items:item_detail)
    items.utils.py addBtnFavToContext

    """

    """テスト項目
    保留 item.favorite_usersに格納されるすべてのUserオブジェクトをusers: listに格納できている 
    保留 既にfavボタンを押しているユーザーのアクセスの場合fav_objはNoneではない。 
    保留 fav_obj.userはUserオブジェクトである
    済 未認証ユーザーの場合にはcontext["btn_fav"]の値が"NO_SHOW"である。 *4
    済 未認証ユーザーの場合にはcontext["fav_obj_id"]が存在しない。 *5
    済 アイテムにfavを押している認証ユーザーの場合にはcontext["btn_fav"]の値が"RED_HEART"である。 *3    
    済 アイテムにfavを押していない認証ユーザーの場合にはcontext["btn_fav"]の値が"WHITE_HEART"である。 *6

    """

    ITEM_DETAIL_URL_FORMAT = "/items/item/{}/"


    def setUp(self):
        """テスト環境

        Itemオブジェクト生成用のCategoryオブジェクト作成...category_obj
        Itemオブジェクトに対しFavボタンを押している役のユーザーを作成...fav_user
        Itemオブジェクトを作成した役のユーザーを作成...post_user
        Itemオブジェクト詳細ページにアクセスするユーザーを作成...access_user
        Itemオブジェクトを生成...item_obj1
        fav_userがFavボタンを押しitem_obj1.favorite_users.add()でfav_userが追加される。

        """

        category_obj = Category.objects.create(number="Donar o vender")
        fav_user = User.objects.create_user(username="fav_user", email="fav_test_user@gmail.com", password='12345')
        post_user = User.objects.create_user(username="post_user", email="test_post_user@gmail.com", password='12345')
        access_user = User.objects.create_user(username="access_user", email="test_access_user@gmail.com", password='12345')
        item_obj1 =  Item.objects.create(user=post_user, id=1, title="テストアイテム１", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")
        item_obj1.favorite_users.add(fav_user) 


    def test_should_be_NO_SHOW_for_anonymous_user(self):
        #未認証ユーザーの場合にはcontext["btn_fav"]の値が"NO_SHOW"である。 *4
       
        EXPECT = "NO_SHOW"        
        
        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        self.client = Client()
        login_status = self.client.logout()
        self.assertFalse(login_status) #未認証状態でアクセス
        response = self.client.get(url) 
        self.assertEqual(response.status_code, 200)
        self.assertTrue("btn_fav" in response.context)
        self.assertEqual(response.context["btn_fav"], EXPECT, "context['btn_fav']=='NO_SHOW'でなければならない。")


    def test_should_be_without_fav_obj_id_for_anonymous_user(self):
        #未認証ユーザーの場合にはcontext["fav_obj_id"]が存在しない。 *5
        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        self.client = Client()
        login_status = self.client.logout()
        self.assertFalse(login_status) #未認証状態でアクセス
        response = self.client.get(url) 
        self.assertEqual(response.status_code, 200)
        self.assertTrue("fav_obj_id" not in response.context)


    def test_should_be_RED_HEART_for_authenticated_user_with_fav(self):
        #認証されたユーザーかつ既にお気に入り済みユーザーに対するcontext["btn_fav"]の値は"RED_HEART"である *3

        EXPECT = "RED_HEART"
        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        self.client = Client()
        client_login = self.client.login(username="fav_user", password="12345")
        self.assertTrue(client_login) #認証状態でアクセス
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("btn_fav" in response.context)
        self.assertEqual(response.context["btn_fav"], EXPECT, "context['btn_fav']=='RED_HEART'でなければならない。")


    def test_should_be_WHITE_HEART_for_authenticated_user_without_fav(self):
        # アイテムにfavを押していない認証ユーザーの場合にはcontext["btn_fav"]の値が"WHITE_HEART"である。 *6
        EXPECT = "WHITE_HEART"

        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        self.client = Client()
        client_login = self.client.login(username="access_user", password="12345")
        self.assertTrue(client_login) #認証状態でアクセス
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("btn_fav" in response.context)
        self.assertEqual(response.context["btn_fav"], EXPECT)



class ItemListByFavorite(TestCase):
    """テスト目的
    認証されたユーザーのFavボタンが押されたItemのリストを表示する
    """
    """テスト対象
    items/views.py ItemListByFavoriteView
    endpoint: 'items/user/favorite/'
    name: 'items:item_list_by_favorite'    
    """
    """テスト項目
    未認証ユーザーによるアクセスの場合にはhomeにリダイレクトする *1
    認証されたユーザーのアクセスの場合はItem.favorite_usersに認証されたユーザーオブジェクトが含まれるものだけを表示する *2
    """

    def setUp(self):
        """テスト環境
        検証対象のユーザー(fav_user)がFavボタンを押したアイテムを以下のものとする。
        item_obj1
        item_obj2
        item_obj5
        """
        category_obj = Category.objects.create(number="Donar o vender")
        fav_user = User.objects.create_user(username="fav_user", email="fav_test_user@gmail.com", password='12345')
        post_user = User.objects.create_user(username="post_user", email="test_post_user@gmail.com", password='12345')
        access_user = User.objects.create_user(username="access_user", email="test_access_user@gmail.com", password='12345')
        item_obj1 = Item.objects.create(user=post_user, id=1, title="テスト1", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")
        item_obj1.favorite_users.add(fav_user)

        item_obj2 = Item.objects.create(user=post_user, id=2, title="テスト2", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")
        item_obj2.favorite_users.add(fav_user)

        item_obj3 = Item.objects.create(user=post_user, id=3, title="テスト3", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")

        item_obj4 = Item.objects.create(user=post_user, id=4, title="テスト4", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")

        item_obj5 = Item.objects.create(user=post_user, id=5, title="テスト5", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")
        item_obj5.favorite_users.add(fav_user)



    def test_should_be_list_of_1_2_5(self):
        # 未認証ユーザーによるアクセスの場合にはhomeにリダイレクトする *1
        # 認証されたユーザーのアクセスの場合はItem.favorite_usersに認証されたユーザーオブジェクトが含まれるものだけを表示する *2

        self.client = Client()
        login_status = self.client.logout()
        self.assertFalse(login_status) #未ログイン状態でアクセス 
        response = self.client.get(reverse('items:item_list_by_favorite'), follow=True)
        #response = self.client.get(reverse('items:item_list_by_favorite'), follow=True)
        #response = self.client.get(reverse(ViewName.ITEM_LIST_BY_FAVORITE), follow=True)
        templates = [ele.name for ele in response.templates]
        self.assertTrue(TemplateName.HOME in templates) #*1

        self.client = Client()
        login_status = self.client.login(username="fav_user", password="12345")
        self.assertTrue(login_status) #ログイン状態でアクセス

        response = self.client.get(reverse_lazy(ViewName.ITEM_LIST_BY_FAVORITE), follow=True)
        item_objects = response.context[ContextKey.ITEM_OBJECTS]
        self.assertTrue(item_objects.count(), 3)
        self.assertTrue(Item.objects.get(id=1) in item_objects)
        self.assertTrue(Item.objects.get(id=2) in item_objects)
        self.assertTrue(Item.objects.get(id=3) not in item_objects)         
        self.assertTrue(Item.objects.get(id=4) not in item_objects)
        self.assertTrue(Item.objects.get(id=5) in item_objects) #*2





class ItemFavoriteViewTest(TestCase):

    """テスト目的
    FavBtnを押したらItem.favorite_usersにUserオブジェクトが追加されるかまたは削除される動作の信頼性を担保する

    """

    """テスト対象
    items.views.py ItemFavoriteView (items:item_detail)
    endpoint: 'items/item/<int:pk>/favorite/' , ViewName.ITEM_FAVORITE
    name: 'items:item_favorite'


    """

    """テスト項目
    済 favボタンを押していないユーザーによるfavボタンを押すことでitem.favorite_usersに含まれる要素が1つ増加する *1
    済 favボタンを押していないユーザーによるfavボタンを押すことでitem.favorite_usersに当該ユーザーが追加される *2 
    """

    def setUp(self):
        """テスト環境

        Itemオブジェクト生成用のCategoryオブジェクト作成...category_obj
        Itemオブジェクトに対しFavボタンを押している役のユーザーを作成...fav_user
        Itemオブジェクトを作成した役のユーザーを作成...post_user
        Itemオブジェクト詳細ページにアクセスするユーザーを作成...access_user
        Itemオブジェクトを生成...item_obj1
        fav_userがFavボタンを押しitem_obj1.favorite_users.add()でfav_userが追加される。

        """

        category_obj = Category.objects.create(number="Donar o vender")
        fav_user = User.objects.create_user(username="fav_user", email="fav_test_user@gmail.com", password='12345')
        #fav_user.set_password('12345')
        #fav_user.save()
        post_user = User.objects.create_user(username="post_user", email="test_post_user@gmail.com", password='12345')
        #post_user.set_password('12345') #, password='top_secret'
        #post_user.save()
        access_user = User.objects.create_user(username="access_user", email="test_access_user@gmail.com", password='12345')
        #access_user.set_password('12345')
        #access_user.save()
        item_obj1 =  Item.objects.create(user=post_user, id=1, title="テストアイテム１", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")
        item_obj1.favorite_users.add(fav_user)

    def test_should_add_user_by_push_fab_btn_for_no_fav_user(self):
        # favボタンを押していないユーザーによるfavボタンを押すことでitem.favorite_usersに含まれる要素が1つ増加する *1
        # favボタンを押していないユーザーによるfavボタンを押すことでitem.favorite_usersに当該ユーザーが追加される *2 

        item_obj = Item.objects.get(id=1)
        self.client = Client()
        login_status = self.client.login(username="access_user", password="12345")
        self.assertTrue(login_status)

        #アクセス前
        response = self.client.get(reverse_lazy(ViewName.ITEM_DETAIL, args=("1",)))
        self.assertTrue("item_obj" in response.context)
        item_obj = response.context["item_obj"]
        self.assertTrue(item_obj.favorite_users.all().count(), 1)

        #Favボタンを押す
        access_user = User.objects.get(username="access_user")
        response = self.client.post(reverse_lazy(ViewName.ITEM_FAVORITE, args="1"), follow=True)
        templates = [ele.name for ele in response.templates]
        #print(templates)
        item_obj = Item.objects.get(id=1)
        self.assertTrue(item_obj.favorite_users.all().count(), 2) # *1
        self.assertTrue(access_user in item_obj.favorite_users.all()) # *2




class ItemDetailTemplatesTest(TestCase):

    """テスト目的
    #ItemDetailViewに使用されるtemplateが正しく使用されているかチェックする

    """

    """テスト対象
    items.views.py ItemDetailView (items:item_detail)

    """

    """テスト項目
    済 未認証ユーザーがアイテム詳細ページにアクセスした場合には使用されるテンプレートは['items/detail_item2.html', 'config/base.html', 'config/include/navbar.html', 'config/include/bottom.html']
    済 アイテム詳細ページの作成者である認証したユーザーがアイテム詳細ページにアクセスした場合には使用されるテンプレートは['items/detail_item2.html', 'config/base.html', 'config/include/navbar.html', 'config/include/bottom.html']
    済 アイテム詳細ページの作成者ではない認証したユーザーがアイテム詳細ページにアクセスした場合には使用されるテンプレートは['items/detail_item2.html', 'config/base.html', 'config/include/navbar.html', 'config/include/bottom.html']
    """

    ITEM_DETAIL_URL_FORMAT = "/items/item/{}/"


    def setUp(self):
        category_obj = Category.objects.create(number="Donar o vender")
        post_user_obj = User.objects.create_user(username="post_user", email="test_post_user@gmail.com", password='12345')
        post_user_profile_obj = Profile.objects.get(user=post_user_obj)

        access_user_obj = User.objects.create_user(username="access_user", email="test_access_user@gmail.com", password='12345')
        #access_user_profile_obj = Profile.objects.get(user=access_user_obj)

        solicitud_user_obj = User.objects.create_user(username="solicitud_user", email="test_solicitud_user@gmail.com", password='12345')
        solicitud_user_profile_obj = Profile.objects.get(user=solicitud_user_obj)

        item_obj1 =  Item.objects.create(user=post_user_obj, id=1, title="テストアイテム１", description="説明です。", category=category_obj, adm0="huh", adm1="cmks", adm2="dks")
        dm_obj = DirectMessage.objects.create( owner=post_user_profile_obj, participant=solicitud_user_profile_obj)
        item_obj1.direct_message = dm_obj
        item_obj1.save()

    def test_templates_by_anonymous_user(self):
        """
        未認証ユーザーがアイテム詳細ページにアクセスした場合には使用されるテンプレートは、
        ['items/detail_item2.html', 'config/base.html', 'config/include/navbar.html', 'config/include/bottom.html']
        """
        self.client = Client()
        login_status = self.client.logout()
        self.assertFalse(login_status)  #未認証でアクセス
        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        response = self.client.get(url)
 
        templates = [ele.name for ele in response.templates]

        self.assertTrue('items/detail_item2.html' in templates)
        self.assertTrue('config/base.html' in templates)
        self.assertTrue('config/include/navbar.html' in templates)
        self.assertTrue('config/include/general/bottom_with_vuetify.html' in templates) 



    def test_templates_by_authentication_and_post_user(self):
        """
        アイテム詳細ページの作成者である認証したユーザーがアイテム詳細ページにアクセスした場合には使用されるテンプレートは、
        ['items/detail_item2.html', 'config/base.html', 'config/include/navbar.html', 'config/include/bottom.html']
        """
        self.client = Client()
        login_status = self.client.login(username="post_user", password='12345')
        self.assertTrue(login_status)  #認証状態でアクセス
        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        response = self.client.get(url)
 
        templates = [ele.name for ele in response.templates]

        self.assertTrue('items/detail_item2.html' in templates)
        self.assertTrue('config/base.html' in templates)
        self.assertTrue('config/include/navbar.html' in templates)
        self.assertTrue('config/include/general/bottom_with_vuetify.html' in templates)


    def test_templates_by_authentication_no_post_user(self):
        """
        アイテム詳細ページの作成者ではない認証したユーザーがアイテム詳細ページにアクセスした場合には使用されるテンプレートは
        ['items/detail_item2.html', 'config/base.html', 'config/include/navbar.html', 'config/include/bottom.html'] 
        """
        self.client = Client()
        login_status = self.client.login(username="access_user", password='12345')
        self.assertTrue(login_status)  #認証状態でアクセス
        url = self.ITEM_DETAIL_URL_FORMAT.format("1")
        response = self.client.get(url)
 
        templates = [ele.name for ele in response.templates]

        self.assertTrue('items/detail_item2.html' in templates)
        self.assertTrue('config/base.html' in templates)
        self.assertTrue('config/include/navbar.html' in templates)
        self.assertTrue('config/include/general/bottom_with_vuetify.html' in templates)

 
   

class ItemCreateViewKaizenPOSTTest(TestCase):
    """テスト目的
    一定の条件下でのみItemオブジェクトが生成されないように制限する
    """
    """テスト対象
    items/views.py ItemCreateview#POST
    endpoint:"items/'create2/"
    name: "items:item_create"
    """
    """テスト項目
    済 category_title_description_adm0_adm1_adm2のデータが有ればItemオブジェクトが生成される
    済 test_categoryデータが不足している場合はFormがinvalidつまりFalseになる
    済 test_categoryデータが不足している場合はItemオブジェクトが作られない
    済 priceデータが不足している場合にはformはinvalidになってしまう
    済 画像データが添付されずに生成されたItemオブジェクトの画像urlはimages_default_images_pngである
    """

    """テストメモ
    ModelFormにModelChiceFieldを実装している。
    このModelChoiceFieldにForeignKeyのオブジェクトを格納するときには
    オブジェクトそのものを渡すのではなくオブジェクト.idで渡すことが必須となる。
    """

    def setUp(self):
        category_obj = Category.objects.create(number="1")
        post_user_obj = User.objects.create_user(username="post_user", email="test_post_user@gmail.com", password='12345')
        self.init_data = {}



    def test_category_title_description_adm0_adm1_adm2_priceのデータが有ればItemオブジェクトが生成される(self):
        post_user_obj = User.objects.get(username="post_user")
        profile_obj = Profile.objects.get(user=post_user_obj)
        item_objects_count_before = Item.objects.filter(user=post_user_obj).count()
        category_obj = Category.objects.get(number="1")
        data = {
                'category':category_obj.id, 
                'title':"テスト", 
                'description':"hdahfifif",
                "price":0,
                'adm0':"GUATEMALA",
                'adm1':"Guatemala",
                'adm2':"Guatemala"
                } 
                #'image1':"nin.jpg", 'image2': None, 'image3': None}
        #files = {'image1':mock.MagicMock(spec=File), 'image2': mock.MagicMock(spec=File), 'image3': mock.MagicMock(spec=File)}
        
        form = ItemModelForm(data) #, files
        self.assertTrue(form.is_valid() == True)


        self.client = Client()
        login_status = self.client.login(username="post_user", password="12345")
        self.assertTrue(login_status)
        response = self.client.post(reverse(ViewName.ITEM_CREATE), data)
        self.assertEqual(response.status_code, 200)
        item_objects_count_after = Item.objects.filter(user=post_user_obj).count()
        self.assertEqual(item_objects_count_before+1, item_objects_count_after) 


    
    def test_categoryデータが不足している場合はFormがinvalidつまりFalseになる(self):

        data = { 
                'title':"テスト", 
                'description':"hdahfifif", 
                'adm0':"GUATEMALA", 'adm1':"Guatemala",'adm2':"Guatemala", "price":1000
                }

                #'image1':'nini.jpg', 'image2': 'nnin.jpg', 'image3': 'ninli.jpg'
                
        #files = {'image1':mock.MagicMock(spec=File), 'image2': mock.MagicMock(spec=File), 'image3': mock.MagicMock(spec=File)}
        form = ItemModelForm(data)
        self.assertFalse(form.is_valid())



    def test_categoryデータが不足している場合はItemオブジェクトが作られない(self):
        post_user_obj = User.objects.get(username="post_user")
        item_objects_count_before = Item.objects.filter(user=post_user_obj).count()
        data = {
                'title':"テスト", 
                'description':"hdahfifif", 
                'adm0':"GUATEMALA", 'adm1':"Guatemala",'adm2':"Guatemala", "price":1999
                }

        self.client = Client()
        login_status = self.client.login(username="post_user", password="12345")
        self.assertTrue(login_status)
        #response = self.client.post(reverse("items:item_create"), data)
        response = self.client.post(reverse(ViewName.ITEM_CREATE), data)
        self.assertEqual(response.status_code, 200)
        item_objects_count_after = Item.objects.filter(user=post_user_obj).count()
        self.assertEqual(item_objects_count_before, item_objects_count_after) 



    def test_priceデータが不足している場合にはformはinvalidになってしまう(self):

        category_obj = Category.objects.get(number="1")
        data = {
        'category': category_obj.id, 
        'title':"テスト", 
        'description':"hdahfifif", 
        'adm0':"GUATEMALA", 'adm1':"Guatemala",'adm2':"Guatemala"
        }

                
        #files = {'image1':mock.MagicMock(spec=File), 'image2': mock.MagicMock(spec=File), 'image3': mock.MagicMock(spec=File)}
        form = ItemModelForm(data)
        self.assertFalse(form.is_valid())



    
    def test_画像データが添付されずに生成されたItemオブジェクトの画像urlはimages_default_item_pngである(self):
        
        post_user_obj = User.objects.get(username="post_user")
        item_objects_count_before = Item.objects.filter(user=post_user_obj).count()
        self.assertEqual(item_objects_count_before, 0)
        category_obj = Category.objects.get(number="1")
        data = {
                'category':category_obj.id, 
                'title':"テスト", 
                'description':"hdahfifif", 
                'adm0':"GUATEMALA", 'adm1':"Guatemala",'adm2':"Guatemala","price":0
                }       
        
        form = ItemModelForm(data)
        self.assertTrue(form.is_valid() )

        self.client = Client()
        login_status = self.client.login(username="post_user", password="12345")
        self.assertTrue(login_status)
        response = self.client.post(reverse(ViewName.ITEM_CREATE), data)
        self.assertEqual(response.status_code, 200)
        item_obj = Item.objects.get(user=post_user_obj)
        self.assertEqual(item_obj.image1, "images/default_item.png")  






class ItemCreateEditTemplateTest(TestCase):
    """テスト目的
    ItemCreateとItemEditでは同一のテンプレートが使用される。しかし表示される内容が変わる部分がある。
    Viewごとに表示内容が適切に表示されているかをテストする
    """
    """テスト対象
    items/views.py ItemCreateview#GET
    endpoint:"items/create2/"
    name: "items:item_create"


    items/views.py ItemEditview#GET
    endpoint:"items/<int:pk>/edit/"
    name: "items:item_edit"
    """
    """テスト項目
    ItemCreateview経由の表示の場合formタグのactionの値はitems_create2である
    ItemEditview経由の表示の場合formタグのactionの値はitems_<int:pk>_editである
    """



    def test_ItemCreateview経由の表示の場合formタグのactionの値はitems_create2である(self):
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy(ViewName.ITEM_CREATE))
        self.assertContains( response, 'action="/items/create2/"', status_code=200 )
        self.assertNotContains( response, '/edit/', status_code=200 )



    def test_ItemEditView経由の表示の場合formタグのactionの値にはeditが含まれる(self):
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)))
        self.assertNotContains( response, 'action="/items/create2/"', status_code=200 )
        self.assertContains( response, '/edit/', status_code=200 )






class ItemEditViewPOSTTest(TestCase):
    """テスト目的
    一定の条件下でのみItemオブジェクトが変更されることを担保する
    """
    """テスト対象
    items/views.py ItemEditview#POST
    endpoint:"items/<int:pk>/edit/"
    name: "items:item_edit"
    """
    """テスト項目
    変更した場合新たにItemインスタンスが生成されることはない。
    価格の変更を実行したときに編集後の記事は価格が変更されている。
    記事詳細を変更したら編集後の記事の詳細が変更される。
    記事タイトルを変更したら編集後の記事のタイトルが変更される
    記事のadm1(departamento値)をguatemalaに変更するデータを送信するとguatemalaに変更される
    記事のadm2(municipio値)をOlintepequeに変更するデータを送信するとOlintepequeに変更される
    記事のpoint値を更新したらpoint値が更新されている。
    記事のカテゴリを変更したら編集記事のカテゴリが更新されている
    記事編集のデータに不適切なデータが有る場合にはリダイレクト(302)のステータスコードが使われる
    """

    #def setUp(self):
    #    category_obj = Category.objects.create(number="1")
    #    post_user_obj = User.objects.create_user(username="post_user", email="test_post_user@gmail.com", password='12345')

    def test_変更した場合新たにItemインスタンスが生成されることはない(self):
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 0)
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        #Itemオブジェクトの編集
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        data = create_item_data(category_obj)
        data["price"] = 1000
        response = self.client.post(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)), data)
        self.assertEqual(response.status_code, 200)
        item_count = Item.objects.all().count()
        #編集しただけなのでItemインスタンスは増えることはない。
        self.assertEqual(item_count, 1)

    def test_価格の変更を実行したときに編集後の記事は価格が変更されている(self):
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        #初期値のpriceをチェックする
        self.assertEqual(item_obj.price, 900)
        #item_objのpriceを1500に変更する
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        data = create_item_data(category_obj)
        data["price"] = 1500
        response = self.client.post(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)), data)
        # item_objのprice値をチェックする
        item_obj = Item.objects.get(id=item_obj.id)
        self.assertEqual(item_obj.price, 1500)

    def test_記事詳細を変更したら編集後の記事の詳細が変更される(self):
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        #初期値のdescriptionをチェックする
        self.assertEqual(item_obj.description, "テストアイテム1の説明") #デフォルト値: テストアイテム1の説明
        #item_objのdescriptionを"editted"に変更する
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        data = create_item_data(category_obj)
        data["description"] = "editted"
        response = self.client.post(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)), data)
        # item_objのprice値をチェックする
        item_obj = Item.objects.get(id=item_obj.id)
        self.assertEqual(item_obj.description, "editted")  

    def test_記事タイトルを変更したら編集後の記事のタイトルが変更される(self):
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        #初期値のtitleをチェックする
        self.assertEqual(item_obj.title, "テストアイテム0") #デフォルト値: テストアイテム0
        #item_objのtitleを"変更後のタイトル"に変更する
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        data = create_item_data(category_obj)
        data["title"] = "変更後のタイトル"
        response = self.client.post(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)), data)
        # item_objのtitle値をチェックする
        item_obj = Item.objects.get(id=item_obj.id)
        self.assertEqual(item_obj.title, "変更後のタイトル")        
  

    def test_記事のdepartamento値をguatemalaに変更するデータを送信するとguatemalaに変更される(self): 
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        #初期値のdepartamentoをチェックする
        self.assertEqual(item_obj.adm1, "Quetzaltenango") #デフォルト値: Quetzaltenango
        #item_objのdescriptionを"editted"に変更する
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        data = create_item_data(category_obj)
        data["adm1"] = "Guatemala"
        response = self.client.post(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)), data)
        # item_objのprice値をチェックする
        item_obj = Item.objects.get(id=item_obj.id)
        self.assertEqual(item_obj.adm1, "Guatemala")  


    def test_記事のmunicipio値をOlintepequeに変更するデータを送信するとOlintepequeに変更される(self): 
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        #初期値のdepartamentoをチェックする
        self.assertEqual(item_obj.adm2, "Quetzaltenango") #デフォルト値: Quetzaltenango
        #item_objのdescriptionを"editted"に変更する
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        data = create_item_data(category_obj)
        data["adm2"] = "Olintepeque"
        response = self.client.post(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)), data)
        # item_objのprice値をチェックする
        item_obj = Item.objects.get(id=item_obj.id)
        self.assertEqual(item_obj.adm2, "Olintepeque")


    def test_記事のカテゴリを変更したら編集記事のカテゴリが更新されている(self):  
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        #初期値のcategoryをチェックする
        self.assertEqual(item_obj.category.number, "10") #デフォルト値:  10 
        #item_objのcategoryを変更する
        changed_category = Category.objects.all().first()
        changed_category_id = changed_category.id
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        data = create_item_data(category_obj)
        data["category"] = changed_category_id
        response = self.client.post(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)), data)
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.status_code, 302)
        # item_objのprice値をチェックする
        item_obj = Item.objects.get(id=item_obj.id)
        self.assertEqual(item_obj.category.number, changed_category.number)


    def test_記事編集のデータに不適切なデータが有る場合にはリダイレクト302のステータスコードが使われる(self):
        """
        カテゴリーの変更の際に適切なデータはcategoryオブジェクトのidをが使用される。
        したがってカテゴリーobjectのアトリビュートであるnumberや他の文字列を使った場合にはエラーが生じる。
        この点を利用して意図的に不適切なデータを作成しリダイレクトが行われるかテストする
        """
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        #初期値のcategoryをチェックする
        self.assertEqual(item_obj.category.number, "10") #デフォルト値:  10 
        #item_objのcategoryを変更する
        changed_category = "不適切な値"
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        data = create_item_data(category_obj)
        data["category"] = changed_category
        response = self.client.post(reverse_lazy(ViewName.ITEM_EDIT, args=(str(item_obj.id),)), data)






class ItemDeactivateViewTest(TestCase):
    """テスト目的
    Itemオブジェクトのactiveアトリビュートのapiを通じた変更操作が担保される
    """
    """テスト対象
    items/views.py ItemDeactivateView#GET, #POST
    endpoint:"items/<int:pk>/delete/"
    name: "items:item_deactivate"
    """
    """テスト項目
    getメソッドでendpointにアクセスすると記事を非アクティブにすることを確認するテンプレートが表示される
    postメソッドでendpointにアクセスすると記事を非アクティブにすることができる
    postメソッドでendpointにアクセスすると記事を消しましたってテンプレートが表示される

    """


    def test_getメソッドでendpointにアクセスすると記事を非アクティブにすることを確認するテンプレートが表示される(self):
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 0)
        #Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        # deactivateにするページを表示する
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy(ViewName.ITEM_DEACTIVATE, args=(str(item_obj.id),)))
        self.assertEqual(response.status_code, 200)
        #表示されるテンプレートの一部に TemplateName.ITEM_DEACTIVATE_CONFIRMが含まれる
        templates = [ele.name for ele in response.templates]
        self.assertTrue(TemplateName.ITEM_DEACTIVATE_CONFIRM in templates)



    def test_postメソッドでendpointにアクセスすると記事を非アクティブにすることができる(self):
        # Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        self.assertEqual(item_obj.active, True)
        # deactivateにする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        response = self.client.post(reverse_lazy(ViewName.ITEM_DEACTIVATE, args=(str(item_obj.id),)))
        self.assertEqual(response.status_code, 200)
        # activeアトリビュートがFalseに変更されたかチェック
        after_item_obj = Item.objects.get(id=item_obj.id)
        self.assertEqual(after_item_obj.active, False)



    def test_postメソッドでendpointにアクセスすると記事を消しましたってテンプレートが表示される(self):
        # Itemオブジェクト作成
        category_obj = pickUp_category_obj_for_test()
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_count = Item.objects.all().count()
        self.assertEqual(item_count, 1)
        self.assertEqual(item_obj.active, True)
        # deactivateにする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        response = self.client.post(reverse_lazy(ViewName.ITEM_DEACTIVATE, args=(str(item_obj.id),)))
        self.assertEqual(response.status_code, 200)
        #表示されるテンプレートの一部に TemplateName.ITEM_DEACTIVATEDが含まれる
        templates = [ele.name for ele in response.templates]
        self.assertTrue(TemplateName.ITEM_DEACTIVATED in templates)       





class ItemUserListViewTest(TestCase):
    """テスト目的
    Itemオブジェクトのactive属性がTrueのみ表示されることを担保する
    """
    """テスト対象
    items/views.py ItemUserListView#GET
    endpoint: "items/list_u/"
    name: "items:itemuser_list"
    """
    """テスト項目
    表示される記事にはactiveがFalseのものは存在しない
    関連しないユーザーの記事が含まれずに記事を一覧する
    contextにプロフィールデータが含まれる
    contextにプロフィール詳細が含まれる
    返されるテンプレートには"items/item_user_list/list.html"が含まれる
    記事の個数が0この場合には"no_item.html"が使われる
    """

    def test_表示される記事にはactiveがFalseのものは存在しない(self):
        # ユーザーが記事を5コ作成する。そのうち2個はactiveをFalseに設定する
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        category_obj = pickUp_category_obj_for_test()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.active = False
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.active = False
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))

        # 記事にアクセスする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        # セッションにユーザーのオブジェクトを追加する
        session = self.client.session
        session['user_obj'] = user_obj
        session.save()
        response = self.client.get(reverse_lazy(ViewName.ITEM_USER_LIST))
        # 返されるコンテンツの個数を確認
        item_objects = response.context[ ContextKey.ITEM_OBJECTS ]
        self.assertEqual(item_objects.count(), 3)
        # 返されるコンテンツのactive属性値がTrueかチェック
        for obj in response.context[ContextKey.ITEM_OBJECTS]:
            self.assertEqual(obj.active, True)



    def test_関連しないユーザーの記事が含まれずに記事を一覧する(self):
        # ユーザーが記事を5コ作成する。そのうち2個はactiveをFalseに設定する
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        category_obj = pickUp_category_obj_for_test()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.active = False
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.active = False
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        # 関係ないユーザーが記事を３個作成する
        other_user_obj, other_profile_obj = create_user_for_test(create_user_data("other1"))
        item_obj = create_item_for_test(other_user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(other_user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(other_user_obj, create_item_data(category_obj))
        # 記事にアクセスする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        # セッションにユーザーのオブジェクトを追加する
        session = self.client.session
        session['user_obj'] = user_obj
        session.save()
        response = self.client.get(reverse_lazy(ViewName.ITEM_USER_LIST))
        # 返されるコンテンツがすべてユーザーに関するものか確認
        item_objects = response.context[ ContextKey.ITEM_OBJECTS ]
        for item_obj in item_objects:
            self.assertEqual(item_obj.user, user_obj)
        # 返されるコンテンツの個数を確認
        self.assertEqual(item_objects.count(), 3)


    def test_contextにプロフィールデータが含まれる(self):
        # ユーザーが記事を5コ作成する。そのうち2個はactiveをFalseに設定する
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        category_obj = pickUp_category_obj_for_test()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.active = False
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.active = False
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))

        # 記事にアクセスする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        # セッションにユーザーのオブジェクトを追加する
        session = self.client.session
        session['user_obj'] = user_obj
        session.save()
        response = self.client.get(reverse_lazy(ViewName.ITEM_USER_LIST))
        # contextにユーザーのProfileオブジェクトが含まれる
        profile_in_context = response.context["profile_obj"]
        self.assertEqual(profile_in_context, profile_obj)
              

    def test_contextにプロフィール詳細が含まれる(self):
        # ユーザーが記事を5コ作成する。そのうち2個はactiveをFalseに設定する
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        category_obj = pickUp_category_obj_for_test()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.active = False
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.active = False
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))

        # 記事にアクセスする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        # セッションにユーザーのオブジェクトを追加する
        session = self.client.session
        session['user_obj'] = user_obj
        session.save()
        response = self.client.get(reverse_lazy(ViewName.ITEM_USER_LIST))
        # contextにユーザーのProfileオブジェクトが含まれる
        profile_description_in_context = response.context["json_prodifle_description"]
        self.assertEqual(profile_description_in_context, json.dumps(profile_obj.description)) 


    def test_返されるテンプレートにはitems_item_user_list_list_htmlが含まれる(self):
        # ユーザーが記事を5コ作成する。
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        category_obj = pickUp_category_obj_for_test()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))

        # 記事にアクセスする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        # セッションにユーザーのオブジェクトを追加する
        session = self.client.session
        session['user_obj'] = user_obj
        session.save()
        response = self.client.get(reverse_lazy(ViewName.ITEM_USER_LIST))
        # templateのチェック
        templates = [template.name for template in response.templates]
        self.assertTrue(TemplateName.USER_ITEM_LIST in templates)


    def test_記事の個数が0この場合にはno_item_htmlが使われる(self):
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        # 記事にアクセスする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        # セッションにユーザーのオブジェクトを追加する
        session = self.client.session
        session['user_obj'] = user_obj
        session.save()
        response = self.client.get(reverse_lazy(ViewName.ITEM_USER_LIST))
        # templateのチェック
        templates = [template.name for template in response.templates]
        self.assertTrue(TemplateName.NO_ITEMS in templates)



class ItemCategoryListViewTest(TestCase):
    """テスト目的
    カテゴリーに応じて国全体における記事が表示される状態を担保する
    """
    """テスト対象
    items/views.py ItemUserListView#GET
    endpoint: 'items/category/<int:pk>/items/list/'
    name: "items:ItemCategoryListView"
    """
    """テスト項目
    特定のカテゴリーを指定すると表示される記事は当該カテゴリーの記事である
    """
    def test_特定のカテゴリーを指定すると表示される記事は当該カテゴリーの記事である(self):
        # ユーザーが記事を8コ作成する。
        user_obj, profile_obj = create_user_for_test(create_user_data("test1"))
        category_obj = pickUp_category_obj_for_test()
        cate1 = Category.objects.get(number="1")
        cate2 = Category.objects.get(number="2")
        cate3 = Category.objects.get(number="3")
        cate4 = Category.objects.get(number="4")
        cate5 = Category.objects.get(number="5")
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.category = cate1
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.category = cate2
        item_obj.save()        
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.category = cate3
        item_obj.save()         
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))
        item_obj.category = cate4
        item_obj.save()         
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))        
        item_obj.category = cate5
        item_obj.save()
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))        
        item_obj.category = cate5
        item_obj.save()  
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))        
        item_obj.category = cate5
        item_obj.save()  
        item_obj = create_item_for_test(user_obj, create_item_data(category_obj))        
        item_obj.category = cate5
        item_obj.save()
        # 記事にアクセスする
        self.client = Client()
        login_status = self.client.login(username="test1", password="1234tweet")
        self.assertTrue(login_status)
        response = self.client.get(reverse_lazy(ViewName.ITEM_CATEGORY_LIST, args=("1",)))
        # 表示される記事のチェック
        item_objects = response.context[ContextKey.ITEM_OBJECTS]
        for obj in item_objects:
            self.assertEqual(obj.category.number, "1")

        response = self.client.get(reverse_lazy(ViewName.ITEM_CATEGORY_LIST, args=("2",)))
        # 表示される記事のチェック
        item_objects = response.context[ContextKey.ITEM_OBJECTS]
        for obj in item_objects:
            self.assertEqual(obj.category.number, "2")

        response = self.client.get(reverse_lazy(ViewName.ITEM_CATEGORY_LIST, args=("3",)))
        # 表示される記事のチェック
        item_objects = response.context[ContextKey.ITEM_OBJECTS]
        for obj in item_objects:
            self.assertEqual(obj.category.number, "3")

        response = self.client.get(reverse_lazy(ViewName.ITEM_CATEGORY_LIST, args=("4",)))
        # 表示される記事のチェック
        item_objects = response.context[ContextKey.ITEM_OBJECTS]
        for obj in item_objects:
            self.assertEqual(obj.category.number, "4")

        response = self.client.get(reverse_lazy(ViewName.ITEM_CATEGORY_LIST, args=("5",)))
        # 表示される記事のチェック
        item_objects = response.context[ContextKey.ITEM_OBJECTS]
        for obj in item_objects:
            self.assertEqual(obj.category.number, "5")

                                