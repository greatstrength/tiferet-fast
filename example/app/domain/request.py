'''Calculator request and response models.'''

# *** imports

# ** infra
from pydantic import Field
from tiferet_openapi import ApiRequestModel, ApiResponseModel


# *** models

# ** model: two_operand_request
class TwoOperandRequest(ApiRequestModel):
    '''
    Request model for two-operand arithmetic operations.
    '''

    # * attribute: a
    a: float = Field(
        ...,
        description='The first operand.',
    )

    # * attribute: b
    b: float = Field(
        ...,
        description='The second operand.',
    )


# ** model: single_operand_request
class SingleOperandRequest(ApiRequestModel):
    '''
    Request model for single-operand operations (e.g., square root).
    '''

    # * attribute: a
    a: float = Field(
        ...,
        description='The operand.',
    )


# ** model: calculator_response
class CalculatorResponse(ApiResponseModel):
    '''
    Response model for calculator operations.
    '''

    # * attribute: result
    result: float = Field(
        ...,
        description='The computation result.',
    )
