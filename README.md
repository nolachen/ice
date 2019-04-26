# ICE
In-house Continuing Education (ICE) is a Web Application for registered users to create or access courses through a standard browser.

## Installation
Dependencies: python==3.7, django==2.2, django-crispy-forms==1.7.2, pillow=6.0.0, requests==2.21.0

Please run the following commands and install the missing dependencies if it fails to run:
1. `pipenv shell`
2. `pipenv install [dependencies-name]`

## Usage
1. Run `python manage.py migrate` to ensure database is up to date.
2. Run `python manage.py runserver` to launch ICE and it is accessible on http://127.0.0.1:8000/

## Functionality Missing / To Be Fixed:
1. (for Instructors) <When adding a module to a course> Indicate a position for insertion.
2. The name of the foreign key of Learner and Instructor should be User for easier understanding.
