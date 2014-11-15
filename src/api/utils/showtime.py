


import falcon
from models import User, Asset, Collection, session
from sqlalchemy import desc
class GetUserShows:
    def on_get(self, req, resp, userid):
        shows = session.query(Asset.name, Asset.description, Asset.thumbnail).join(Collection)\
            .filter(Asset.users.any(User.id==userid)).order_by(desc(Asset.modified_on)).all()
        resp.body = [{'name':i.name.replace('.zip', ''), 
                      'description':i.description, 'thumbnail':i.thumbnail} for i in shows]
