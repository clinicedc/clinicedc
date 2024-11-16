from celery.result import AsyncResult
from django.http import JsonResponse
from django.views import View


class CeleryTaskStatusView(View):

    def get(self, request, *args, **kwargs):
        task_id = request.GET.get("task_id")
        if task_id:
            result = AsyncResult(task_id)
            return JsonResponse(
                {"task_id": task_id, "status": result.status, "result": result.result}
            )
        return JsonResponse({"error": "No task_id provided"}, status=400)
