##############################
Courses API Module
##############################

.. module:: api_manager

The page contains docstrings and example responses for:

* `Get a List of Courses`_
* `Get Course Details`_
* `Get Course Content`_
* `Get Content Details`_
* `Get a Course Overview`_


.. _Get a List of Courses:

**************************
Get a List of Courses
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




.. _Get Course Details:

**************************
Get Course Details
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


.. _Get Course Content:

**************************
Get Course Content
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


.. _Get Content Details:

**************************
Get Content Details
**************************

.. autoclass:: courses.views.CourseContentDetail
    :members:

**Example response**:

.. code-block:: json

    HTTP 200 OK
    Vary: Accept
    Content-Type: text/html; charset=utf-8
    Allow: GET, HEAD, OPTIONS

    {
        "category": "chapter", 
        "due": null, 
        "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/introduction", 
        "id": "i4x://un/cs101/chapter/introduction", 
        "name": "Introduction"
        "children": [
            {
                "category": "sequential", 
                "due": null, 
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/introduction/sequential/19a30717eff543078a5d94ae9d6c18a5", 
                "id": "i4x://un/cs101/chapter/introduction/sequential/19a30717eff543078a5d94ae9d6c18a5", 
                "name": "Lesson 1 - Getting Started"
            }, 
            {
                "category": "sequential", 
                "due": null, 
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/introduction/sequential/basic_questions", 
                "id": "i4x://un/cs101/chapter/introduction/sequential/basic_questions", 
                "name": "Homework - Basic Questions"
            }
        ], 
        "resources": [
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/introduction/users"
            }, 
            {
                "uri": "http://edx-lms-server/api/courses/un/CS/cs101/content/i4x://un/cs101/chapter/introduction/groups"
            }
        ]
    }

.. _Get a Course Overview:

**************************
Get a Course Overview
**************************

.. autoclass:: courses.views.CoursesOverview
    :members:

**Example response with no parse parameter**:

.. code-block:: json

    HTTP 200 OK
    Vary: Accept
    Content-Type: text/html; charset=utf-8
    Allow: GET, HEAD, OPTIONS

    { "overview_html": "\n\n<section class=\"about\">\n   <h2>About This
        Course</h2>\n   <p>This course is about . . .</p>\n </section>\n\n
        <section class=\"prerequisites\">\n   <h2>Prerequisites</h2>\n
        <p>Course prerequisites are: a, b, c</p>\n </section>\n\n <section class
        =\"course-staff\">\n   <h2>Course Staff</h2>\n   <article
        class=\"teacher\">\n     <div class=\"teacher-image\">\n       <img
        src=\"/static/images/pl-faculty.png\" align=\"left\" style=\"margin:0 20
        px 0\">\n     </div>\n\n     <h3>Staff Member #1</h3>\n     <p>Biography
        of . . .</p>\n   </article>\n\n   <article class=\"teacher\">\n     <div
        class=\"teacher-image\">\n       <img src=\"/static/images/pl-
        faculty.png\" align=\"left\" style=\"margin:0 20 px 0\">\n
        </div>\n\n     <h3>Staff Member #2</h3>\n     <p>Biography of . .
        .</p>\n   </article>\n </section>\n\n <section class=\"faq\">\n
        <section class=\"responses\">\n     <h2>Frequently Asked
        Questions</h2>\n     <article class=\"response\">\n       <h3>Do I need
        to buy a textbook?</h3>\n       <p>No</p>\n     </article>\n\n
        <article class=\"response\">\n       <h3>Question #2</h3>\n
        <p>Answer here . . .</p>\n     </article>\n   </section>\n
        </section>\n\n\n" 
    }

**Example response when parse is true**:

.. code-block:: json

    HTTP 200 OK
    Vary: Accept
    Content-Type: text/html; charset=utf-8
    Allow: GET, HEAD, OPTIONS

    {
        "sections": [
            {
                "class": "about", 
                "body": "<h2>About This Course</h2>\n
                <p>This course is about . . .</p>\n "
            }, 
            {
                "class": "prerequisites", 
                "body": "<h2>Prerequisites</h2>\n   
                <p>Course prerequisites are: a, b, c</p>\n "
            }, 
            {
                "class": "course-staff", 
                "articles": [
                    {
                        "class": "teacher", 
                        "name": "Staff Member #1", 
                        "image_src": "/static/images/pl-faculty.png", 
                        "bio": "<p>Biography of . . .</p>\n   "
                    }, 
                    {
                        "class": "teacher", 
                        "name": "Staff Member #2", 
                        "image_src": "/static/images/pl-faculty.png", 
                        "bio": "<p>Biography of . . .</p>\n   "
                    }
                ]
            }, 
            {
                "class": "faq", 
                "body": "<section class=\"responses\">
                <h2>Frequently Asked Questions</h2>\n     
                <article class=\"response\">
                <h3>Do I need to buy a textbook?</h3>\n       
                <p>No</p>\n     
                </article>
                <article class=\"response\"><h3>Question #2</h3>\n      
                <p>Answer here . . .</p>\n     
                </article>
                </section>"
            }
        ]
    }