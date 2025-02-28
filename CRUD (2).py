#!/usr/bin/env python
# coding: utf-8

from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib.parse

class AnimalShelter(object):

    # Property variables
    records_updated = 0  # Keep a record of the records updated in an operation; CYA
    records_matched = 0  # Keep a record of the records matched in an operation; CYA
    records_deleted = 0  # Keep a record of the records deleted in an operation; CYA

    # Constructor to initialize the MongoDB
    # To do: this should be a singleton
    def __init__(self, _password, _username='aacuser'):

        # URI must be percent escaped as per pymongo documentation
        userName = urllib.parse.quote_plus('aacuser')
        password = urllib.parse.quote_plus('Password')

        self.client = MongoClient('mongodb://%s:%s@nv-desktop-services.apporto.com:30264/?authSource=AAC' % (userName, password))
        self.dataBase = self.client['AAC']

    # Method to create a record
    # Input data formatted as per the Pymongo API
    # Example: ({"name": "Rex", 'age_upon_outcome': '2 months'})
    def createRecord(self, data):
        if data:
            _insertValid = self.dataBase.animals.insert_one(data)
            # Check the status of the inserted value 
            return True if _insertValid.acknowledged else False
        else:
            raise Exception("No document to save. Data is empty.")

    # Todo: implement the R (Read)
    # Get documents by the GUID
    # This is more for a test but could be used after the createRecord
    # Since the document returned by insert_one contains the newly created _id
    def getRecordId(self, postId):
        _data = self.dataBase.animals.find_one({'_id': ObjectId(postId)})
        return _data

    # Get records with criteria
    # All records are returned if criteria is None
    # Default is None
    # Example: ({"name": "Rex", 'age_upon_outcome': '2 months'})
    # Do not return the _id
    def getRecordCriteria(self, criteria=None):
        if criteria:
            _data = self.dataBase.animals.find(criteria, {'_id': 0})
        else:
            _data = self.dataBase.animals.find({}, {'_id': 0})
        return _data

    # Update a record
    def updateRecord(self, query, newValue):
        if not query:
            raise Exception("No search criteria is present.")
        elif not newValue:
            raise Exception("No update value is present.")
        else:
            _updateValid = self.dataBase.animals.update_many(query, {"$set": newValue})
            self.records_updated = _updateValid.modified_count
            self.records_matched = _updateValid.matched_count
            return True if _updateValid.modified_count > 0 else False

    # Delete a record
    def deleteRecord(self, query):
        if not query:
            raise Exception("No search criteria is present.")
        else:
            _deleteValid = self.dataBase.animals.delete_many(query)
            self.records_deleted = _deleteValid.deleted_count
            return True if _deleteValid.deleted_count > 0 else False

