from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    return render(
        request, 'core/404.html', {'path': request.path},
        status=HTTPStatus.NOT_FOUND.value
    )


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def internal_server_error(request, reason=''):
    context = {
        'status': HTTPStatus.INTERNAL_SERVER_ERROR.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.INTERNAL_SERVER_ERROR.value
    )


def not_implemented(request, exception):
    context = {
        'status': HTTPStatus.NOT_IMPLEMENTED.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.NOT_IMPLEMENTED.value
    )


def bad_gateway(request, exception):
    context = {
        'status': HTTPStatus.BAD_GATEWAY.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.BAD_GATEWAY.value
    )


def service_unavailable(request, exception):
    context = {
        'status': HTTPStatus.SERVICE_UNAVAILABLE.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.SERVICE_UNAVAILABLE.value
    )


def gateway_timeout(request, exception):
    context = {
        'status': HTTPStatus.GATEWAY_TIMEOUT.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.GATEWAY_TIMEOUT.value
    )


def http_version_not_supported(request, exception):
    context = {
        'status': HTTPStatus.HTTP_VERSION_NOT_SUPPORTED.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.HTTP_VERSION_NOT_SUPPORTED.value
    )


def variant_also_negotiates(request, exception):
    context = {
        'status': HTTPStatus.VARIANT_ALSO_NEGOTIATES.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.VARIANT_ALSO_NEGOTIATES.value
    )


def insufficient_storage(request, exception):
    context = {
        'status': HTTPStatus.INSUFFICIENT_STORAGE.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.INSUFFICIENT_STORAGE.value
    )


def loop_detected(request, exception):
    context = {
        'status': HTTPStatus.LOOP_DETECTED.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.LOOP_DETECTED.value
    )


def not_extended(request, exception):
    context = {
        'status': HTTPStatus.NOT_EXTENDED.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.NOT_EXTENDED.value
    )


def network_authentication_required(request, exception):
    context = {
        'status': HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED.value
    }
    return render(
        request, 'core/5xx_server_error.html',
        context, {'path': request.path},
        status=HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED.value
    )
