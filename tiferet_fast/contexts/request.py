"""Fast API Request Context"""

# *** imports

# ** core
from typing import Any

# ** infra
from tiferet.contexts.request import RequestContext
from tiferet.models import ModelObject

# *** contexts

# ** context: fast_request_context
class FastRequestContext(RequestContext):
    '''
    A context for handling Fast API request data and responses.
    '''

    # * method: handle_response
    def handle_response(self) -> Any:
        '''
        Handle the response for the Fast API request context.

        :return: The response.
        :rtype: Any
        '''

        # Set the result using the set_result method to ensure proper formatting.
        self.set_result(self.result)

        # Handle the response using the parent method.
        return super().handle_response()

    # * method: set_result
    def set_result(self, result: Any):
        '''
        Set the result of the request context.

        :param result: The result to set.
        :type result: Any
        '''

        # If the response is None, return an empty response.
        if result is None:
            self.result = ''

        # Convert the response to a dictionary if it's a ModelObject.
        elif isinstance(result, ModelObject):
            self.result = result.to_primitive()

        # If the response is a list containing model objects, convert each to a dictionary.
        elif isinstance(result, list) and all(isinstance(item, ModelObject) for item in result):
            self.result = [item.to_primitive() for item in result]

        # If the response is a dict containing model objects, convert each to a dictionary.
        elif isinstance(result, dict) and all(isinstance(value, ModelObject) for value in result.values()):
            self.result = {key: value.to_primitive() for key, value in result.items()}

        # Otherwise, set the result directly.
        else:
            self.result = result