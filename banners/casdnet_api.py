from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import CasdnetCategory, CasdnetBanner


def _image_url(request, image):
    if not image:
        return None
    return f"https://manager.promallshop.com{image.url}"


@api_view(["GET"])
@permission_classes([AllowAny])
def casdnet_categories_api(request):
    data = [
        {
            "id": item.id,
            "entity_id": item.entity_id,
            "entity": str(item.entity),
            "title": item.title,
            "image": _image_url(request, item.image),
            "link": item.link,
        }
        for item in CasdnetCategory.objects.all()
    ]
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([AllowAny])
def casdnet_banners_api(request):
    data = [
        {
            "id": item.id,
            "entity_id": item.entity_id,
            "entity": str(item.entity),
            "title": item.title,
            "subtitle": item.subtitle,
            "link": item.link,
            "image": _image_url(request, item.image),
        }
        for item in CasdnetBanner.objects.all()
    ]
    return Response({"results": data})

