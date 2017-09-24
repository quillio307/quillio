# HERE IS WHERE WE DEFINE USER
from mongoengine import *

connect('pyroute_db')

class User(Document):
    name = StringField(required=True, min_length=2, max_length=50)
    email = EmailField(required=True, min_length=5, unique=True)
    username = StringField(required=True, min_length=3, max_length=20)
    password = StringField(required=True, min_length=6, max_length=35) #regex = none

    #incomplete, finish later 
    #def add_user(user)
      #  if 

    