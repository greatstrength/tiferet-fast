'''Calculator validation utility.'''

# *** imports

# ** infra
from tiferet.events import RaiseError


# *** utils

# ** util: calc_util
class CalcUtil:
    '''
    Utility for validating numeric inputs.
    '''

    # * method: verify_number (static)
    @staticmethod
    def verify_number(value: str) -> int | float:
        '''
        Verify that the value can be converted to an integer or float.

        :param value: The value to verify.
        :type value: str
        :return: The numeric value as an integer or float.
        :rtype: int | float
        '''

        # Check if the value is a valid number.
        is_valid = isinstance(value, str) and (
            value.isdigit()
            or (value.replace('.', '', 1).isdigit() and value.count('.') < 2)
        )

        # Raise error if invalid.
        if not is_valid:
            RaiseError.execute(
                error_code='INVALID_INPUT',
                value=value,
            )

        # If valid, return the value as a float or int.
        if '.' in value:
            return float(value)
        return int(value)
