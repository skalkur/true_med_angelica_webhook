#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") == "re_iterate_info-yes":

        result=req.get("result")
        duration=result.get('contexts')[0].get('parameters').get('duration').get('date-period.original')
        parameters=result.get('parameters')
        person=parameters.get('person')
        gender=parameters.get('gender')
        problems=parameters.get('problems')
        other_symptoms_list=[parameters.get('secondary_symptom'),parameters.get('tertiary_symptom'),parameters.get('psycological_symptoms')]
        other_symptoms_list=([k for k in other_symptoms_list if k!='null'])
        
    
      #  cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}
    
     #   speech = "The cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."
        if other_symptoms_list!=[]:
            if len(other_symptoms_list)>1:
                other_symptoms_list[-1]='and '+other_symptoms_list[-1]
                speech="Your name is {} and your gender is {}. You seem to have {} since {}. In addition to this, you also have {}.".format(person, gender, problems, duration, ", ".join(other_symptoms_list))
            else:
                speech="Your name is {} and your gender is {}. You seem to have {} since {}. In addition to this, you also have {}.".format(person, gender, problems, duration, "".join(other_symptoms_list))
    
        else:
            speech="Your name is {} and your gender is {}. You seem to have {} since {}. You have no other symptoms.".format(person, gender, problems, duration) 
        print("Response:")
        print(speech)
    
        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            # "contextOut": [],
            "source": "apiai-angelica"
        }
        
    elif req.get("result").get("action")=="re_iterate_info-no":
        result=req.get("result")
        duration=result.get('contexts')[0].get('parameters').get('duration').get('date-period.original')
        parameters=result.get('parameters')
        person=parameters.get('person')
        gender=parameters.get('gender')
        problems=parameters.get('problems')
        other_symptoms_list=[parameters.get('secondary_symptom'),parameters.get('tertiary_symptom'),parameters.get('psycological_symptoms')]
        other_symptoms_list=([k for k in other_symptoms_list if k!='null'])
        return {}

    else:
        return {}
        


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % (port))

    app.run(debug=True, port=port, host='0.0.0.0')
