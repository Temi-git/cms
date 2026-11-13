from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Brand
from .api_helpers import build_media_url


def serialize_brand_detail(request, brand):
    return {
        "id": brand.id,
        "title": brand.title,
        "slug": brand.slug,
        "short_description": brand.short_description,
        "description": brand.description,
        "image": build_media_url(request, brand.image),
        "entity": {
            "id": brand.entity.id,
            "name": brand.entity.name,
            "slug": brand.entity.slug,
            "url": brand.entity.url,
        },
        "faqs": [
            {
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
            }
            for faq in brand.faqs.all().order_by("id")
        ],
    }


def find_brand(slug):
    return (
        Brand.objects
        .select_related("entity")
        .prefetch_related("faqs")
        .filter(
            slug=slug,
            entity__is_active=True,
        )
        .first()
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_brand_detail_api(request, slug):
    """
    GET /api/promall/brands/<slug>/
    Authenticated Brand detail endpoint.
    """
    brand = find_brand(slug)

    if not brand:
        return Response(
            {
                "status": "error",
                "message": "Brand not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({
        "status": "success",
        "brand": serialize_brand_detail(request, brand),
    })


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def proxy_brand_detail_api(request, slug):
    """
    GET /proxy/promall/brands/<slug>/
    Public Brand detail endpoint.
    """
    brand = find_brand(slug)

    if not brand:
        return Response(
            {
                "status": "error",
                "message": "Brand not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({
        "status": "success",
        "brand": serialize_brand_detail(request, brand),
    })