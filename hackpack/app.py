import re

from flask import Flask
from flask import render_template
from flask import url_for
from flask import request

from twilio import twiml
from twilio.util import TwilioCapability

# Declare and configure application
app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('local_settings.py')

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

# Voice Request URL
@app.route('/voice', methods=['GET', 'POST'])
def voice():
    print str(request)
    to = request.values.get('To', None)
    print "to: " + str(to)
    if to is None:
        return ("Point the voice URL of your registration-enabled Twilio SIP domain to this script. "
                "You will see what it can do for you :-)")

    found_e164_pstn = re.search("^sip:([+][0-9]{10,14})@", to)
    found_011_pstn = re.search("^sip:011([0-9]{10,14})@", to)
    found_us_pstn = re.search("^sip:[+]?1?([0-9]{10})@", to)

    if found_e164_pstn:
        to = "{0}".format(found_e164_pstn.group(1))
    elif found_011_pstn:
        to = "+{0}".format(found_011_pstn.group(1))
    elif found_us_pstn:
        to = "+1{0}".format(found_us_pstn.group(1))

    answer_on_bridge = str2bool(request.values.get('answerOnBridge', "True"))
    print "answer_on_bridge: " + str(answer_on_bridge)
    record_param = request.values.get('record', 'do-not-record')
    print "record_param: " + str(record_param)

    response = twiml.Response()

    if to.startswith("sip:"):
        with response.dial(answerOnBridge=answer_on_bridge, record=record_param) as d:
            d.sip(to)
    else:
        caller_id = request.values.get('callerId', app.config['TWILIO_CALLER_ID'])
        print "caller_id before strip: " + str(caller_id)
        caller_id = caller_id.strip()
        print "caller_id aftewr strip: " + str(caller_id)
        with response.dial(answerOnBridge=answer_on_bridge, callerId=caller_id, record=record_param) as d:
            d.number(to)
    print str(response)
    return str(response)




# Installation success page
@app.route('/')
def index():

    voice_url = url_for('.voice', _external=True) + "?callerId=+1NXXNXXXXXX"

    params = {
         'Voice URL': voice_url
    }
    return render_template('index.html', params=params,
                           configuration_error=None)
