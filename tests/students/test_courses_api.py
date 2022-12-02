import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory

@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory

@pytest.mark.django_db
def test_retrieve_course(client, course_factory):
    #создадим 10 курсов, будем получать по индексу 3
    courses = course_factory(_quantity=10)

    course = courses[3]
    url ='/api/v1/courses/' + str(course.id) + '/'

    response = client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert data['name'] == course.name
    assert data['id'] == course.id

@pytest.mark.django_db
def test_list_course(client, course_factory):

    courses = course_factory(_quantity=10)

    count = Course.objects.count()

    response = client.get('/api/v1/courses/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == count
    for index, course in enumerate(data):
        assert course['name'] == courses[index].name

@pytest.mark.django_db
def test_list_course_filter_id(client, course_factory):

    # создадим 10 курсов, будем получать по индексу 3
    courses = course_factory(_quantity=10)

    course = courses[3]
    url = '/api/v1/courses/?id=' + str(course.id)

    response = client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == course.name
    assert data[0]['id'] == course.id

@pytest.mark.django_db
def test_list_course_filter_name(client, course_factory):
    # создадим 10 курсов, будем получать по индексу 3
    courses = course_factory(_quantity=10)

    course = courses[3]
    url = '/api/v1/courses/?name=' + str(course.name)

    response = client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == course.name
    assert data[0]['id'] == course.id

@pytest.mark.django_db
def test_create_course(client):
    count = Course.objects.count()

    st1 = Student.objects.create(name='Ivan')
    st2 = Student.objects.create(name='Tamara')

    response = client.post('/api/v1/courses/', data={'name': 'Python разработка',
                                                     'students': [st1.id, st2.id]}, format='json')
    data = response.json()

    assert response.status_code == 201
    assert data['name'] == 'Python разработка'
    assert len(data['students']) == 2
    assert Course.objects.count() == count + 1

@pytest.mark.django_db
def test_update_course(client, course_factory, student_factory):
    # создадим 10 курсов, будем получать по индексу 3
    courses = course_factory(_quantity=10)
    students = student_factory(_quantity=2)

    course = courses[3]

    url = '/api/v1/courses/' + str(course.id) + '/'

    response = client.put(url, data={'name': 'test',
                                     'students': [students[0].id, students[1].id]})
    data = response.json()

    assert response.status_code == 200
    assert data['name'] == 'test'
    assert len(data['students']) == 2
    assert data['students'][0] == students[0].id

@pytest.mark.django_db
def test_delete_course(client, course_factory, student_factory):
    # создадим 10 курсов, будем получать по индексу 3
    courses = course_factory(_quantity=10)

    count = Course.objects.count()

    course = courses[3]

    url = '/api/v1/courses/' + str(course.id) + '/'

    response = client.delete(url)

    assert response.status_code == 204
    assert Course.objects.count() == count - 1
    assert Course.objects.filter(id=course.id).count() == 0