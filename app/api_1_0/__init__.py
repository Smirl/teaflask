from flask import Blueprint, request, current_app

api = Blueprint('api', __name__)


def paginate(query, page):
    """Helper for making pagination objects."""
    return query.paginate(
        page,
        per_page=request.args.get(
            'limit',
            current_app.config['TEAFLASK_PER_PAGE'],
            type=int
        ),
        error_out=False
    )


# Must be below the other code
from . import authentication, pots, brewers, teas, errors
