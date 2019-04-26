# ICE
In-house Continuing Education (ICE) is a Web Application for registered users to create or access courses through a standard browser.

## Installation
Dependencies: django, django-crispy-forms, pillow, requests

Please run the following commands and install the missing dependencies if it fails to run:
pipenv shell
pipenv install [dependencies-name]

## Usage
Run `python manage.py migrate` to ensure database is up to date.
Run `python manage.py runserver` to launch ICE and it is accessible on http://127.0.0.1:8000/

## Functionality Missing / To Be Fixed:
(for Instructors) <When adding a module to a course> Indicate a position for insertion;
The name of the foreign key of Learner and Instructor should be User
