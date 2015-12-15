
from flib.utils.AAA import getUserInfoFromSession
from flib.utils.helpers import get_params
from flib.models import Comment, Asset, Collection, Project, User


class AddComment:
    def on_put(self, req, resp):
        userInfo = getUserInfoFromSession(req, resp)
	userId = userInfo.get('id')
        data = get_params(req.stream, flat=False)
	content = data.get('content')
	item = data.get('item')
	user_id = data.get('user_id')
	## lets see if it's an asset:
	#req.session

	_type = None
	_id = None
	_name = None
        target_asset = Asset.query.filter_by(uuid=item).first()
        target_collection = Collection.query.filter_by(uuid=item).first()
        #target_project = Project.query.filter_by(uuid=item).first()
	target = target_asset or target_collection
	if target_asset:
		 _type = 'ams/a'
	elif target_collection:
		_type='amc/c'
	#print target	
	message_targets = set()
	if target:
		_id = target.id
		_name = target.name
		message_targets.add(target.owner_id)
        	other_commentors = User.query.join(Comment).\
			filter_by(item=item).all()
		for i in other_commentors:
			message_targets.add(i.id)


	newC = Comment(content=content, item=item, user_id=user_id)
	req.session.add(newC)
	if userId in message_targets:
		message_targets.remove(userId)
	resp.body = dict(targets=list(message_targets), type=_type,
		 id=_id, name=_name)

