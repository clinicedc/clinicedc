from ..codenames.navbars import navbars

navbar_tuples = []
for codename in navbars:
    navbar_tuples.append((codename, f"Can access {codename.split('.')[1]}"))
