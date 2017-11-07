import json
import logging
import simplejson as json
import tornado.web

import simplejson as json
from models.jobs import Jobs
from models.profits import Profits
from util.executor import run_async
from util.utilis import get_new_jobs_ids, json_into_modelObject

LOGGER = logging.getLogger(__name__)


class ProfitsHandler(tornado.web.RequestHandler):
    """
    Subclass of ``tornado.web.RequestHandler`` which handles HTTP requests to
    ``/profits`` API endpoint.
    """

    @property
    def database_client(self):
        return self.application.database_client

    @property
    def rabbitmq_client(self):
        return self.application.rabbitmq_client

    def prepare(self):
        self.set_header('Content-Type', 'application/json')

    async def get(self):
        LOGGER.info('*** GET %s (%s)', self.request.uri, self.request.remote_ip)
        with self.database_client.session_factory.auto_session() as session:
            profits = await run_async(session.query(Profits).all)
            response = [profit.dict for profit in profits]
            response_json = json.dumps(response, sort_keys=True)
        self.write(response_json)

    def insert_into_db(self, data):
        data_json = json.loads(data)
        with self.database_client.session_factory.auto_session() as session:
            session.add_all(json_into_modelObject(data_json))
            session.commit()

    async def post(self):
        LOGGER.info('*** GET %s (%s)', self.request.uri, self.request.remote_ip)
        with self.database_client.session_factory.auto_session() as session:
            jobs = await run_async(session.query(Jobs).all)
            profits = await run_async(session.query(Profits).all)
            ids = get_new_jobs_ids(jobs, profits)
            new_jobs = await run_async( session.query(Jobs).filter(Jobs.id.in_(ids)).all)
            response = [new_job.dict for new_job in new_jobs]
            response_json = json.dumps(response, sort_keys=True)
            if response != []:
                data = await (self.rabbitmq_client.call('rpc', response_json))
                self.insert_into_db(data)
            else:
                LOGGER.info('Nothing to do')    


