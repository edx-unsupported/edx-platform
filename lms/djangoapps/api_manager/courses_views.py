""" API implementation for course-oriented interactions. """

from lxml import etree
from StringIO import StringIO
from collections import OrderedDict
import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api_manager.permissions import ApiKeyHeaderPermission
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import Location, InvalidLocationError

from courseware.courses import get_course_about_section, get_course_info_section
from courseware.views import get_static_tab_contents

log = logging.getLogger(__name__)

def _get_module_submodules(module, submodule_type=None):
    """
    Parses the provided module looking for child modules
    Matches on submodule type (category) when specified
    """
    submodules = []
    if hasattr(module, 'children'):
        child_modules = module.get_children()
        for child_module in child_modules:
            if submodule_type:
                if getattr(child_module, 'category') == submodule_type:
                    submodules.append(child_module)
            else:
                submodules.append(child_module)
    return submodules


def _serialize_module(request, course_id, module):
    """
    Loads the specified module data into the response dict
    This should probably evolve to use DRF serializers
    """
    data = {}

    if getattr(module, 'id') == course_id:
        module_id = module.id
    else:
        module_id = module.location.url()
    data['id'] = module_id

    if hasattr(module, 'display_name'):
        data['name'] = module.display_name

    data['category'] = module.location.category

    protocol = 'http'
    if request.is_secure():
        protocol = protocol + 's'
    module_uri = '{}://{}/api/courses/{}'.format(
        protocol,
        request.get_host(),
        course_id.encode('utf-8')
    )

    # Some things we do only if the module is a course
    if (course_id == module_id):
        data['number'] = module.location.course
        data['org'] = module.location.org

    # Other things we do only if the module is not a course
    else:
        module_uri = '{}/modules/{}'.format(module_uri, module_id)
    data['uri'] = module_uri

    return data


def _serialize_module_submodules(request, course_id, submodules):
    """
    Loads the specified module submodule data into the response dict
    This should probably evolve to use DRF serializers
    """
    data = []
    if submodules:
        for submodule in submodules:
            submodule_data = _serialize_module(
                request,
                course_id,
                submodule
            )
            data.append(submodule_data)
    return data


@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def modules_list(request, course_id, module_id=None):
    """
    GET retrieves the list of submodules for a given module
    We don't know where in the module hierarchy we are -- could even be the top
    """
    if module_id is None:
        module_id = course_id
    response_data = []
    submodule_type = request.QUERY_PARAMS.get('type', None)
    store = modulestore()
    if course_id != module_id:
        try:
            module = store.get_instance(course_id, Location(module_id))
        except InvalidLocationError:
            module = None
    else:
        module = store.get_course(course_id)
    if module:
        submodules = _get_module_submodules(module, submodule_type)
        response_data = _serialize_module_submodules(
            request,
            course_id,
            submodules
        )
        status_code = status.HTTP_200_OK
    else:
        status_code = status.HTTP_404_NOT_FOUND
    return Response(response_data, status=status_code)


@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def modules_detail(request, course_id, module_id):
    """
    GET retrieves an existing module from the system
    """
    store = modulestore()
    response_data = {}
    submodule_type = request.QUERY_PARAMS.get('type', None)
    if course_id != module_id:
        try:
            module = store.get_instance(course_id, Location(module_id))
        except InvalidLocationError:
            module = None
    else:
        module = store.get_course(course_id)
    if module:
        response_data = _serialize_module(
            request,
            course_id,
            module
        )
        submodules = _get_module_submodules(module, submodule_type)
        response_data['modules'] = _serialize_module_submodules(
            request,
            course_id,
            submodules
        )
        status_code = status.HTTP_200_OK
    else:
        status_code = status.HTTP_404_NOT_FOUND
    return Response(response_data, status=status_code)


@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def courses_list(request):
    """
    GET returns the list of available courses
    """
    response_data = []
    store = modulestore()
    course_descriptors = store.get_courses()
    for course_descriptor in course_descriptors:
        course_data = _serialize_module(
            request,
            course_descriptor.id,
            course_descriptor
        )
        response_data.append(course_data)
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def courses_detail(request, course_id):
    """
    GET retrieves an existing course from the system
    """
    response_data = {}
    store = modulestore()
    try:
        course_descriptor = store.get_course(course_id)
    except ValueError:
        course_descriptor = None
    if course_descriptor:
        response_data = _serialize_module(
            request,
            course_descriptor.id,
            course_descriptor
        )
        submodules = _get_module_submodules(course_descriptor, None)
        response_data['modules'] = _serialize_module_submodules(
            request,
            course_id,
            submodules
        )
        status_code = status.HTTP_200_OK
    else:
        status_code = status.HTTP_404_NOT_FOUND
    return Response(response_data, status=status_code)


def _inner_content(tag):
    """
    Helper method
    """
    inner_content = None
    if tag is not None:
        inner_content = tag.text if tag.text else u''
        inner_content += u''.join(etree.tostring(e) for e in tag)
        inner_content += tag.tail if tag.tail else u''

    return inner_content

def _parse_overview_html(html):
    """
    Helper method to break up the course about HTML into components
    """
    result = {}

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser)

    sections = tree.findall('/body/section')

    result = []
    for section in sections:
        section_class = section.get('class')
        if section_class:
            section_data = OrderedDict()
            section_data['class'] = section_class

            articles = section.findall('article')
            if articles:
                section_data['articles'] = []
                for article in articles:
                    article_class = article.get('class')
                    if article_class:
                        article_data = OrderedDict()
                        article_data['class'] = article_class

                        if article_class == "teacher":

                            name_element = article.find('h3')
                            if name_element is not None:
                                article_data['name'] = name_element.text

                            image_element = article.find("./div[@class='teacher-image']/img")
                            if image_element is not None:
                                article_data['image_src'] = image_element.get('src')

                            bios = article.findall('p')
                            bio_html = ''
                            for bio in bios:
                                bio_html += etree.tostring(bio)

                            if bio_html:
                                article_data['bio'] = bio_html
                        else:
                            article_data['body'] = _inner_content(article)

                        section_data['articles'].append(article_data)
            else:
                section_data['body'] = _inner_content(section)

            result.append(section_data)

    return result


@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def course_overview(request, course_id):
    """
    GET retrieves the course overview module, which - in MongoDB - is stored with the following
    naming convention {"_id.org":"i4x", "_id.course":<course_num>, "_id.category":"about", "_id.name":"overview"}
    """
    store = modulestore()
    response_data = OrderedDict()

    try:
        course_module = store.get_course(course_id)
        if not course_module:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        content = get_course_about_section(course_module, 'overview')

        if request.GET.get('parse') and request.GET.get('parse') in ['True', 'true']:
            try:
                response_data['sections'] = _parse_overview_html(content)
            except:
                log.exception(
                    u"Error prasing course overview. Content = {0}".format(
                        content
                    ))
                return Response({'err': 'could_not_parse'}, status=status.HTTP_409_CONFLICT)
        else:
            response_data['overview_html'] = content

    except InvalidLocationError:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    return Response(response_data)


def _parse_updates_html(html):
    """
    Helper method to break up the course updates HTML into components
    """
    result = {}

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser)

    # get all of the individual postings
    postings = tree.findall('/body/ol/li')

    result = []
    for posting in postings:
        posting_data = {}
        posting_date_element = posting.find('h2')
        if posting_date_element is not None:
            posting_data['date'] = posting_date_element.text

        content = u''
        for el in posting:
            # note, we can't delete or skip over the date element in
            # the HTML tree because there might be some tailing content
            if el != posting_date_element:
                content += etree.tostring(el)
            else:
                content += el.tail if el.tail else u''

        posting_data['content'] = content.strip()
        result.append(posting_data)

    return result


@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def course_updates(request, course_id):
    """
    GET retrieves the course overview module, which - in MongoDB - is stored with the following
    naming convention {"_id.org":"i4x", "_id.course":<course_num>, "_id.category":"course_info", "_id.name":"updates"}
    """
    store = modulestore()
    response_data = OrderedDict()

    try:
        course_module = store.get_course(course_id)
        if not course_module:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        content = get_course_info_section(request, course_module, 'updates')

        if not content:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        if request.GET.get('parse') and request.GET.get('parse') in ['True', 'true']:
            try:
                response_data['postings'] = _parse_updates_html(content)
            except:
                log.exception(
                    u"Error prasing course updates. Content = {0}".format(
                        content
                    ))
                return Response({'err': 'could_not_parse'}, status=status.HTTP_409_CONFLICT)
        else:
            response_data['content'] = content

    except InvalidLocationError:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    return Response(response_data)


@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def static_tabs_list(request, course_id):
    """
    GET returns an array of Static Tabs inside of a course
    """
    store = modulestore()
    response_data = OrderedDict()

    try:
        course_module = store.get_course(course_id)
        if not course_module:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        tabs = []
        for tab in course_module.tabs:
            if tab.type == 'static_tab':
                tab_data = OrderedDict()
                tab_data['id'] = tab.url_slug
                tab_data['name'] = tab.name
                if request.GET.get('detail') and request.GET.get('detail') in ['True', 'true']:
                    tab_data['content'] = get_static_tab_contents(request,
                        course_module,
                        tab,
                        wrap_xmodule_display=False
                    )

                tabs.append(tab_data)

        response_data['tabs'] = tabs

    except InvalidLocationError:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    return Response(response_data)


@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def static_tab_detail(request, course_id, tab_id):
    """
    GET returns an array of Static Tabs inside of a course
    """
    store = modulestore()
    response_data = OrderedDict()

    try:
        course_module = store.get_course(course_id)
        if not course_module:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        for tab in course_module.tabs:
            if tab.type == 'static_tab' and tab.url_slug == tab_id:
                response_data['id'] = tab.url_slug
                response_data['name'] = tab.name
                response_data['content'] = get_static_tab_contents(request,
                    course_module,
                    tab,
                    wrap_xmodule_display=False
                )

    except InvalidLocationError:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    if not response_data:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    return Response(response_data)
