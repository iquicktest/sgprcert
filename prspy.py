import requests
import json
import os

mail_username = ''
mail_password = ''
mail_recv = ""
info_nric = ''
info_no_of_people = ''
info_phonenumber = ''

base_url = 'https://eappointment.ica.gov.sg/ibook/services'

def get_payload(month):
    return {
        "get3MthCalendarRequest": {
            "authToken": "",
            "bookingID": "",
            "collVenue": "ICA",
            "groupBookingIDs": "",
            "groupID": "",
            "identifier1": info_nric,
            "identifier2": info_no_of_people,
            "identifier3": info_phonenumber,
            "month": str(month),
            "nav": "P",
            "noOfPpl": "3",
            "selVseiMode": "",
            "svcType": "PRAP",
            "year": "2017"
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
    r = requests.post(
            url='{0}/mwsCheckSingPassEligibility'.format(base_url), 
            data=json.dumps(pay_load), 
            headers=headers)
    res = r.json()
    return json.loads(
            res['message'])['checkSingPassEligibilityResponse'][0]['authToken']

def getWarning(data, headers):
    r = None
    status = ['cal_PH','cal_AF','cal_NA']
    response = requests.post(
            url='{0}/mwsGet3MthCalendar'.format(base_url), 
            data=data, headers=headers)
    # if error, then retry and get new token
    if 'error' in response.text:
        print 'bad'
        headers['auth_token'] = getToken()
        response = requests.post(
                url='{0}/mwsGet3MthCalendar'.format(base_url), 
                data=data, headers=headers)
    r = json.loads(response.text)
    print r
    allres = json.loads(r['message'])['get3MthCalendarResponse'][0]['calendar']
    for i in allres:
        print i['startDate']
        for j in  i['days']:
            if j['dayStatus'] not in status:
                print j['dayStatus']
                return i['startDate']+" - "+j['day']
    return None

day = ""

####################################################
################### MAIN WORKFLOW ##################
####################################################
while True:
    try:
        print '##### for 2017 for 4~6 #####'
        payload = get_payload(6)
        key2017 = getWarning(json.dumps(payload), headers)
        if not key2017==None:
            day=key2017
            break;

        print '##### for 2017 for 7~9 #####'
        payload = get_payload(9)
        key2017 = getWarning(json.dumps(payload), headers)
        if not key2017==None:
            day=key2017
            break;

        print '##### for 2017 for 10 #####'
        payload = get_payload(12)
        key2017 = getWarning(json.dumps(payload), headers)
        if not key2017==None:
            day=key2017
            break;
    except:
        print "error"

#notify(title='found pr', subtitle='warning',message=day)
send_email(user=mail_username, pwd=mail_password, recipient=mail_recv, subject='found pr index', body=day)
