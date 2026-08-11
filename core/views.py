# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
# from .models import Entity, Banner


# def home(request):
#     return render(request, 'home.html')


# def banner_api(request, slug):
#     entity = get_object_or_404(Entity, slug=slug)
#     banner = Banner.objects.filter(entity=entity, is_active=True).order_by('-created_at').first()
#     if not banner:
#         return JsonResponse({'success': False, 'message': 'No active banner found'})

#     image_url = request.build_absolute_uri(banner.image.url)
#     aspect_ratio = None
#     if banner.height:
#         aspect_ratio = round(banner.width / banner.height, 6) if banner.height else None

#     return JsonResponse({
#         'success': True,
#         'banner': {
#             'image': image_url,
#             'text': banner.text or '',
#             'width': banner.width or 0,
#             'height': banner.height or 0,
#             'aspect_ratio': aspect_ratio,
#         }
#     })
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Entity, Banner


def home(request):
    return render(request, 'home.html')


def banner_api(request, slug):
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = JsonResponse([], safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    entity = get_object_or_404(Entity, slug=slug)
    banners = Banner.objects.filter(entity=entity, is_active=True).order_by('created_at')

    banner_list = [
        {
            'image': request.build_absolute_uri(banner.image.url),
            'title': banner.title or '',
            'text': banner.text or '',
            'link': banner.link or '',
            'width': banner.width or 0,
            'height': banner.height or 0,
            'aspect_ratio': round(banner.width / banner.height, 6) if banner.width and banner.height else None,
        }
        for banner in banners
    ]

    response = JsonResponse(banner_list, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response