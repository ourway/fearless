


import falcon
from models import User, Asset, Collection,Repository, session
from sqlalchemy import desc

class GetUserShows:
    def on_get(self, req, resp, userid):
        shows = session.query(Asset).filter_by(owner_id=userid)\
            .join(Repository).filter_by(name = 'showtime').order_by(desc(Asset.modified_on)).all()
        resp.body = [{'name':i.name.replace('.zip', ''), 
                      'description':i.description, 'thumbnail':i.thumbnail} for i in shows]


