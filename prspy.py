import requests
import json
import os
mail_username = '<username>'
mail_password = '<password>'
mail_recv = "<mail@gmail.com>"
info_nric = '<ep_num>'
info_no_of_people = '1'
info_phonenumber = '123123XX'

payload2017 = {
    "get3MthCalendarRequest": {
        "authToken": "",
        "bookingID": "",
        "collVenue": "ICA",
        "groupBookingIDs": "",
        "groupID": "",
        "identifier1": info_nric,
        "identifier2": info_no_of_people,
        "identifier3": info_phonenumber,
        "month": "1",
        "nav": "P",
        "noOfPpl": "3",
        "selVseiMode": "",
        "svcType": "PRAP",
        "year": "2017"
    }
}
payload2016 = {
    "get3MthCalendarRequest": {
        "authToken": "",
        "bookingID": "",
        "collVenue": "ICA",
        "groupBookingIDs": "",
        "groupID": "",
        "identifier1": info_nric,
        "identifier2": info_no_of_people,
        "identifier3": info_phonenumber,
        "month": "12",
        "nav": "P",
        "noOfPpl": "3",
        "selVseiMode": "",
        "svcType": "PRAP",
        "year": "2016"
    }
}

headers = {
    'Content-type': 'application/json',
    "auth_token":"e0d25197-332a-454f-9f81-ae30d20ffa40"
}

def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

def getToken():
    import json
    import requests
    pay_load = {
        "checkSingPassEligibilityRequest": {
            "authToken": "",
            "identifier1": info_nric,
            "identifier2": info_no_of_people,
            "identifier3": info_phonenumber,
            "svcType": "PRAP"
        }
    }
    headers = {
        'Content-type': 'application/json',
    }
    r = requests.post(url='https://eappointment.ica.gov.sg/ibook/services/mwsCheckSingPassEligibility', data=json.dumps(pay_load), headers=headers)
    res = r.json()
    return json.loads(res['message'])['checkSingPassEligibilityResponse'][0]['authToken']

def getWarning(data, headers):
    r = None
    response = requests.post(url='https://eappointment.ica.gov.sg/ibook/services/mwsGet3MthCalendar', data=data, headers=headers)
    if 'error' in response.text:
        print 'bad'
        headers['auth_token'] = getToken()
        response = requests.post(url='https://eappointment.ica.gov.sg/ibook/services/mwsGet3MthCalendar', data=data, headers=headers)
    r= json.loads(response.text)
    print r
    allres = json.loads(r['message'])['get3MthCalendarResponse'][0]['calendar']
    for i in allres:
        print i['startDate']
        for j in  i['days']:
            if not j['dayStatus']=='cal_PH' and not j['dayStatus'] =='cal_AF' and not j['dayStatus']=='cal_NA':
                print j['dayStatus']
                return i['startDate']+" - "+j['day']
    return None

day = ""

####################################################
################### MAIN WORKFLOW ##################
####################################################
while True:
    try:
        print '##### for 2016 #####'
        key2016 = getWarning(json.dumps(payload2016), headers)
        if not key2016==None:
            day=key2016
            break;
        print '##### for 2017 #####'
        key2017 = getWarning(json.dumps(payload2017), headers)
        if not key2017==None:
            day=key2017
            break;
    except:
        print "error"

#notify(title='found pr', subtitle='warning',message=day)
send_email(user=mail_username, pwd=mail_password, recipient=mail_recv, subject='found pr index', body=day)
