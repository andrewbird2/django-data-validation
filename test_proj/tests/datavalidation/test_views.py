import pytest
import urllib.parse as urlparse
from urllib.parse import urlencode

from django.urls import reverse

from animalconference.models import Animal

from datavalidation.results import Status
from datavalidation.runner import ModelValidationRunner
from datavalidation.viewsets import FailingObjectPagination


HTTP_OK = 200


@pytest.fixture
def auth_client(client, django_user_model):
    username = "admin"
    password = "badmin"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client


def encode_url_with_params(url: str, params: dict) -> str:
    """ add url encoded parameters to a url """
    url_parts = list(urlparse.urlparse(url))
    url_parts[4] = urlencode(params)
    return urlparse.urlunparse(url_parts)


def test_api_csrf_views(auth_client):
    url = reverse("admin:datavalidation_csrf_info")
    resp = auth_client.get(url)
    assert resp.status_code == HTTP_OK
    data = resp.json()
    assert data["csrf_cookie_name"] == "csrftoken"
    assert data["csrf_header_name"] == "X-CSRFTOKEN"


@pytest.mark.django_db
def test_api_object_counts_view(auth_client):
    base_url = reverse("admin:datavalidation_object_counts")

    incomplete_url = encode_url_with_params(
        base_url, params={"appLabel": "animalconference"}
    )
    resp = auth_client.get(incomplete_url)
    assert resp.status_code == 400

    non_model_url = encode_url_with_params(
        base_url, params={"appLabel": "animalconference", "modelName": "foobar"}
    )
    resp = auth_client.get(non_model_url)
    assert resp.status_code == 404

    url = encode_url_with_params(
        base_url,
        params={"appLabel": Animal._meta.app_label,
                "modelName": Animal._meta.model_name}
    )
    resp = auth_client.get(url)
    assert resp.status_code == HTTP_OK
    assert int(resp.content) == 100


@pytest.mark.django_db
def test_rest_api_validator_list(auth_client):
    ModelValidationRunner(Animal, method_names=["check_alliteration"]).run()

    url = reverse("admin:validator-list")
    resp = auth_client.get(url)
    assert resp.status_code == HTTP_OK
    data = resp.json()
    assert isinstance(data, list)
    for validator in data:
        if validator["model_name"] != "Animal":
            continue
        if validator["method_name"] != "check_alliterations":
            continue

        assert validator["is_class_method"] is False
        assert validator["description"] == "test that names are alliterations"
        assert validator["num_passing"] == 100
        assert validator["num_failing"] == 0
        assert validator["num_na"] == 0
        assert validator["num_allowed_to_fail"] == 0
        assert validator["status"] == Status.PASSING
        break


@pytest.mark.django_db
def test_rest_api_failing_objects_pagination(auth_client):
    """ test that failing objects are paginated """
    page_size = FailingObjectPagination.page_size
    for _ in range(page_size + 1):
        Animal.objects.test_create(species="Ant", name="Bob")  # fails
    ModelValidationRunner(Animal, method_names=["check_alliteration"]).run()

    url = reverse("admin:failingobject-list")
    resp = auth_client.get(url)
    assert resp.status_code == HTTP_OK

    data = resp.data
    assert "results" in data
    assert len(data["results"]) == page_size
    assert "next" in data
    next_url = data["next"]
    resp = auth_client.get(next_url)
    assert resp.status_code == HTTP_OK
    assert len(resp.data["results"]) == 1


@pytest.mark.django_db
def test_rest_api_failing_objects_list_for_validator(auth_client):
    """ test the FailingObject API for a given validator """
    animal = Animal.objects.test_create(species="Ant", name="Bob")  # fails
    animal_admin_page = reverse("admin:animalconference_animal_change", args=(animal.id,))

    results = ModelValidationRunner(Animal, method_names=["check_alliteration"]).run()
    valinfo, _ = results[0]
    validator_id = valinfo.get_pk()

    url = encode_url_with_params(
        reverse("admin:failingobject-list"),
        params={"validator_id": validator_id}
    )
    resp = auth_client.get(url)
    assert resp.status_code == HTTP_OK

    data = resp.json()
    assert data["next"] is None
    assert len(data["results"]) == 1

    fobj = data["results"][0]
    assert fobj["object_pk"] == animal.id
    assert fobj["admin_page"] == animal_admin_page
    assert fobj["allowed_to_fail"] is False
    assert fobj["validator"] == validator_id