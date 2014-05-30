##############################
Courses API Module
##############################

.. module:: api_manager

The page contains docstrings for:

* `View a List of Courses`_
* `View Course Details`_
* `View Course Content`_


.. _View a List of Courses:

**************************
View a List of Courses
**************************

.. autoclass:: courses.views.CoursesList
    :members:

**Example response**

.. code-block:: json

    HTTP 200 OK  
    Vary: Accept   
    Content-Type: text/html; charset=utf-8   
    Allow: GET, HEAD, OPTIONS 

    [
        {
            "category": "course",   
            "name": "Computer Science 101",   
            "uri": "http://edx-lms-server/api/courses/un/CS/cs101",   
            "number": "CS101",   
            "due": null,   
            "org": "University N",   
            "id": "un/CS/cs101"  
        }
    ]




.. _View Course Details:

**************************
View Course Details
**************************

.. autoclass:: courses.views.CoursesDetail
    :members:


**Example response with no depth parameter**

.. code-block:: json

    HTTP 200 OK  
    Vary: Accept   
    Content-Type: text/html; charset=utf-8   
    Allow: GET, HEAD, OPTIONS 

    {
        "category": "course", 
        "name": "Computer Science 101",   
        "uri": "http://edx-lms-server/api/courses/un/CS/cs101",   
        "number": "CS101",   
        "due": null,   
        "org": "University N",   
        "id": "un/CS/cs101"  
        "resources": [
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/groups/"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/overview"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/updates/"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/static_tabs/"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/users/"
            }
        ]
    }

**Example response with depth=2**

.. code-block:: json

    HTTP 200 OK  
    Vary: Accept   
    Content-Type: text/html; charset=utf-8   
    Allow: GET, HEAD, OPTIONS 

    {
        "category": "course", 
        "name": "Computer Science 101",   
        "uri": "http://edx-lms-server/api/courses/un/CS/cs101",   
        "number": "CS101",
        "content": [
            {
                "category": "chapter", 
                "name": "Introduction", 
                "due": null, 
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/introduction", 
                "id": "i4x://un/cs101/chapter/introduction", 
                "children": [
                    {
                        "category": "sequential", 
                        "due": null, 
                        "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://edX/Open_DemoX/sequential/cs_setup", 
                        "id": "i4x://un/cs101/sequential/cs_setup", 
                        "name": "Course Setup"
                        }
                    ]
            }, 
            {
                "category": "chapter", 
                "name": "Getting Started", 
                "due": null, 
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/getting_started", 
                "id": "i4x://un/cs101/chapter/getting_started", 
                "children": [
                    {
                        "category": "sequential", 
                        "due": null, 
                        "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://edX/Open_DemoX/sequential/sample_problem", 
                        "id": "i4x://un/cs101/sequential/sample_problem", 
                            "name": "Sample Problem"
                    }
                ]
            }, 
        "due": null,   
        "org": "University N",   
        "id": "un/CS/cs101",   
        "resources": [
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/groups/"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/overview"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/updates/"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/static_tabs/"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/users/"
            }
        ]
    }


.. _View Course Content:

**************************
View Course Content
**************************

.. autoclass:: courses.views.CourseContentList
    :members:

**Example response**:

.. code-block:: json

    HTTP 200 OK
    Vary: Accept
    Content-Type: text/html; charset=utf-8
    Allow: GET, HEAD, OPTIONS

    [
        {
            "category": "chapter", 
            "due": null, 
            "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/introduction", 
            "id": "i4x://un/cs101/chapter/introduction", 
            "name": "Introduction"
        }, 
        {
            "category": "chapter", 
            "due": null, 
            "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/getting_started", 
            "id": "i4x://un/cs101/chapter/getting_started", 
            "name": "Getting Started"
        }
    ]
