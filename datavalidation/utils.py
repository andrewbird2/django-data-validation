from functools import wraps
import itertools
import sys
import time

import inspect
from typing import Callable, Type

from django.db import models
from django.db.models import prefetch_related_objects


def is_class_method(method: Callable, owner: Type) -> bool:
    """ return True if a function is a classmethod """
    assert callable(method) and owner is not None
    return inspect.ismethod(method) and getattr(method, "__self__", None) is owner


# def get_date_modified_field_name(model: Type[models.Model]) -> Optional[str]:
#     """ return the field of the model that hold the date modified """
#     # first check if the user specified it in the Meta class
#     field_name = getattr(model._meta, "date_modified_field", None)
#     if field_name is not None:
#         assert hasattr(model, field_name), f"{model.__name__} has no field {field_name}"
#         return field_name
#
#     # else return an auto_now field
#     for field in model._meta.fields:
#         if getattr(field, "auto_now", False):
#             return field.name


# noinspection PyProtectedMember
def queryset_iterator(queryset: models.QuerySet, chunk_size: int):
    """ QuerySet.iterate with prefetch_related

     QuerySet.iterate silently ignores prefetch_related
     modified from this PR: https://github.com/django/django/pull/10707/files
    """
    iterable = queryset._iterable_class(queryset, chunked_fetch=True, chunk_size=chunk_size)  # noqa E501
    if not queryset._prefetch_related_lookups:
        yield from iterable
        return

    iterator = iter(iterable)
    while True:
        results = list(itertools.islice(iterator, chunk_size))
        if not results:
            break
        prefetch_related_objects(results, *queryset._prefetch_related_lookups)
        yield from iter(results)


def timer(output: Callable):
    """ decorator to record the execution time of a function """
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args, **kwargs):
            # quick and dirty, don't need precision timing
            start_time = time.time()
            ret = func(*args, **kwargs)
            duration = time.time() - start_time
            output(f"Total Execution Time: {duration/1000:.1}s")
            return ret
        return inner
    return wrapper


def sysexit(func: Callable) -> Callable:
    """ use the function return value as the system exit code """
    @wraps(func)
    def wrapper(*args, **kwargs):
        sys.exit(func(*args, **kwargs))
    return wrapper
