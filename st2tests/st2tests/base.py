import sys
import eventlet
import st2tests.config

from unittest2 import TestCase
from oslo.config import cfg
from st2common.models.db import db_setup, db_teardown
import st2common.models.db.reactor as reactor_model
import st2common.models.db.action as action_model
import st2common.models.db.datastore as datastore_model
import st2common.models.db.actionrunner as actionrunner_model

ALL_MODELS = []
ALL_MODELS.extend(reactor_model.MODELS)
ALL_MODELS.extend(action_model.MODELS)
ALL_MODELS.extend(datastore_model.MODELS)
ALL_MODELS.extend(actionrunner_model.MODELS)


class EventletTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        eventlet.monkey_patch(
            os=True,
            select=True,
            socket=True,
            thread=False if '--use-debugger' in sys.argv else True,
            time=True
        )

    @classmethod
    def tearDownClass(cls):
        eventlet.monkey_patch(
            os=False,
            select=False,
            socket=False,
            thread=False,
            time=False
        )


class DbTestCase(TestCase):

    db_connection = None

    @classmethod
    def setUpClass(cls):
        st2tests.config.parse_args()
        DbTestCase.db_connection = db_setup(cfg.CONF.database.db_name, cfg.CONF.database.host,
                                            cfg.CONF.database.port)
        cls.drop_collections()
        DbTestCase.db_connection.drop_database(cfg.CONF.database.db_name)

    @classmethod
    def tearDownClass(cls):
        cls.drop_collections()
        DbTestCase.db_connection.drop_database(cfg.CONF.database.db_name)
        db_teardown()
        DbTestCase.db_connection = None

    @classmethod
    def drop_collections(cls):
        # XXX: Explicitly drop all the collection. Otherwise, artifacts are left over in
        # subsequent tests.
        # See: https://github.com/MongoEngine/mongoengine/issues/566
        # See: https://github.com/MongoEngine/mongoengine/issues/565
        global ALL_MODELS
        for model in ALL_MODELS:
            model.drop_collection()
