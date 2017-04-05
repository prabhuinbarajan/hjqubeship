#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class TesthjqubeshipModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_hjqubeship_model(self):
        from qube.src.models.hjqubeship import hjqubeship
        hjqubeship_data = hjqubeship(name='testname')
        hjqubeship_data.tenantId = "23432523452345"
        hjqubeship_data.orgId = "987656789765670"
        hjqubeship_data.createdBy = "1009009009988"
        hjqubeship_data.modifiedBy = "1009009009988"
        hjqubeship_data.createDate = str(int(time.time()))
        hjqubeship_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            hjqubeship_data.save()
            self.assertIsNotNone(hjqubeship_data.mongo_id)
            hjqubeship_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
