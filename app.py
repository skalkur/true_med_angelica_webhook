#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

patient_info={}
strain_score={
              "Snoop Dogg":400,
              "Eminem":240,
              "NWA":350,
              "Akon":750,
              "Dr. Dre":425
              }

def get_comparables(strain_taken):
    global strain_score
    return [k for k,v in strain_score.items() if v>strain_score[strain_taken]]

def get_strains():
    global strain_score
    return [k for k,v in sorted(strain_score.items(), key=lambda k:k[1], reverse=True)]
             
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
    global patient_info
    if req.get("result").get("action") == "re_iterate_info-yes":
        result=req.get("result")
        duration=result.get('contexts')[0].get('parameters').\
get('duration').get('any.original')
        patient_info['duration']=duration
        parameters=result.get('parameters')
        person=parameters.get('person')
        patient_info['person']=person
        gender=parameters.get('gender')
        patient_info['gender']=gender
        problems=parameters.get('problems')
        patient_info['problems']=problems
        other_symptoms_list=[parameters.get('secondary_symptom'),parameters.\
                             get('tertiary_symptom'),parameters.\
get('psycological_symptoms')]
        other_symptoms_list=([k for k in other_symptoms_list if k!='null'])
        patient_info['other_symptoms_list']=other_symptoms_list

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
            "speech": speech+" May I know what strains do you use for your condition?",
            "displayText": speech+" May I know what strains do you use for your condition?",
            #"data": {},
#             "contextOut": [
#                            {
#                             "name":"strain",
#                             "parameters":{
#                                           "strain":"Snoop Dogg"
#                                           },
#                                           "lifespan":5
#                                           }
#                                           ],
            "source": "apiai-angelica"
        }
        
    elif req.get("result").get("action")=="re-iterate_info-no":
        result=req.get("result")
        duration=result.get('contexts')[0].get('parameters').get('duration').get('any.original')
        patient_info['duration']=duration
        parameters=result.get('parameters')
        person=parameters.get('person')
        patient_info['person']=person
        gender=parameters.get('gender')
        patient_info['gender']=gender
        problems=parameters.get('problems')
        patient_info['problems']=problems
        other_symptoms_list=[parameters.get('secondary_symptom'),parameters.get('tertiary_symptom'),parameters.get('psycological_symptoms')]
        other_symptoms_list=([k for k in other_symptoms_list if k!='null'])
        patient_info['other_symptoms_list']=other_symptoms_list

        speech="Alright!"+" May I know what strains do you use for your condition?"
        return {
                "speech":speech,
                "displayText":speech,
                "source":"apiai-angelica"
       }

    elif req.get("result").get("action")=="get_strain_info":
        result=req.get("result")
        strain_taken=result.get('parameters').get('strain')
        comparables=get_comparables(strain_taken)
        patient_info["strain_taken"]=strain_taken
        patient_info["comparables"]=comparables
        if comparables!=[]:
            if len(comparables)>1:
                comparables[-1]='or '+comparables[-1]
                speech="Based on our observations, the better comparables for {} are either of {}.".format(strain_taken, ", ".join(comparables))
            else:
                speech="Based on our observations, the only better comparable for {} is {}.".format(strain_taken, "".join(comparables))
    
        else:
            speech="As per my knowledge, you seem to be taking the most effective strain for {}".format(patient_info['problems']) 
        
        print(patient_info)    
            
        print("Response:")
        print(speech)
        return {
            "speech": speech+" I hope I was able to help you out, %s.\nTo start over afresh, type or say 'Start Over'. Goodbye." %(patient_info['person']),
            "displayText": speech+" I hope I was able to help you out, %s.\nTo start over afresh, type or say 'Start Over'. Goodbye." %(patient_info['person']),
            #"data": {},
#             "contextOut": [
#                            {
#                             "name":"strain",
#                             "parameters":{
#                                           "strain":"Snoop Dogg"
#                                           },
#                                           "lifespan":5
#                                           }
#                                           ],
            "source": "apiai-angelica"
        }    
        
    elif req.get("result").get("action")=="no_strain_info_re-iterate_yes" or req.get("result").get("action")=="no_strain_info_re-iterate_no":
        strains=get_strains()
        speech="Not to worry, {}. Based on my knowledge, I shall provide you the top strains for {} ranked as per our metrics. \
        They are {}. I hope I was able to help you out, {}.\nTo start over afresh, type or say 'Start Over'. Goodbye.".format(patient_info['person'],patient_info['problems'], ", ".join(strains), patient_info['person'])
        print(patient_info)
        print("Response:")
        print(speech)
        
        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
#             "contextOut": [
#                            {
#                             "name":"strain",
#                             "parameters":{
#                                           "strain":"Snoop Dogg"
#                                           },
#                                           "lifespan":5
#                                           }
#                                           ],
            "source": "apiai-angelica"
        }         
        
    else:
        return {}
        


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % (port))

    app.run(debug=True, port=port, host='0.0.0.0')
