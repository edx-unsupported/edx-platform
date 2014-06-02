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
   * - :ref:`Get a List of Courses`
     - GET /api/courses
   * - :ref:`Get Course Content`
     - GET /api/courses/{course_id}/content?type=content_type
   * - :ref:`Get Course Details`
     - GET /api/courses/{course_id}?depth=n
   * - :ref:`Get Content Details`
     - GET /api/courses/{course_id}/content/{content_id}?type=content_type
   * - :ref:`Get a Course Overview`
     - GET /api/courses/{course_id}/overview?parse=true