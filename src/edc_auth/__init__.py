def slugify_user(user):
    return f"{user.first_name}-{user.last_name}-{user.username}-{user.email}"
