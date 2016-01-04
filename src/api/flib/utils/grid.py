
from flib.models import Asset, Project, Tag, User
import ujson as json
import itertools


class GridAssets:
	def on_get(self, req, resp, tag, page):
		_from = (int(page)-1) * 50
		_to =  50
		raws = req.session.query(Asset).\
		    filter(Asset.tgs.any(Tag.name==tag)).offset(_from).limit(_to).all()
		tags = list(set(list(itertools.chain(*[i.tags for i in raws]))))
		resp.body = raws

