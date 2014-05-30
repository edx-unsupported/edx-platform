###############################
edX ReST API Resources
###############################

**********
Courses
**********

.. list-table::
   :widths: 20 60
   :header-rows: 1

   * - Goal
     - Resource
   * - :ref:`View a List of Courses`
     - GET /api/courses
   * - :ref:`View Course Content`
     - GET /api/courses/{course_id}/content?type=content_type
   * - :ref:`View Course Details`
     - GET /api/courses/{course_id}?depth=n