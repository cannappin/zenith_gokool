
import datetime

from .models import *


from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from django.core.files.uploadedfile import SimpleUploadedFile

# ----------------Les Fonction-------------------#


def create_artist(nom_artist, talent_artist):
    artist = Artist.objects.create(name_artist=nom_artist, skill_artist=talent_artist)
    # l'attribut pics-artist (ImageField) doit etre associé a un dossier. Pour ne pas toucher a notre vrai dossier on creer un Mock grace a 'SimpleUploadedFile'
    artist.pics_artist = SimpleUploadedFile(name='test_image.jpg', content=open('C:/Users/dev/Desktop/DevOps git/DJANGO/Zenith2.0/TiersMonde/event/static/event/images/3.jpg', 'rb').read(),  content_type='image/jpeg')

    artist.save()
    return artist 


def create_groupe(nom_groupe, type_groupe):
    """creates a new groupe
    """

    groupe = Groups.objects.create(name_group=nom_groupe, type_group=type_groupe)
    # l'attribut pics-group (ImageField) doit etre associé a un dossier. Pour ne pas toucher a notre vrai dossier on creer un Mock grace a 'SimpleUploadedFile'
    groupe.pics_group = SimpleUploadedFile(name='test_image.jpg', content=open('C:/Users/dev/Desktop/DevOps git/DJANGO/Zenith2.0/TiersMonde/event/static/event/images/2.jpg', 'rb').read(), content_type='image/jpeg')

    groupe.save()
    return groupe

def create_event(nom_event, billet_dispo):   
    """
    Creates a new event     
    """ 
    date_debut = timezone.now()
    date_fin = timezone.now() + datetime.timedelta(days=2)
    new_type = EventType.objects.create(name_type = 'concert')
    new_artist = create_artist('Maddy', 'drummer')
    new_groupe = create_groupe('les Lingos', 'Meeting')

    event = Events.objects.create(name_event=nom_event, av_ticket=billet_dispo, begin_date=date_debut, end_date=date_fin, type=new_type)

    new_groupe.artist.add(new_artist)
    event.group.add(new_groupe)

    # event.save()
    return event

def create_user(username, email, password):
    """creates new user 
    """
    user = User.objects.create_user(username, email, password)
    return user 

class EventIndexViewTests(TestCase):
    
    def test_no_event(self):
        """
        test_no_event tests the view 'Index' if no event,
        tests if the 'response.status_code' returns 200 (Successful)
        tests if the template 'event/index' contains << Pas d'évènements disponible >> 
        tests if context event_list is an 'empty' list 
        """
        response = self.client.get(reverse('event:index'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, "Pas d'évènements disponible")
        self.assertQuerysetEqual(response.context['event_list'],[])

    def test_single_event(self):
        event = create_event('Grounddays', '1043')
        response = self.client.get(reverse('event:index'))
        self.assertQuerysetEqual(response.context['event_list'],[event])

    def test_multiple_events(self):
        event1 = create_event('Grounddays', '1043')
        event2 = create_event('Mobys creation', '143')
        response = self.client.get(reverse('event:index'))
        self.assertQuerysetEqual(response.context['event_list'],[event1, event2])

    def test_event_as_group_details(self):
        event = create_event('Grounddays', '1043')
        response = self.client.get(reverse('event:index'))
        self.assertContains(response, event.group.all()[0].pics_group)
        # self.assertContains(response, event.group.all()[0].name_group)
        

class EventDetailViewTest(TestCase):
    
    def test_event_detail_with_event_without_user(self):
        event = create_event('Neverland', 200)
        response = self.client.get(reverse('event:detail', args=(event.id,)))
        self.assertEqual(response.status_code, 200)      
        # 'Connectez-vous pour acheter ou reserver !' ne s'affiche que si mon event a un group associé car j'appel group dans mon template detail.html pour pouvoir afficher les details d'un group de l'event
        self.assertContains(response, "Connectez-vous pour acheter ou reserver !")
        # on va test si 'artist.name_artist' apparait dans mon response, pour que cela marche j'ai besoin d'associé artist a groupe pour pouvoir afficher les details d'un artist 
        self.assertContains(response, event.group.all()[0].artist.all()[0].name_artist)

    def test_event_detail_with_event_with_user(self):
        event = create_event('Neverland', 200)
        create_user('test','test','test')
        
        self.client.login(username='test',password='test')
        response = self.client.get(reverse('event:detail', args=(event.id,)))
        self.assertContains(response, "Acheter")

    def test_event_detail_no_event(self):
        response = self.client.get(reverse('event:detail', args=(1,)))
        self.assertEqual(response.status_code, 404)
       



class EventAcheterViewTests(TestCase):

    def test_acheter_billet_without_user(self):
        event = create_event('School of rock', 333)
        url = reverse('event:acheter', args=(event.id,))
        response =self.client.get(url) 
        self.assertEqual(response.status_code, 200)

class EventProfilViewTests(TestCase):

    def test_profil_without_user(self):
        response = self.client.get(reverse('event:profil'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vous devez être connecté")

    def test_profil_with_user(self):        
        create_user('test','test','test')        
        self.client.login(username='test',password='test')
        response = self.client.get(reverse('event:profil', ))
        self.assertContains(response, "Vos billets")