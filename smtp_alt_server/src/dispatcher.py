import message
import schedule
import time

from googleapiclient.errors import HttpError


class Dispatcher:
    def __init__(self, service):
        self.service = service
        self.message_handler = message.MessageHandler(self.service)

    def watch_inbox(self, pubsub_request):
        schedule.every().day.do(
            self._watch_inbox_helper,
            request=pubsub_request)

        schedule.run_all()
        while True:
            schedule.run_pending()
            time.sleep(1)

    def _watch_inbox_helper(self, request):
        self.service.users().watch(
            userId='me',
            body=request).execute()

        print('[debug] Inbox watch initiated. request: {}'.format(request))

    def check_inbox(self, query):
        try:
            received_messages = self._list_messages(query)
            processed_payload = self.message_handler.process_messages(received_messages)

            return processed_payload
        except Exception as error:
            # logger.error('Cannot get mail: %s' % error)
            print('check_inbox error: {}'.format(error))

    def _list_messages(self, query):
        try:
            response = self.service.users().messages().list(
                userId='me',
                q=query).execute()

            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages
        except HttpError as error:
            print('list_messages error: {}'.format(error))