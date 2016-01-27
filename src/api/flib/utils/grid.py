
from flib.models import Asset, Project, Tag, User
import ujson as json
from sqlalchemy import desc, asc
import itertools


class GridAssets:
	def on_get(self, req, resp, tag, page):
		_from = (int(page)-1) * 100
		_to = 100
		raws = req.session.query(Asset).\
		    filter(Asset.tgs.any(Tag.name==tag)).order_by(desc(Asset.created_on)).offset(_from).limit(_to).all()
		tags = list(set(list(itertools.chain(*[i.tags for i in raws]))))
		resp.body = raws

