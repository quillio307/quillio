# HERE IS WHERE WE DEFINE USER
# NOTE: for those working with flask authentication, be sure to set user.authenticated = true upon successful login 
from mongoengine import *

connect('pyroute_db')

class User(Document):
    name = StringField(required=True, min_length=2, max_length=50)
    email = EmailField(required=True, min_length=5, unique=True)
    username = StringField(required=True, min_length=3, max_length=20)
    password = StringField(required=True, min_length=6, max_length=35) #regex = none
    authenticated = BooleanField(required=False, default=False) #after a user creates a profile, they arent automatically logged in 

    #returns success or failure for now  
    def add_user(user):
         if user_exists(user):
             return {'message': 'failure'}
        User(name=user['name'],username=user['username'], password=user['password'], email=user['email']).save()
        return {'message': 'success'}

    #checks database to determine if user exists already 
    def user_exists(user):
        if len(User.objects(email__exact=user['email'])) != 0
            return True
        return False


    # the following methods are used with flask-login authentication 
    
    # method used to see if a user is authenticated - returns value of their field
    def is_authenticated(user):
        return user['authenticated']
    
    # method determines if user has activated their account 
    #always returns true since we dont have emailing activation services yet
    def is_active(user):
        return True
    
    # method returns true if anonymous user -- there are none for our program
    # will always return false, this is not supported 
    def is_anonymous(user):
        return False
    
    # method returns a unicode that uniquely identifies a user
    # converts user id to unicode before return  (chr method)
    def get_id(user):
        return chr(user.id)
