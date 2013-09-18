import os
import json
import requests

class API:
    app_id = None
    token = None
    endpoint = None

    def __init__(self, app_id, token=None, endpoint=None):
        self.app_id = app_id
        self.token = token
        self.endpoint = endpoint

    def debug(self):
        return self._api_call('get', 'debug/')

    def auth(self, username, password):
        response = self._api_call(method='post', path='auth/', username=username, password=password)
        if response['success']:
            self.token = response['token']
            return self.token
        else:
            raise Exception(response['message']) # TODO: set custom exception?

    def offer_list(self):
        response = self._api_call(method='get', path='offer')
        return response

    def offer_detail(self, slug):
        response = self._api_call(method='get', path='offer/%s/' % slug)
        return response

    def offer_create(self, title, description=None, # Basic
                     base_price=None, currency=None, # Pricing
                     quantity=None, # Quantity
                     start_date=None, end_date=None, venue=None, timezone=None, # Event
                     redirect_url=None, # Redirect user to URL after successful payment
                     note=None, # Show note, embed in receipt after successful payment
                     upload_file=None, # File to upload
                     cover_image=None, # Cover image to associate with offer
                     ):

        if upload_file:
            file_upload_json = self._upload_file(upload_file)
        else:
            file_upload_json = None

        if cover_image:
            cover_image_json = self._upload_file(cover_image)
        else:
            cover_image_json = None

        offer_data = dict(
            title=title,
            description=description,
            base_price=base_price,
            currency=currency,
            quantity=quantity,
            start_date=start_date,
            end_date=end_date,
            venue=venue,
            timezone=timezone,
            redirect_url=redirect_url,
            note=note,
            file_upload_json=file_upload_json,
            cover_image_json=cover_image_json,
        )
        response = self._api_call(method='post', path='offer/', **offer_data)
        return response

    def offer_edit(self, slug, # Need slug to identify offer
                     title=None, description=None, # Basic
                     base_price=None, currency=None, # Pricing
                     quantity=None, # Quantity
                     start_date=None, end_date=None, venue=None, timezone=None, # Event
                     redirect_url=None, # Redirect user to URL after successful payment
                     note=None, # Show note, embed in receipt after successful payment
                     upload_file=None, # File to upload
                     cover_image=None, # Cover image to associate with offer
                     ):
        raise NotImplementedError('Uh oh!')

    def offer_delete(self, slug):
        response = self._api_call(method='delete', path='offer/%s/' % slug)
        return response

    def _api_call(self, method, path, **kwargs):
        # Header: App-Id
        headers = {'X-App-Id': self.app_id}

        # If available, add the Auth-token to header
        if self.token:
            headers.update({'X-Auth-Token':self.token})

        # Build the URL for API call
        api_path = self.endpoint + path

        if method.upper() == 'GET':
            req = requests.get(api_path, data=kwargs, headers=headers)
        elif method.upper() == 'POST':
            req = requests.post(api_path, data=kwargs, headers=headers)
        elif method.upper() == 'DELETE':
            req = requests.delete(api_path, data=kwargs, headers=headers)
        elif method.upper() == 'PUT':
            req = requests.put(api_path, data=kwargs, headers=headers)
        elif method.upper() == 'PATCH':
            req = requests.patch(api_path, data=kwargs, headers=headers)
        else:
            raise Exception('Unable to make a API call for "%s" method.' % method)

        try:
            return json.loads(req.text)
        except:
            raise Exception('Unable to decode response. Expected JSON, got this: \n\n\n %s' % req.text)

    def _get_file_upload_url(self):
        """
        Gets signed upload URL from server, use this to upload file.
        """
        response = self.api_request(method='GET', path='offer/get_file_upload_url/')
        return response

    def _upload_file(self, filepath):
        """
        Helper function to upload file from local path.
        """
        file_upload_url = self._get_file_upload_url()

        filename = os.path.basename(filepath)
        files = {'fileUpload':(filename, open(filepath, 'rb'))}
        response = requests.post(file_upload_url, files=files)
        return response.text
