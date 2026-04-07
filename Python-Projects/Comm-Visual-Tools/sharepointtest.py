import os
import office365
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_request import ClientRequest
from office365.runtime.utilities.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.file_creation_information import FileCreationInformation

url = '[HTTPS]'

ctx_auth = AuthenticationContext(url=f'{url}')
if ctx_auth.acquire_token_for_user(username='[username]',
                                       password='[password]'):

    ctx = ClientContext(f'{url}', ctx_auth)
    target_list = ctx.web.lists.get_by_title("Documents")
    info = FileCreationInformation()
    file_name = "lixxcpsutap01_8080.png"
    path = "{0}/python/live_files/{1}".format(os.path.dirname(__file__), file_name)
    with open(path, 'rb') as content_file:
        info.content = content = content_file.read()
    info.url = file_name
    info.overwrite = True
    upload_file = target_list.root_folder.files.add(info)
    ctx.execute_query()