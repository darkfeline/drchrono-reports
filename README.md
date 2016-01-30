drchrono-reports
================

drchrono-reports is a Django app that uses [drchrono's API][] to calculate and
view how often clinical note fields are filled out.

[drchrono]: (https://www.drchrono.com/)

Dependencies
------------

- Python 2
- Django 1.8
- django-bootstrap3

Installation and configuration
------------------------------

Install all of the dependencies.

drchrono-reports is distributed as a Django app, which is installed as follows:

1. Copy the `reports` directory to your project.
2. Enable the app in your project's `settings.py`, along with `bootstrap3`
   (django-bootstrap3):

        INSTALLED_APPS = (
            # ...
            'reports',
            'bootstrap3',
        )

3. Configure the app in your project's `urls.py`, with the namespace
   `drchrono_birthday`:

        urlpatterns = [
            # ...
            url(r'^reports/', include('reports.urls',
                                      namespace="reports")),
        ]

5. Set up your drchrono API key and OAuth client secrets file.  An example file
   is included.  Refer to drchrono for information about obtaining the API key.

   Put this file somewhere and configure drchrono Birthday with the path in
   your site's `settings.py`:

        DRCHRONO_REPORTS_SECRETS = "/path/to/secrets.json"

drchrono Birthday relies on Django's native authentication library.  User
authentication and/or registration should be handled by your site.

License
-------

Copyright (C) 2016  Allen Li

This file is part of drchrono Birthday.

drchrono Birthday is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

drchrono Birthday is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with drchrono Birthday.  If not, see <http://www.gnu.org/licenses/>.
