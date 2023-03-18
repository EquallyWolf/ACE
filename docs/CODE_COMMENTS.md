<div align="center">

# Code Comments

</div>

This document is intended to help you write code comments. It will cover the following topics:

-   [Module docstrings](#module-docstrings)
-   [Class docstrings](#class-docstrings)
-   [Function docstrings](#function-docstrings)
-   [Inline comments](#inline-comments)

When writing code comments using the style outlined in the below sections, you must follow the [PEP 257](https://www.python.org/dev/peps/pep-0257/) and [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guides.

## Module docstrings

You must add a docstring to the top of each module to describe what the module does.

It must also describe the classes and functions available.

Each class and function must be separated by a line, and each class and function must have a short description underneath.

The docstring must be formatted as follows:

```python
"""
<Description of the module>

#### Classes:

<ClassName>:
    <Description of the class>

...

#### Functions:

<function_name>:
    <Description of the function>

...
"""
```

If there are no classes and/or functions, the docstring must be formatted as follows:

```python
"""
<Description of the module>

#### Classes: None

#### Functions: None
"""
```

## Class docstrings

Each class must have a docstring to describe what the class does and describe the class's parameters and methods available.

Each parameter and method must be separated by a line, and each parameter and method must have a short description underneath.

The docstring must be formatted as follows:

```python
class ClassName:
    """
    <Description of the class>

    #### Parameters:

    <parameter_name>:
        <Description of the parameter>

    ...

    #### Methods:

    <method_name>:
        <Description of the method>

    ...
    """
```

If there are no parameters and/or methods, the docstring must be formatted as follows:

```python
class ClassName:
    """
    <Description of the class>

    #### Parameters: None

    #### Methods: None
    """
```

## Function docstrings

Each function must have a docstring to describe what the function does and describe the function's parameters and return value.

It must also describe any exceptions that may be raised.

Each parameter must be separated by a line, and each parameter must have a short description underneath.

The docstring must be formatted as follows:

```python
def function_name(parameter1: str, parameter2: int) -> str:
    """
    <Description of the function>

    #### Parameters:

    <parameter_name>:
        <Description of the parameter>

    ...

    #### Returns: <return_type>
        <Description of the return value>

    #### Raises:

    <exception_name>:
        <Description of the exception>

    ...
    """
```

If there are no parameters and/or return value, the docstring must be formatted as follows:

```python
def function_name() -> None:
    """
    <Description of the function>

    #### Parameters: None

    #### Returns: None

    #### Raises: None
    """
```

## Inline comments

You must add comments throughout the code to explain what each line or section does.

Make sure to use proper grammar and punctuation, the comment is not too long and there are not too many comments.

If the comment is too long, you can split it into multiple lines.
