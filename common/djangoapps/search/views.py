from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from manager import SearchEngine
from django.http import HttpResponse
import json


@csrf_exempt
def do_search(request, course_id=None):
    results = {
        "error": _("Nothing to search")
    }
    status_code = 500

    try:
        if request.method == 'POST':
            field_dictionary = None
            if course_id:
                field_dictionary = {"course": course_id}
            searcher = SearchEngine.get_search_engine("courseware_index")
            results = searcher.search_string(
                request.POST["search_string"], field_dictionary=field_dictionary)

            # update the data with the right stuff
            for result_data in [result["data"] for result in results["results"]]:
                result_data["url"] = u"/courses/{course_id}/jump_to/{location}".format(
                        course_id=result_data["course"],
                        location=result_data["id"],
                    )

            status_code = 200
    except Exception as err:
        results = {
            "error": str(err)
        }

    return HttpResponse(
        json.dumps(results),
        content_type='application/json',
        status=status_code
    )
