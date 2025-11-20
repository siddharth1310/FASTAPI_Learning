import pytest

def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1


def test_is_instance():
    assert isinstance("This is a string", str)
    assert not isinstance("10", int)


def test_boolean():
    validated = True
    assert validated is True
    assert ("Hello" == "World") is False


def test_type():
    assert type("Hello" is str)
    assert type("World" is not int)


def test_greater_and_less_than():
    assert 3 > 1
    assert 7 < 10


def test_list():
    num_list = [1, 2, 3, 4, 5, 6, 7]
    any_list = [False, False]
    
    assert 7 in num_list
    assert 8 not in any_list
    
    assert all(num_list)
    assert not any(any_list)


class Student:
    def __init__(self, first_name : str, last_name : str, major : str, years : int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


# 1st version
# def test_person_initialization():
#     p = Student("Siddharth", "Singh", "Computer Science", 4)
#     assert p.first_name == "Siddharth", "First name should be Siddharth"
#     assert p.last_name == "Singh", "Last name should be Singh"
#     assert p.major == "Computer Science"
#     assert p.years == 4

# 2nd Version
@pytest.fixture
def default_employee():
    return Student("Siddharth", "Singh", "Computer Science", 4)

def test_person_initialization(default_employee):
    assert default_employee.first_name == "Siddharth", "First name should be Siddharth"
    assert default_employee.last_name == "Singh", "Last name should be Singh"
    assert default_employee.major == "Computer Science"
    assert default_employee.years == 4