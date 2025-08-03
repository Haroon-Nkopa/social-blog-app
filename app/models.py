from app import db, login
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from app import app

#we defining the followers association table 
followers = sa.Table('follower', db.metadata,
                     sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True ),
                     sa.Column('following_id', sa.Integer, sa.ForeignKey('user.id'), primary_key= True)
                     )

class User(UserMixin, db.Model):

    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    username : so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    email : so.Mapped[str] = so.mapped_column(sa.String(124), unique=True, index=True)
    password_hash : so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me : so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen : so.Mapped[Optional[datetime]] = so.mapped_column( default= lambda : datetime.now(timezone.utc))
    posts : so.WriteOnlyMapped['Post'] = so.relationship( back_populates='author' )
    following : so.WriteOnlyMapped['User'] = so.relationship(secondary= followers, primaryjoin=(followers.c.follower_id == id),
                                                              secondaryjoin=(followers.c.following_id == id), 
                                                              back_populates='followers')
    followers : so.WriteOnlyMapped['User'] = so.relationship(secondary=followers, primaryjoin=(followers.c.following_id == id),
                                                             secondaryjoin=(followers.c.follower_id ==id), 
                                                             back_populates='following') 



    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
        
    def __repr__(self):
        return '<user {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash , password)    

    #defing functions that are responsable for allowing following and unfollowing 

    def is_following(self, user):
        query = self.followers.select().where( User.id == user.id )
        return db.session.scalar(query) is not None

    def follow(self, user):
        if not self.is_following(user) :
            self.followers.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followers.remove(user)            

    #a funtion to count followers and followin people

    def count_following(self):
        query = sa.select( sa.func.count() ).select_from( self.following.select().subquery() )      
        return db.session.scalar(query)

    def count_followers(self):
        query = sa.select( sa.func.count() ).select_from( self.followers.select().subquery() )   
        return db.session.scalar(query)
    
    #defining a method that creates a query that returns a list of followers and our posts. 
 
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(Author.id == self.id, 
                          Follower.id == self.id)
            )
            .group_by(Post)
            .order_by( Post.timestamp.desc() )
        )
    
    def generate_token(self):
        #generate pay load
        payload = {'user_id' : self.id,'exp' : time() + 600 }
        try:
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        except TypeError :
            print('probably the payload is not diction type', TypeError)
            token = None
        except ValueError:
            print('The is an empty value, probably the secrete key is not set, algorithm or something..', ValueError)
            token = None
        except jwt.exceptions.PyJWTError:
            print('something weird when trying to generate token', jwt.exceptions.PyJWTError)
            token = None
        return token
    
    @staticmethod
    def verify_token(token):
        try:  
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
            user = db.session.get(User, id)
        except Exception:
            return    
        return user

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))    


class Post(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    body : so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp : so.Mapped[datetime] = so.mapped_column(default= lambda: datetime.now(timezone.utc,), index=True) 
    user_id : so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)   
    author : so.Mapped['User'] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<post {}>'.format(self.body)


