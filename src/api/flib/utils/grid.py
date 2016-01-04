
from flib.models import Asset, Project, Tag, User
import ujson


class GridAssets:
	def on_get(self, req, resp, tag):
		resp.body = req.session.query(Asset).\
			filter(Asset.tgs.any(Tag.name==tag)).all()


