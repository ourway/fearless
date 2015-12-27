
from flib.models import Asset, Project, Tag, User
import ujson


class LatestImages:
	def on_get(self, req, resp):
		resp.body = req.session.query(Asset).\
			filter(Asset.tgs.any(Tag.name=='grid')).all()

