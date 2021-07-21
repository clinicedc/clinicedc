from .tmg import tmg

tmg_review = [
    c for c in tmg if ("view_" in c or "edc_nav" in c or "edc_dashboard" in c)
]
