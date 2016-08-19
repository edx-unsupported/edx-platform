"""
Utils for Discussion XBlock and Course Discussion XBlock
"""

from django.templatetags.static import static


def _(text):
    """
    A noop underscore function that marks strings for extraction.
    """
    return text


def asset_to_static_url(asset_path):
    """
    :param str asset_path: path to asset
    :return: str|unicode url of asset
    """
    return static(asset_path)
