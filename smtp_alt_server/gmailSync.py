from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from bs4 import BeautifulSoup
from dateutil import parser
import csv
import pickle
import os
import sys

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
credentials_path = os.path.join(script_dir, './confidential/smtp_credentials.json')


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
credential = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        credential = pickle.load(token)
if not credential or not credential.valid:
    if credential and credential.expired and credential.refresh_token:
        credential.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES)
        credential = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(credential, token)

GMAIL = build('gmail', 'v1', credentials=credential)

user_id = 'me'
label_id_one = 'INBOX'
label_id_two = 'UNREAD'

unread_msgs = GMAIL.users().messages().list(userId=user_id, labelIds=[label_id_one, label_id_two]).execute()

# request = {
#   'labelIds': [label_id_one, label_id_two],
#   'topicName': 'projects/principal-fact-300509/topics/mailupdate'
# }
# 'labelFilterAction': filter_action,
# GMAIL.users().watch(userId=user_id, body=request).execute()

print(unread_msgs)
msg_list = unread_msgs['messages']
print("Pending email count = ", str(len(msg_list)))

final_list = []

for msg in msg_list:
    temp_dict = {}
    m_id = msg['id']
    message = GMAIL.users().messages().get(userId=user_id, id=m_id).execute()
    payload = message['payload']
    header = payload['headers']

    for one in header:
        if one['name'] == 'Subject':
            msg_subject = one['value']
            temp_dict['Subject'] = msg_subject
        else:
            pass

    for two in header:
        if two['name'] == 'Date':
            msg_date = two['value']
            date_parse = (parser.parse(msg_date))
            m_date = (date_parse.date())
            temp_dict['Date'] = str(m_date)
        else:
            pass

    for three in header:
        if three['name'] == 'From':
            msg_from = three['value']
            temp_dict['Sender'] = msg_from
        else:
            pass

    temp_dict['Snippet'] = message['snippet']  # fetching message snippet

    try:
        # >_ ref mail cleaning repo
        # Fetching message body
        msg_parts = payload['parts']  # fetching the message parts
        part_one = msg_parts[0]  # fetching first element of the part
        part_body = part_one['body']  # fetching body of the message
        part_data = part_body['data']  # fetching data from the body
        clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8
        clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
        soup = BeautifulSoup(clean_two, "lxml")
        msg_body = soup.body()
        # msg_body is a readible form of message body
        # depending on the end user's requirements, it can be further cleaned
        # using regex, beautiful soup, or any other method
        temp_dict['Message_body'] = msg_body

    except:
        pass

    print(temp_dict)
    final_list.append(temp_dict)

    # mark as read
    GMAIL.users().messages().modify(userId=user_id, id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()

print("Total messaged retrieved: ", str(len(final_list)))

with open('CSV_NAME.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['Sender', 'Subject', 'Date', 'Snippet', 'Message_body']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()
    for val in final_list:
        writer.writerow(val)