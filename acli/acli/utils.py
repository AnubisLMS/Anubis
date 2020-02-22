import functools
import json


def display(res):
    """
    This is used by the command wrapper to pretty print the json response
    for a request.

    :res: requests response object
    """
    if res.status_code == 200:
        print(json.dumps(res.json(), indent=2))
    else:
        print(res.status_code, res.content.decode())


def command(function):
    """
    This descriptor should be used on any function that handles a command.
    When the funtion returns the requests response object, this wrapper passes
    it to the display function. That will pretty print the response.

    :function: function to wrap
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        res = function(*args, **kwargs)
        display(res)
        return res
    return wrapper
