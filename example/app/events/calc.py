'''Calculator arithmetic domain events.'''

# *** imports

# ** core
from typing import Any

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..utils.calc import CalcUtil


# *** events

# ** event: add_number
class AddNumber(DomainEvent):
    '''
    A domain event to perform addition of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the addition event.

        :param a: The first operand.
        :type a: Any
        :param b: The second operand.
        :type b: Any
        :return: The sum of a and b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = CalcUtil.verify_number(str(a))
        b_verified = CalcUtil.verify_number(str(b))

        # Add verified values.
        result = a_verified + b_verified

        # Return the result.
        return result


# ** event: subtract_number
class SubtractNumber(DomainEvent):
    '''
    A domain event to perform subtraction of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the subtraction event.

        :param a: The first operand.
        :type a: Any
        :param b: The second operand.
        :type b: Any
        :return: The difference of a and b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = CalcUtil.verify_number(str(a))
        b_verified = CalcUtil.verify_number(str(b))

        # Subtract verified values.
        result = a_verified - b_verified

        # Return the result.
        return result


# ** event: multiply_number
class MultiplyNumber(DomainEvent):
    '''
    A domain event to perform multiplication of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the multiplication event.

        :param a: The first operand.
        :type a: Any
        :param b: The second operand.
        :type b: Any
        :return: The product of a and b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = CalcUtil.verify_number(str(a))
        b_verified = CalcUtil.verify_number(str(b))

        # Multiply verified values.
        result = a_verified * b_verified

        # Return the result.
        return result


# ** event: divide_number
class DivideNumber(DomainEvent):
    '''
    A domain event to perform division of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the division event.

        :param a: The numerator.
        :type a: Any
        :param b: The denominator (must be non-zero).
        :type b: Any
        :return: The quotient of a and b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = CalcUtil.verify_number(str(a))
        b_verified = CalcUtil.verify_number(str(b))

        # Verify non-zero denominator.
        self.verify(b_verified != 0, 'DIVISION_BY_ZERO')

        # Divide verified values.
        result = a_verified / b_verified

        # Return the result.
        return result


# ** event: exponentiate_number
class ExponentiateNumber(DomainEvent):
    '''
    A domain event to perform exponentiation of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the exponentiation event.

        :param a: The base.
        :type a: Any
        :param b: The exponent.
        :type b: Any
        :return: The result of a raised to the power of b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = CalcUtil.verify_number(str(a))
        b_verified = CalcUtil.verify_number(str(b))

        # Exponentiate verified values.
        result = a_verified ** b_verified

        # Return the result.
        return result
