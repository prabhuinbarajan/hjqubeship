#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['HJQUBESHIP_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['HJQUBESHIP_MONGOALCHEMY_SERVER'] = ''
    os.environ['HJQUBESHIP_MONGOALCHEMY_PORT'] = ''
    os.environ['HJQUBESHIP_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.hjqubeship import hjqubeship
    from qube.src.services.hjqubeshipservice import hjqubeshipService
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, hjqubeshipServiceError


class TesthjqubeshipService(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.hjqubeshipService = hjqubeshipService(context)
        self.hjqubeship_api_model = self.createTestModelData()
        self.hjqubeship_data = \
            self.setupDatabaseRecords(self.hjqubeship_api_model)
        self.hjqubeship_someoneelses = \
            self.setupDatabaseRecords(self.hjqubeship_api_model)
        self.hjqubeship_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.hjqubeship_someoneelses.save()
        self.hjqubeship_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.hjqubeship_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.hjqubeship_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, hjqubeship_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            hjqubeship_data = hjqubeship(name='test_record')
            for key in hjqubeship_api_model:
                hjqubeship_data.__setattr__(key, hjqubeship_api_model[key])

            hjqubeship_data.description = 'my short description'
            hjqubeship_data.tenantId = "23432523452345"
            hjqubeship_data.orgId = "987656789765670"
            hjqubeship_data.createdBy = "1009009009988"
            hjqubeship_data.modifiedBy = "1009009009988"
            hjqubeship_data.createDate = str(int(time.time()))
            hjqubeship_data.modifiedDate = str(int(time.time()))
            hjqubeship_data.save()
            return hjqubeship_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_hjqubeship(self, *args, **kwargs):
        result = self.hjqubeshipService.save(self.hjqubeship_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.hjqubeship_api_model['name'])
        hjqubeship.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_hjqubeship(self, *args, **kwargs):
        self.hjqubeship_api_model['name'] = 'modified for put'
        id_to_find = str(self.hjqubeship_data.mongo_id)
        result = self.hjqubeshipService.update(
            self.hjqubeship_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.hjqubeship_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_hjqubeship_description(self, *args, **kwargs):
        self.hjqubeship_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.hjqubeship_data.mongo_id)
        result = self.hjqubeshipService.update(
            self.hjqubeship_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_hjqubeship_item(self, *args, **kwargs):
        id_to_find = str(self.hjqubeship_data.mongo_id)
        result = self.hjqubeshipService.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_hjqubeship_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(hjqubeshipServiceError):
            self.hjqubeshipService.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_hjqubeship_list(self, *args, **kwargs):
        result_collection = self.hjqubeshipService.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.hjqubeship_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.hjqubeship_data.mongo_id)
        with self.assertRaises(hjqubeshipServiceError) as ex:
            self.hjqubeshipService.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.hjqubeship_data.mongo_id)
        self.hjqubeshipService.auth_context.is_system_user = True
        self.hjqubeshipService.delete(id_to_delete)
        with self.assertRaises(hjqubeshipServiceError) as ex:
            self.hjqubeshipService.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.hjqubeshipService.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.hjqubeship_someoneelses.mongo_id)
        with self.assertRaises(hjqubeshipServiceError):
            self.hjqubeshipService.delete(id_to_delete)
