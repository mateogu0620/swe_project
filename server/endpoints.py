"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from flask import Flask, request
from flask_restx import Resource, Api, fields
from scraper import scraper
from db import db

app = Flask(__name__)
api = Api(app)

''' #Shelving the client connection for now, pivoting to Data API

client = MongoClient('localhost', 27017)
# Username: Cluster08493
# Password: RlhRbmFKSH1E
db = client.flask_db  # creating mongoDB instance
collection = db.collec
'''

LIST = 'list'
HELLO = '/hello'
MESSAGE = 'message'
TM = "TICKETMASTER"
SG = "SEATGEEK"
TM_GET_EVENTS = '/tm_get_events'
SG_GET_EVENTS = '/sg_get_events'
GET_EVENTS = '/get_events'
MG_GET_DOCUMENT = '/mg_get_document'
MG_INSERT_DOCUMENT = '/mg_insert_document'
MG_DELETE_DOCUMENT = '/mg_delete_document'
MG_GET_MANY = '/mg_get_many'
ALL_INSERT = '/all_insert'
ALL_CLEAR = '/all_clear'
GET_AND_CONVERT = '/get_and_convert'
FILTER = 'filter'
EVENTS = 'events'
DOCUMENT = 'document'
DOCUMENTS = 'documents'
INSERTED_ID = 'insertedId'
INSERTED_IDS = 'insertedIds'
DELETED_COUNT = 'deletedCount'


@api.route(HELLO)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {MESSAGE: 'hello world'}


tm_event_fields = api.model('TMGetEvents', {
    scraper.POSTAL_CODE: fields.Integer,
    scraper.MAX_PRICE: fields.Integer,
    scraper.START_DATE: fields.DateTime,
    scraper.END_DATE: fields.DateTime,
    scraper.SIZE: fields.Integer
})

sg_event_fields = api.model('SGGetEvents', {
    scraper.POSTAL_CODE: fields.Integer,
    scraper.MAX_PRICE: fields.Integer,
    scraper.START_DATE: fields.DateTime,
    scraper.END_DATE: fields.DateTime,
    scraper.SIZE: fields.Integer
})

all_fields = api.model('AllInsert', {
    scraper.POSTAL_CODE: fields.Integer,
    scraper.MAX_PRICE: fields.Integer,
    scraper.START_DATE: fields.DateTime,
    scraper.END_DATE: fields.DateTime,
    scraper.SIZE: fields.Integer
})

generic_event_fields = api.model('GetEvents', {
    scraper.POSTAL_CODE: fields.Integer,
    scraper.MAX_PRICE: fields.Integer,
    scraper.START_DATE: fields.DateTime,
    scraper.END_DATE: fields.DateTime,
    scraper.SIZE: fields.Integer
})


@api.route(f'{TM_GET_EVENTS}')
class TMGetEvents(Resource):
    """
    Making an API call to Ticketmaster and returning the list of events
    matching the user-provided filters
    """
    @api.expect(tm_event_fields)
    def post(self):
        '''
        Calls Ticketmaster's API and return a list of events as POST request
        '''
        postal_code = request.json[scraper.POSTAL_CODE]
        max_price = request.json[scraper.MAX_PRICE]
        start_date = request.json[scraper.START_DATE]
        end_date = request.json[scraper.END_DATE]
        size = request.json[scraper.SIZE]
        events = scraper.ticketmasterGetEvents(postal_code,
                                               max_price,
                                               start_date,
                                               end_date,
                                               size)
        return {EVENTS: events}


@api.route(f'{SG_GET_EVENTS}')
class SGGetEvents(Resource):
    """
    Making an API call to SeatGeek and returning the list of events
    matching the user-provided filters
    """
    @api.expect(sg_event_fields)
    def post(self):
        '''
        Calls SeatGeeks's API and return a list of events as POST request
        '''
        postal_code = request.json[scraper.POSTAL_CODE]
        max_price = request.json[scraper.MAX_PRICE]
        # TODO: have a function that process the datetime-local input from the
        # HTML form and converts timezones to UTC
        start_date = request.json[scraper.START_DATE]
        end_date = request.json[scraper.END_DATE]
        size = request.json[scraper.SIZE]
        events = scraper.seatgeekGetEvents(postal_code, max_price,
                                           start_date, end_date, size)
        return {EVENTS: events}


@api.route(f'{GET_EVENTS}')
class GetEvents(Resource):
    """
    Making API calls to Ticketmaster and Seatgeek and return a list of events
    matching the user-provided filters
    """
    @api.expect(generic_event_fields)
    def post(self):
        postal_code = request.json[scraper.POSTAL_CODE]
        max_price = request.json[scraper.MAX_PRICE]
        start_date = request.json[scraper.START_DATE]
        end_date = request.json[scraper.END_DATE]
        size = request.json[scraper.SIZE]
        events = scraper.getEvents(postal_code,
                                   max_price,
                                   start_date,
                                   end_date,
                                   size)
        return {EVENTS: events}


@api.route(f'{MG_INSERT_DOCUMENT}/<size>/<postalCode>')
class MGInsertDocument(Resource):
    """
    Test to make sure the MongoDB's Atlas Data
    API POST requests can add data
    """
    def post(self, size, postalCode):
        """
        Calls MongoDB's API and inserts a doc, returns inserted ID
        """
        doc = {"size": size, "postalCode": postalCode}
        document = db.POST("insertOne", doc)
        return document


@api.route(f'{MG_GET_DOCUMENT}/<size>/<postalCode>')
class MGGetDocument(Resource):
    """
    Test to make sure the MongoDB's Atlas Data
    API POST request can find data
    """
    def post(self, size, postalCode):
        """
        Calls MongoDB's API and returns attributes of a doc
        """
        doc = {"size": size, "postalCode": postalCode}
        document = db.POST("findOne", doc)
        return document


@api.route(f'{MG_DELETE_DOCUMENT}/<size>/<postalCode>')
class MGDeleteDocument(Resource):
    """
    Test to make sure the MongoDB's Atlas Data
    API POST request can find data
    """
    def post(self, size, postalCode):
        """
        Calls MongoDB's API and deletes a doc, returning # of items deleted
        """
        doc = {"size": size, "postalCode": postalCode}
        document = db.POST("deleteOne", doc)
        return document


@api.route(f'{MG_GET_MANY}/<size>/<postalCode>')
class MGGetMany(Resource):
    """
    Test to make sure the MongoDB's Atlas Data
    API POST request can find data
    """
    def post(self, size, postalCode):
        """
        Calls MongoDB's API and returns list of documents
        """
        doc = {"size": size, "postalCode": postalCode}
        documents = db.POST("find", doc)
        return documents


@api.route(f'{ALL_INSERT}')
class AllInsert(Resource):
    """
    Test insertion of parsed events from Ticketmaster and Seatgeek
    into MongoDB collection
    """
    @api.expect(all_fields)
    def post(self):
        """
        Calls Ticketmaster, SeatGeek, and MongoAPI to get events and then
        insert them, returns inserted IDs for both
        """
        postal_code = request.json[scraper.POSTAL_CODE]
        max_price = request.json[scraper.MAX_PRICE]
        start_date = request.json[scraper.START_DATE]
        end_date = request.json[scraper.END_DATE]
        size = request.json[scraper.SIZE]
        tm_events = scraper.ticketmasterGetEvents(postal_code,
                                                  max_price,
                                                  start_date,
                                                  end_date,
                                                  size)
        sg_events = scraper.seatgeekGetEvents(postal_code, max_price,
                                              start_date, end_date, size)
        tm_response = db.POST("insertMany", tm_events)
        sg_response = db.POST("insertMany", sg_events)
        return {TM: tm_response, SG: sg_response}


@api.route(f'{ALL_CLEAR}')
class AllClear(Resource):
    """
    Clears the entire MongoDB Event collection
    """
    def post(self):
        """
        Calls MongoDB's API and returns number of deleted documents
        """
        document = db.POST("deleteMany", {})
        return document


@api.route(f'{GET_AND_CONVERT}/<size>')
class GetAndConvert(Resource):
    """
    MongoDB data API returning list of dicts and converting them
    to Event objects
    """
    def post(self, size):
        documents = db.POST("find", {"size": size})
        events = db.convertToEvent(documents[DOCUMENTS])
        return {EVENTS: events}
