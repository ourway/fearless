

import falcon
from flib.models import User, Asset, Collection, Repository
from sqlalchemy import desc


class GetUserShows:

    def on_get(self, req, resp, userid):
        shows = req.session.query(Asset).filter_by(owner_id=userid)\
            .join(Repository).filter_by(name='showtime').order_by(desc(Asset.modified_on)).all()
        resp.body = [{'name': i.fullname.replace('.zip', ''),
                      'description': i.description, 'thumbnail': i.thumbnail} for i in shows]
