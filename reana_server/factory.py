# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask-application factory for Reana-Server."""

import logging

from flask import Flask, current_app
from flask_babelex import Babel
from flask_menu import Menu as FlaskMenu
from flask_oauthlib.client import OAuth as FlaskOAuth
from invenio_accounts import InvenioAccounts
from invenio_accounts.views import blueprint as blueprint_user
from invenio_db import InvenioDB
from invenio_oauthclient import InvenioOAuthClient
from invenio_oauthclient.views.client import blueprint as blueprint_client
from invenio_oauthclient.views.settings import blueprint as blueprint_settings
from reana_commons.config import REANA_LOG_FORMAT, REANA_LOG_LEVEL
from reana_db.database import Session


def create_app(config_mapping=None):
    """REANA Server application factory."""
    logging.basicConfig(level=REANA_LOG_LEVEL, format=REANA_LOG_FORMAT)
    app = Flask(__name__)
    app.config.from_object("reana_server.config")
    if config_mapping:
        app.config.from_mapping(config_mapping)
    app.secret_key = "hyper secret key"

    app.session = Session

    Babel(app)
    FlaskMenu(app)
    InvenioDB(app)
    InvenioAccounts(app)
    FlaskOAuth(app)
    InvenioOAuthClient(app)

    # Register Invenio OAuth endpoints
    app.register_blueprint(blueprint_user)
    app.register_blueprint(blueprint_client)
    app.register_blueprint(blueprint_settings)

    # Register API routes
    from .rest import (
        config,
        gitlab,
        ping,
        secrets,
        status,
        users,
        workflows,
        workspaces,
    )  # noqa

    app.register_blueprint(ping.blueprint, url_prefix="/api")
    app.register_blueprint(workflows.blueprint, url_prefix="/api")
    app.register_blueprint(users.blueprint, url_prefix="/api")
    app.register_blueprint(secrets.blueprint, url_prefix="/api")
    app.register_blueprint(gitlab.blueprint, url_prefix="/api")
    app.register_blueprint(config.blueprint, url_prefix="/api")
    app.register_blueprint(status.blueprint, url_prefix="/api")
    app.register_blueprint(workspaces.blueprint, url_prefix="/api")

    @app.teardown_appcontext
    def shutdown_session(response_or_exc):
        """Close session on app teardown."""
        current_app.session.remove()
        return response_or_exc

    return app
