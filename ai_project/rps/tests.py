from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from .views import login_request, register, player, custom_logout, guess_gesture
from .models import Image
from .forms import CreateUserForm

class TestUrls(SimpleTestCase):

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login_request)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, register)

    def test_player_url_resolves(self):
        url = reverse('player')
        self.assertEquals(resolve(url).func, player)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, custom_logout)

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.player_url = reverse('player')
        self.logout_url = reverse('logout')

    def test_login_GET(self):
        response = self.client.get(self.login_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'rps/home.html')

    def test_register_GET(self):
        response = self.client.get(self.register_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'rps/registration.html')

    def test_player_GET(self):
        response = self.client.get(self.player_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'rps/player.html')

    def test_logout_GET(self):
        response = self.client.get(self.logout_url)

        self.assertEquals(response.status_code, 302)

    def test_register_POST(self):
        response = self.client.post(self.register_url)

        self.assertEquals(response.status_code, 200)

    def test_register_Form(self):
        form_data = {'username': 'jeffbazos', 'first_name': 'Jeff', 'email': 'jeff.bazos@hotmail.com',
                     'password1': 'hellojeff','password2': 'hellojeff'}
        form = CreateUserForm(data=form_data)
        self.assertTrue(form.is_valid())

class TestModels(TestCase):

    def setUp(self):
        self.image = Image.objects.create(
            file='abcde.png',
            predict='✋'
        )

    def test_image_object_is_valid(self):
        image = Image.objects.get(file="abcde.png")
        self.assertEqual(image.predict, '✋')
