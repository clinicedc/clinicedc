from django.contrib import messages


def update_query_rules_action(modeladmin, request, queryset):

    total_created = 0
    total_resolved = 0
    for obj in queryset:
        created, resolved = obj.update_queries()
        total_created += created
        total_resolved += resolved
    msg = (
        f"Done updating data queries. "
        f"{total_created} were created, {total_resolved} were resolved."
    )

    messages.add_message(request, messages.SUCCESS, msg)


update_query_rules_action.short_description = "Create or update automated queries"
