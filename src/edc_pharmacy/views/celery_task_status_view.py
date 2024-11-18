from celery.result import AsyncResult
from django.http import JsonResponse
from django.views import View


class CeleryTaskStatusView(View):

    def get(self, request, *args, **kwargs):
        task_id = request.GET.get("task_id")
        try:
            result = AsyncResult(str(task_id or ""))
        except (TypeError, ValueError):
            result = None
        if getattr(result, "id", None):
            return JsonResponse(
                {"task_id": result.id, "status": result.status, "result": result.result}
            )
        return JsonResponse({"error": "No task_id provided"}, status=400)
