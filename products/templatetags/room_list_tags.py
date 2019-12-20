from django import template

register = template.Library()


@register.simple_tag
def query_params(page_num, urlencode=None):
    url = f"?page={page_num}"
    if urlencode:
        querystring = urlencode.split("&")
        for query in querystring:
            key, val = query.split("=")
            if key == "page":
                continue
            else:
                url += f"&{key}={val}"
    return url
