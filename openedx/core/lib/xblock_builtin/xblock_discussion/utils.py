"""
Utils for Discussion XBlock and Course Discussion XBlock
"""

from django.templatetags.static import static


JS_URLS = [
    # VENDOR
    'js/vendor/mustache.js',

    # FIXME: Provides gettext, ngettext, interpolate; these are probably already available?
    'xblock/discussion/js/vendor/i18n.js',
]


def _(text):
    """
    A noop underscore function that marks strings for extraction.
    """
    return text


def add_resources_to_fragment(fragment):
    """
    Add resources specified in JS_URLS to a given fragment.
    """
    for url in JS_URLS:
        fragment.add_javascript_url(asset_to_static_url(url))


def asset_to_static_url(asset_path):
    """
    :param str asset_path: path to asset
    :return: str|unicode url of asset
    """
    return static(asset_path)
