from celery.result import AsyncResult
from django.http import JsonResponse
from django.views import View


class CeleryTaskStatusView(View):

    def get(self, request, *args, **kwargs):
        task_id = request.GET.get("task_id")
        response_data = {"task_id": task_id, "status": None}
        try:
            result = AsyncResult(str(task_id or ""))
        except (TypeError, ValueError):
            result = None
        if getattr(result, "id", None):
            response_data.update({"status": result.status})
        return JsonResponse(response_data)
