from envelopes import Envelope, GMailSMTP
from base64 import decodestring

envelope = Envelope(
    from_addr=(u'from@example.com', u'From Example'),
    to_addr=(u'farsheed.ashouri@gmail.com'),
    subject=u'Envelopes demo 2',
    text_body=u"I'm a  not helicopter!"
)
envelope.add_attachment('/home/farsheed/Pictures/Screenshot.jpg')

# Send the envelope using an ad-hoc connection...
#envelope.send('smtp.googlemail.com', login='vixenserver@gmail.com',
#              password='Cc183060', tls=True)

# Or send the envelope using a shared GMail connection...
pwd = '\n==gchZmcoVWbwADMxM2Q'[::-1]
gmail = GMailSMTP('farsheed.ashouri@gmail.com', decodestring(pwd))
gmail.send(envelope)
