from collections import defaultdict
from itertools import chain
from typing import List, Type, Tuple

from django.db import models
import pytest
from pytest import Session
from _pytest.config import Config
from _pytest.nodes import Item

from animalconference.models import Animal, Seminar
from datavalidation.registry import REGISTRY, ValidatorInfo
from datavalidation.results import SummaryEx
from datavalidation.runner import ModelValidationRunner


import logging
logger = logging.getLogger(__name__)


# def pytest_collection_modifyitems(session: Session, config: Config, items: List[Item]):
#     order = [
#         "animalconference/test_aminals",
#         "animalconference/test_seminars"
#         "datavalidation/test_registry",
#     ]
#     modules = defaultdict(list)
#     for item in items:
#         module = item.parent.name.replace(".py", "")
#         logger.warning(module)
#         modules[module].append(item)
#
#     missing = set(modules.keys()) - set(order)
#     if len(missing) != 0:
#         logger.warning(missing)
#         #raise ValueError(f"please specify order for modules: {', '.join(diff)}")
#     else:
#         items[:] = list(chain(*modules.values()))
#         logger.warning(items)



# noinspection PyUnusedLocal
@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """ add Validators to the test database """
    with django_db_blocker.unblock():
        for modelinfo in REGISTRY.values():
            for valinfo in modelinfo.validators.values():
                valinfo.get_pk()  # creates the record if it doesn't exist


@pytest.fixture(scope="session")
def valid_animals(django_db_blocker):
    """ add 100 valid Animals to the test database """
    # setup
    with django_db_blocker.unblock():
        count = Animal.objects.count()
        if count == 0:
            Animal.objects.populate_database(100)
        elif count != 100:
            logger.info(count)
            raise AssertionError("something went wrong with --reuse-db")


@pytest.fixture(scope="session")
def valid_seminars(django_db_blocker):
    """ add 10 valid Seminars to the test database """
    with django_db_blocker.unblock():
        count = Seminar.objects.count()
        if count == 0:
            Seminar.objects.populate_database(10)
        elif count != 10:
            logger.info(count)
            raise AssertionError("something went wrong with --reuse-db")


def run_validator(model: Type[models.Model], method_name: str) -> SummaryEx:
    """ helper method to run validation for a single method """
    runner = ModelValidationRunner(model, method_names=[method_name])
    result = runner.run()
    assert len(result) == 1
    assert len(result[0]) == 2

    valinfo, summary = result[0]
    assert isinstance(valinfo, ValidatorInfo)
    assert isinstance(summary, SummaryEx)
    return summary
