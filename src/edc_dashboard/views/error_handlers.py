from django.template.response import TemplateResponse


def edc_handler400(request, exception=None):
    """400 error handler which includes ``request`` in the context.

    Templates: `400.html`
    Context: None
    """

    context = {"request": request, "message": "bad request", "code": 400}
    template_name = "400.html"  # You need to create a 400.html template.
    return TemplateResponse(request, template_name, context, status=400)


def edc_handler403(request, exception=None):
    """403 error handler which includes ``request`` in the context.

    Templates: `403.html`
    Context: None
    """

    context = {"request": request, "message": "permission denied", "code": 403}
    template_name = "403.html"  # You need to create a 403.html template.
    return TemplateResponse(request, template_name, context, status=403)


def edc_handler404(request, exception=None):
    """404 error handler which includes ``request`` in the context.

    Templates: `404.html`
    Context: None
    """

    context = {"request": request, "message": "page not found", "code": 404}
    template_name = "404.html"  # You need to create a 404.html template.
    return TemplateResponse(request, template_name, context, status=404)


def edc_handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """

    context = {"request": request, "message": "server error", "code": 500}
    template_name = "500.html"  # You need to create a 500.html template.
    return TemplateResponse(request, template_name, context, status=500)
