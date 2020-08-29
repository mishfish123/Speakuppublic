import requests


class ApiCall:
    """ Represents on API request & its associated response.

    Constructor:

    :param api_url: API url endpoint.
    :type api_url: string

    :param api_key: API Access Key
    :type api_key: string

    :param function: API function name to call.
    :type function: string

    :param output: Expected response format.
                   Can be one of:
                   * js (ie. json) *default*,
                   * xml,
                   * php (serialised php array),
                   * rabx
    :type output: string

    :param immediate: If True, will execute request
                      at time of construction. Otherwise,
                      `send_request` will need to be
                      called as needed.
    :type immediate: boolean

    Remaining `kwargs` will be passed along as
    request query parameters.
    """
    def __init__(
        self, api_url, api_key, function, output='js',
        immediate=True, **kwargs
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.function = function
        self.output = output
        self.params = kwargs
        self.params['key'] = self.api_key
        self.params['output'] = self.output

        if immediate:
            self.send_request()

    def send_request(self):
        """ Executes this API request.

        If the HTTP response is 200 OK, the response contents
        will be stored in this instance's `result` property.

        JSON responses will be automatically decoded.

        If the HTTP response was not ok, an exception will
        be raised.
        """
        response = requests.get(
            "{0}/{1}".format(self.api_url, self.function),
            params=self.params
        )
        if response.status_code != requests.codes.ok:
            # Eject with exception.
            response.raise_for_status()

        if self.output == 'js':
            self.result = response.json()
        else:
            self.result = response.text()
