def insert_into_domain(domain: str, subdomain: str):
    as_list = domain.split(".")
    if subdomain not in as_list:
        as_list.insert(1, subdomain)  # after the site name
    return ".".join(as_list)
