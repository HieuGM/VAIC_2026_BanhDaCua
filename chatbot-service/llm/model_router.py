from core.enums import Route


def model_for_route(route: Route) -> str:
    if route == Route.FIXED_HYBRID:
        return "complex"
    return "simple"
