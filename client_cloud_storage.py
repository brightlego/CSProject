import os
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import json
import ssl

CLOUD_IP = '127.0.0.1'
CLOUD_PORT = 5005
CLOUD_URL = f'https://{CLOUD_IP}:{CLOUD_PORT}'

cert = ssl.get_server_certificate((CLOUD_IP, CLOUD_PORT))
with open('tmp/server.crt', 'w') as f:
    f.write(cert)

context = ssl.create_default_context()
context.load_verify_locations(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp', 'server.crt'))
context.check_hostname = False

USER_AUTH_URL = urllib.parse.urljoin(CLOUD_URL, 'user/auth')
USER_CREATE_URL = urllib.parse.urljoin(CLOUD_URL, 'user/create')
FILE_CREATE_URL = urllib.parse.urljoin(CLOUD_URL, 'file/add')
FILE_UPDATE_URL = urllib.parse.urljoin(CLOUD_URL, 'file/update')
FILE_GET_ONE_URL = urllib.parse.urljoin(CLOUD_URL, 'file/get-one/')
FILE_GET_ALL_URL = urllib.parse.urljoin(CLOUD_URL, 'file/get-all')


class AuthorisationError(Exception): pass
class ConflictError(Exception): pass


def handle_http_error(err):
    match err.code:
        case 403:
            raise AuthorisationError
        case 404:
            raise FileNotFoundError
        case 409:
            raise ConflictError
        case _:
            print(f'Received {err.code} {err.reason}')


class CloudStorage:
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        self.handlers = (urllib.request.HTTPCookieProcessor(self.cj),
                         urllib.request.HTTPSHandler(context=context))
        self.opener = urllib.request.build_opener(*self.handlers)

    def authorise_user(self, username, password):
        data = urllib.parse.urlencode({'Username': username, 'Password': password})
        data = data.encode('UTF-8')
        try:
            resp = self.opener.open(USER_AUTH_URL, data=data)
        except urllib.error.HTTPError as err:
            handle_http_error(err)

    def create_user(self, username, password):
        data = urllib.parse.urlencode({'Username': username, 'Password': password})
        data = data.encode('UTF-8')
        try:
            resp = self.opener.open(USER_CREATE_URL, data=data)
        except urllib.error.HTTPError as err:
            handle_http_error(err)

    def create_file(self, filename, description):
        data = urllib.parse.urlencode({'Filename': filename, 'Description': description})
        data = data.encode('UTF-8')
        filepath = ""
        try:
            response = self.opener.open(FILE_CREATE_URL, data=data)
            response_data = response.read()
            response_data = json.loads(response_data)
            filepath = response_data['Filepath']
        except urllib.error.HTTPError as err:
            handle_http_error(err)
        return filepath

    def update_file(self, filepath, filename, description, content):
        data = json.dumps({'Filepath': filepath, 'Filename': filename, 'Description': description, 'Content': content})
        data = data.encode('UTF-8')
        try:
            response = self.opener.open(FILE_UPDATE_URL, data=data)
        except urllib.error.HTTPError as err:
            handle_http_error(err)
        return

    def get_all_files(self):
        files = []
        try:
            response = self.opener.open(FILE_GET_ALL_URL)
            response_data = response.read()
            response_data = json.loads(response_data)
            files = response_data["Files"]
        except urllib.error.HTTPError as err:
            handle_http_error(err)
        return files

    def get_one_file(self, filepath):
        filename = ""
        description = ""
        content = ""
        try:
            path = urllib.parse.urljoin(FILE_GET_ONE_URL, filepath)
            response = self.opener.open(path)
            response_data = response.read()
            response_data = json.loads(response_data)
            filename = response_data["Filename"]
            description = response_data["Description"]
            content = response_data["Content"]
        except urllib.error.HTTPError as err:
            handle_http_error(err)

        return filename, description, content
