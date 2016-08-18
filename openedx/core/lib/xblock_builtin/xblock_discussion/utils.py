from django.templatetags.static import static

def asset_to_static_url(asset_path):
    """
    :param str asset_path: path to asset
    :return: str|unicode url of asset
    """
    return static(asset_path)
