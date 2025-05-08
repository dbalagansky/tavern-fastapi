import logging

from httpx import Response
from tavern._plugins.rest.response import RestResponse

logger = logging.getLogger(__name__)


class FastAPIResponse(RestResponse):
    """FastAPI response verifier"""

    def verify(self, response: Response):
        """Wrap the TestClient response into a Requests response and call the
        verifier for that. See docs for RestResponse for what this does and
        returns
        """

        from requests import Response

        wrapped_response = Response()
        wrapped_response.headers = response.headers
        wrapped_response.status_code = response.status_code
        wrapped_response._content = response.content

        return super().verify(wrapped_response)
