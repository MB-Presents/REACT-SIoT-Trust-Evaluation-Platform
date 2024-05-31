import os
import random
import sys
from typing import List




project_root = os.getenv("RESEARCH_PROJECT_ROOT", default="/app")
sys.path.insert(0, project_root)

import unittest
from unittest.mock import MagicMock
from uuid import UUID

from trust_management.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust_management.data_models.transaction.data_models.direct_recommendation import DirectRecommendation
from trust_management.data_models.transaction.status import TransactionStatus
from trust_management.data_models.transaction.transaction_manager import TransactionManager
from data_models.iot_devices.common import DeviceType

from data_models.iot_devices.genric_iot_device import GenericDevice
from data_models.report_management.report.report import SendingPacket
from data_models.report_management.report.report_models import ReportType, Situation
from trust_management.data_models.TrustVerifierRoles import TrustVerfierRoles
from trust_management.data_models.transaction.data_models.trust_transaction import Transaction

from trust_management.data_models.transaction.type import TransactionType

class TestTransactionManager(unittest.TestCase):

    def setUp(self):
        self.transaction_manager = TransactionManager()
        
        self.devices = self.get_devices()
        self.requests = self.get_requests(self.devices)
        self.transactions : List[Transaction] = self.get_transactions()
        self.recommendations : List[DirectRecommendation] = self.get_recommendations()
        
        
    def get_devices(self): 
        vehicle_1 = GenericDevice(device_id="veh_1", device_type=DeviceType.VEHICLE, position=[0,0])
        vehicle_2 = GenericDevice(device_id="veh_2", device_type=DeviceType.VEHICLE, position=[0,0])
        vehicle_3 = GenericDevice(device_id="veh_3", device_type=DeviceType.VEHICLE, position=[0,0])
        
        smartphone_1 = GenericDevice(device_id="ped_1", device_type=DeviceType.VEHICLE, position=[0,0])
        smartphone_2 = GenericDevice(device_id="ped_2", device_type=DeviceType.VEHICLE, position=[0,0])
        smartphone_3 = GenericDevice(device_id="ped_3", device_type=DeviceType.VEHICLE, position=[0,0])       

        devices = [vehicle_1, vehicle_2, vehicle_3, smartphone_1, smartphone_2, smartphone_3]

        return devices
    
    
    def get_requests(self,devices):
        
        
        accident_request_1 = SendingPacket(time = "100", receiver=devices[0], sending_entities=None, situation=Situation.EMERGENCY_REPORT, object_of_interest=None, type=ReportType.EmergencyReport)
        # accident_request_2 = SendingPacket(time = "100", receiver=devices[0], sending_entities=None, situation=Situation.EMERGENCY_REPORT, object_of_interest=None, type=ReportType.EmergencyReport)
        
        # traffic_light_request_1 = SendingPacket(time = "100", receiver=devices[0], sending_entities=None, situation=Situation.TRAFFIC_PRIORITY_REQUEST, object_of_interest=None, type=ReportType.TraffiCPriorityRequest)
        traffic_light_request_2 = SendingPacket(time = "100", receiver=devices[0], sending_entities=None, situation=Situation.TRAFFIC_PRIORITY_REQUEST, object_of_interest=None, type=ReportType.TraffiCPriorityRequest)
        
        requests = [accident_request_1,  traffic_light_request_2]
        
        return requests
        
            
    def get_three_different_trustees_transactions(self):


        transaction_1 = Transaction(trustor=self.devices[0], trustee=self.devices[1], task_context=self.requests[0], trust_value=0.5, role=TrustVerfierRoles.REPORTER)
        transaction_2 = Transaction(trustor=self.devices[0], trustee=self.devices[2], task_context=self.requests[0], trust_value=0.5, role=TrustVerfierRoles.SERVICE_PROVIDER)
        transaction_3 = Transaction(trustor=self.devices[0], trustee=self.devices[3], task_context=self.requests[0], trust_value=0.5, role=TrustVerfierRoles.REPORTER)

        return transaction_1, transaction_2, transaction_3


    def get_two_different_transaction_contexts(self):
        vehicle_1, vehicle_2, _, _, _, _ = self.devices

        transaction_4 = Transaction(trustor=vehicle_1, trustee=self.devices[1], task_context=self.requests[0], trust_value=0.5, role=TrustVerfierRoles.SERVICE_PROVIDER)
        transaction_5 = Transaction(trustor=vehicle_1, trustee=self.devices[1], task_context=self.requests[1], trust_value=0.5, role=TrustVerfierRoles.REPORTER)

        return transaction_4, transaction_5


    def get_two_different_contexts_with_different_trustees(self):
        
        transaction_6 = Transaction(trustor=self.devices[0], trustee=self.devices[3], task_context=self.requests[0], trust_value=0.5, role=TrustVerfierRoles.SERVICE_PROVIDER)
        transaction_7 = Transaction(trustor=self.devices[0], trustee=self.devices[4], task_context=self.requests[1], trust_value=0.5, role=TrustVerfierRoles.REPORTER)

        return transaction_6, transaction_7


    def get_three_different_trustees_same_context(self):
        
        transaction_8 = Transaction(trustor=self.devices[0], trustee=self.devices[2], task_context=self.requests[0], trust_value=0.5, role=TrustVerfierRoles.REPORTER)
        transaction_9 = Transaction(trustor=self.devices[0], trustee=self.devices[3], task_context=self.requests[0], trust_value=0.5, role=TrustVerfierRoles.SERVICE_PROVIDER)
        transaction_10 = Transaction(trustor=self.devices[0], trustee=self.devices[4], task_context=self.requests[0], trust_value=0.5, role=TrustVerfierRoles.REPORTER)

        return transaction_8, transaction_9, transaction_10


    def get_transactions(self):

        selected_device_list = [self.devices[1], self.devices[2], self.devices[3], self.devices[4], self.devices[5]]

        transactions = []
        for transaction in range(1,20):
            
            trustee = random.choice(selected_device_list)
            task_context = random.choice(self.requests)
            trust_verifier_role = random.choice([TrustVerfierRoles.REPORTER, TrustVerfierRoles.SERVICE_PROVIDER])
            transaction = Transaction(trustor=self.devices[0], trustee=trustee, task_context=task_context, trust_value=0.5,role=trust_verifier_role)
            
            transactions.append(transaction)

        return transactions
    




        
    def test_add_transaction(self):
        
        # Arrange
        num_transactions = 1
        transactions = random.sample(self.transactions, num_transactions)
        
        num_trust_transactions = len(transactions) 
        num_trust_transactions_pairs = self.get_num_trust_transaction_pairs(transactions)
        num_transactions_by_report_id = self.get_num_report_ids(transactions)
        num_transactions_by_trustee_id = self.get_number_of_trustees(transactions)
        num_transactions_by_transaction_context = self.get_num_task_contextx(transactions)
        num_transactions_by_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(transactions)
        
        num_unverified_trust_transactions = len(transactions)
        num_unverified_trust_transactions_pairs = self.get_num_trust_transaction_pairs(transactions)
        num_unverified_trust_transactions_by_trustee = self.get_number_of_trustees(transactions)
        num_unverified_trust_transactions_by_report_id = self.get_num_report_ids(transactions)
        num_unverified_trust_transactions_by_transaction_context = self.get_num_task_contextx(transactions)
        num_unverified_trust_transactions_by_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(transactions)
                

        # Action        
        for transaction in transactions:
            self.transaction_manager.add_transaction(transaction)

        # Assertion
        self.assertEqual(len(self.transaction_manager.trust_transactions), num_trust_transactions)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), num_trust_transactions_pairs)  
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), num_transactions_by_report_id)  
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), num_transactions_by_trustee_id)  
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), num_transactions_by_transaction_context)  
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), num_transactions_by_trustee_and_transaction_context)

        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), num_unverified_trust_transactions)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), num_unverified_trust_transactions_pairs)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), num_unverified_trust_transactions_by_trustee)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), num_unverified_trust_transactions_by_report_id)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), num_unverified_trust_transactions_by_transaction_context)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), num_unverified_trust_transactions_by_trustee_and_transaction_context) 

    def test_add_transaction_1_2(self):
        
        # Arrange
        num_transactions = 2
        transactions = random.sample(self.transactions, num_transactions)
        
        num_trust_transactions = len(transactions) 
        num_trust_transactions_pairs = self.get_num_trust_transaction_pairs(transactions)
        num_transactions_by_report_id = self.get_num_report_ids(transactions)
        num_transactions_by_trustee_id = self.get_number_of_trustees(transactions)
        num_transactions_by_transaction_context = self.get_num_task_contextx(transactions)
        num_transactions_by_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(transactions)
        
        num_unverified_trust_transactions = len(transactions)
        num_unverified_trust_transactions_pairs = self.get_num_trust_transaction_pairs(transactions)
        num_unverified_trust_transactions_by_trustee = self.get_number_of_trustees(transactions)
        num_unverified_trust_transactions_by_report_id = self.get_num_report_ids(transactions)
        num_unverified_trust_transactions_by_transaction_context = self.get_num_task_contextx(transactions)
        num_unverified_trust_transactions_by_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(transactions)
                

        # Action        
        for transaction in transactions:
            self.transaction_manager.add_transaction(transaction)

        # Assertion
        self.assertEqual(len(self.transaction_manager.trust_transactions), num_trust_transactions)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), num_trust_transactions_pairs)  
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), num_transactions_by_report_id)  
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), num_transactions_by_trustee_id)  
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), num_transactions_by_transaction_context)  
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), num_transactions_by_trustee_and_transaction_context)

        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), num_unverified_trust_transactions)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), num_unverified_trust_transactions_pairs)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), num_unverified_trust_transactions_by_trustee)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), num_unverified_trust_transactions_by_report_id)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), num_unverified_trust_transactions_by_transaction_context)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), num_unverified_trust_transactions_by_trustee_and_transaction_context) 
        
    def test_add_transaction_1_2_3_4(self):


        # Arrange
        num_transactions = 4
        transactions = random.sample(self.transactions, num_transactions)
        
        num_trust_transactions = len(transactions) 
        num_trust_transactions_pairs = self.get_num_trust_transaction_pairs(transactions)
        num_transactions_by_report_id = self.get_num_report_ids(transactions)
        num_transactions_by_trustee_id = self.get_number_of_trustees(transactions)
        num_transactions_by_transaction_context = self.get_num_task_contextx(transactions)
        num_transactions_by_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(transactions)
        
        num_unverified_trust_transactions = len(transactions)
        num_unverified_trust_transactions_pairs = self.get_num_trust_transaction_pairs(transactions)
        num_unverified_trust_transactions_by_trustee = self.get_number_of_trustees(transactions)
        num_unverified_trust_transactions_by_report_id = self.get_num_report_ids(transactions)
        num_unverified_trust_transactions_by_transaction_context = self.get_num_task_contextx(transactions)
        num_unverified_trust_transactions_by_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(transactions)
                

        # Action        
        for transaction in transactions:
            self.transaction_manager.add_transaction(transaction)
        
        # Assertion
        self.assertEqual(len(self.transaction_manager.trust_transactions), num_trust_transactions)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), num_trust_transactions_pairs)  
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), num_transactions_by_report_id)  
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), num_transactions_by_trustee_id)  
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), num_transactions_by_transaction_context)  
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), num_transactions_by_trustee_and_transaction_context)

        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), num_unverified_trust_transactions)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), num_unverified_trust_transactions_pairs)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), num_unverified_trust_transactions_by_trustee)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), num_unverified_trust_transactions_by_report_id)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), num_unverified_trust_transactions_by_transaction_context)  
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), num_unverified_trust_transactions_by_trustee_and_transaction_context) 

    def get_num_trust_transaction_pairs(self, transactions):
        num_trust_transactions_pairs = len(set((transaction.trustor._id, transaction.trustee._id) for transaction in transactions))
        return num_trust_transactions_pairs # Based on unique trustee-transaction_context pairs
                
    def test_three_different_trustees_transactions(self):
        
        # Arrange
        transaction_1, transaction_2, transaction_3 = self.get_three_different_trustees_transactions()
        
        # Action
        self.transaction_manager.add_transaction(transaction_1)
        self.transaction_manager.add_transaction(transaction_2)
        self.transaction_manager.add_transaction(transaction_3)
        
        # Assertion
        self.assertEqual(len(self.transaction_manager.trust_transactions), 3)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), 3)
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), 1)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), 3)
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), 1)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), 3)

        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), 3)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), 3)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), 3)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), 1)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), 1)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), 3)

    def test_two_different_transaction_contexts(self):
        # Arrange
        transaction_4, transaction_5 = self.get_two_different_transaction_contexts()

        # Action
        self.transaction_manager.add_transaction(transaction_4)
        self.transaction_manager.add_transaction(transaction_5)

        # Assertion
        self.assertEqual(len(self.transaction_manager.trust_transactions), 2)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), 1)
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), 2)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), 1)
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), 2)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), 2)

        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), 2)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), 1)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), 2)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), 1)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), 2)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), 2)     

    def test_two_different_contexts_with_different_trustees(self):
        # Arrange
        transaction_6, transaction_7 = self.get_two_different_contexts_with_different_trustees()

        # Action
        self.transaction_manager.add_transaction(transaction_6)
        self.transaction_manager.add_transaction(transaction_7)

        # Assertion
        self.assertEqual(len(self.transaction_manager.trust_transactions), 2)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), 2)
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), 2)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), 2)
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), 2)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), 2)

        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), 2)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), 2)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), 2)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), 2)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), 2)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), 2)

    def test_three_different_trustees_same_context(self):
        # Arrange
        transaction_8, transaction_9, transaction_10 = self.get_three_different_trustees_same_context()

        # Action
        self.transaction_manager.add_transaction(transaction_8)
        self.transaction_manager.add_transaction(transaction_9)
        self.transaction_manager.add_transaction(transaction_10)

        # Assertion
        self.assertEqual(len(self.transaction_manager.trust_transactions), 3)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), 3)
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), 1)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), 3)
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), 1)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), 3)

        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), 3)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), 3)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), 1)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), 3)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), 1)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), 3)

    def test_update_transaction(self):
        
        # Arrange
        num_selected_transactions = 1
        num_updated_transactions = 1
        
        selected_transactions : List[Transaction] = random.sample(self.transactions, num_selected_transactions)
        selected_updated_transaction : List[Transaction] = random.sample(selected_transactions, num_updated_transactions)
        
        # Selected Transactions
        num_transactions = len(selected_transactions)
        num_trustees = self.get_number_of_trustees(selected_transactions)
        num_task_contexts = self.get_num_task_contextx(selected_transactions)
        num_report_ids = self.get_num_report_ids(selected_transactions)
        num_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(selected_transactions)
        
        
        # Selected unverified transactions
        unverified_transaction_list = set(selected_transactions).difference(set(selected_updated_transaction))
        # unverified_transaction_list = [transaction for transaction in selected_transactions if transaction._id != selected_updated_transaction._id]
        
        num_unverified_transactions = len(unverified_transaction_list)
        num_unverified_trustees = self.get_number_of_trustees(unverified_transaction_list)
        num_unverified_task_contexts = self.get_num_task_contextx(unverified_transaction_list)
        num_unverified_report_ids = self.get_num_report_ids(unverified_transaction_list)
        num_unverified_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(unverified_transaction_list)
        
        # Selected verified transactions
        verified_transactions = selected_updated_transaction
        
        num_verified_transactions = len(verified_transactions)
        num_verified_trustees = self.get_number_of_trustees(verified_transactions)
        num_verified_task_contexts = self.get_num_task_contextx(verified_transactions)
        num_verified_report_ids = self.get_num_report_ids(verified_transactions)
        num_verified_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(verified_transactions)
        
        # Action
        for transaction in selected_transactions:
            self.transaction_manager.add_transaction(transaction)
    
        # Update Transacitons
        for transaction in selected_updated_transaction:
            self.transaction_manager.update_transaction(transaction, TransactionStatus.VERIFIED)
        
        # Assertion
        self.assertEqual(len(self.transaction_manager.trust_transactions), num_transactions)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), num_trustees)
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), num_report_ids)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), num_trustees)
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), num_task_contexts)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), num_trustee_and_transaction_context)
        
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), num_unverified_transactions)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), num_unverified_trustees)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), num_unverified_trustees)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), num_unverified_report_ids)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), num_unverified_task_contexts)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), num_unverified_trustee_and_transaction_context)
        
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions), num_verified_transactions)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_pairs), num_verified_transactions)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_trustee), num_verified_trustees)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_report_id), num_verified_report_ids)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_transaction_context), num_verified_task_contexts)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_trustee_and_transaction_context), num_verified_trustee_and_transaction_context)
            
    def get_number_of_trustees(self,transactions : List[Transaction]):
        
        unique_trustees = set(transaction.trustee._id for transaction in transactions)
        num_trustees = len(unique_trustees)
        return num_trustees
    
    def get_num_task_contextx(self, transactions : List[Transaction]):
            
        unique_task_contexts = set(transaction.task_context.request_type for transaction in transactions)
        num_task_contexts = len(unique_task_contexts)
        return num_task_contexts
    
    def get_num_trustee_and_transaction_context(self, transactions : List[Transaction]):
            
        unique_trustee_and_transaction_context = set((transaction.trustee._id, transaction.task_context.request_type) for transaction in transactions)
        num_trustee_and_transaction_context = len(unique_trustee_and_transaction_context)
        return num_trustee_and_transaction_context
        
    def get_num_report_ids(self, transactions : List[Transaction]):
            
        unique_report_ids = set(transaction.task_context.report_id for transaction in transactions)
        num_report_ids = len(unique_report_ids)
        return num_report_ids
                
    def test_update_transaction_tc_2(self):
        
        # Arrange
        selected_transactions = random.sample(self.transactions, 10)
        
        selected_updated_transaction : Transaction = random.choices(selected_transactions)[0]
        
        # Selected Transactions
        num_transactions = len(selected_transactions)
        num_trustees = self.get_number_of_trustees(selected_transactions)
        num_task_contexts = self.get_num_task_contextx(selected_transactions)
        num_report_ids = self.get_num_report_ids(selected_transactions)
        num_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(selected_transactions)
        
        
        # Selected updated transactions
        unverified_transaction_list = [transaction for transaction in selected_transactions if transaction._id != selected_updated_transaction._id]
        
        num_unverified_transactions = len(unverified_transaction_list)
        num_unverified_trustees = self.get_number_of_trustees(unverified_transaction_list)
        num_unverified_task_contexts = self.get_num_task_contextx(unverified_transaction_list)
        num_unverified_report_ids = self.get_num_report_ids(unverified_transaction_list)
        num_unverified_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(unverified_transaction_list)
        
        # Selected verified transactions
        verified_transactions = [selected_updated_transaction]
        
        num_verified_transactions = len(verified_transactions)
        num_verified_trustees = self.get_number_of_trustees(verified_transactions)
        num_verified_task_contexts = self.get_num_task_contextx(verified_transactions)
        num_verified_report_ids = self.get_num_report_ids(verified_transactions)
        num_verified_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(verified_transactions)
        

        # Action
        for transaction in selected_transactions:
            self.transaction_manager.add_transaction(transaction)
        
        # Update 
        self.transaction_manager.update_transaction(selected_updated_transaction, TransactionStatus.VERIFIED)
        
        
        # Assetion
        
        self.assertEqual(len(self.transaction_manager.trust_transactions), num_transactions)
        self.assertEqual(len(self.transaction_manager.trust_transactions_pairs), num_trustees)
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), num_report_ids)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_id), num_trustees)
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), num_task_contexts)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), num_trustee_and_transaction_context)
        
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions), num_unverified_transactions)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_pairs), num_unverified_trustees)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee), num_unverified_trustees)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_report_id), num_unverified_report_ids)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), num_unverified_task_contexts)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), num_unverified_trustee_and_transaction_context)
        
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions), num_verified_transactions)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_pairs), num_verified_transactions)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_trustee), num_verified_trustees)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_report_id), num_verified_report_ids)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_transaction_context), num_verified_task_contexts)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_trustee_and_transaction_context), num_verified_trustee_and_transaction_context)
        
    
    def get_recommendations(self):
        
        
        selected_device_list = [self.devices[0], self.devices[2], self.devices[3], self.devices[4], self.devices[5]]

        recommendations = []
        
        for recommendation in range(1,20): 
            

            trustee = random.choice(selected_device_list)
            task_context = random.choice(self.requests)
            trust_verifier_role = random.choice([TrustVerfierRoles.REPORTER, TrustVerfierRoles.SERVICE_PROVIDER])
            transaction = random.choice(self.transactions)
            transaction = DirectRecommendation(recommender=self.devices[1], recommendee=trustee, task_context=task_context, recommended_trust_value=transaction.trust_value, original_transaction_id=transaction._id, transaction_type=TransactionType.DIRECT_RECOMMENDATION, transaction_status=transaction.status,parent_transaction=transaction)
            
            
            recommendations.append(transaction)

        return recommendations
     
    def get_num_recommendation_transactions(self, transactions : List[DirectRecommendation]):
            
        recommendation_transactions = set(transaction for transaction in transactions if transaction.type == TransactionType.DIRECT_RECOMMENDATION or transaction.type == TransactionType.INDIRECT_RECOMMENDATION)
        num_trustees = len(recommendation_transactions)
        return num_trustees
    
    def get_recommender_id(self, transactions : List[DirectRecommendation]):
                
        unique_recommenders = set(transaction.trustor._id for transaction in transactions)
        num_recommenders = len(unique_recommenders)
        return num_recommenders
    
    def get_num_of_trust_subject(self, transactions : List[DirectRecommendation]):
                    
        unique_trustees = set(transaction.trustee._id for transaction in transactions)
        num_trustees = len(unique_trustees)
        return num_trustees
    
    def get_num_of_trust_subject_transaction_context(self, transactions : List[DirectRecommendation]):
                            
        unique_trustees = set((transaction.trustee._id, transaction.task_context.request_type) for transaction in transactions)
        num_trustees = len(unique_trustees)
        return num_trustees 
    
    def get_num_transaction_per_recommender(self, transactions : List[DirectRecommendation]):
                                
        unique_trustees = set((transaction.trustor._id, transaction.task_context.request_type) for transaction in transactions)
        num_trustees = len(unique_trustees)
        return num_trustees 
    
    
    
    
    
    def test_add_recommendations(self):
        
        
        num_selected_recommendations = 10
        num_updated_recommendations = 0
        
        selected_recommendations : List[Transaction] = random.sample(self.recommendations, num_selected_recommendations)
        selected_updated_recommendations : List[Transaction] = random.sample(selected_recommendations, num_updated_recommendations)
        
        # Selected Transactions
        self.transaction_manager.trust_transactions
        self.transaction_manager.trust_transactions_pairs
        
        num_transactions = len(selected_recommendations)
        num_task_contexts = self.get_num_task_contextx(selected_recommendations)
        
        
        num_report_ids = self.get_num_report_ids(selected_recommendations)
        num_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(selected_recommendations)
        num_recommendation_transactions = self.get_num_recommendation_transactions(selected_recommendations)
        num_transactions_by_recommender_id = self.get_recommender_id(selected_recommendations)
        num_recommendations_of_trust_subject = self.get_num_of_trust_subject(selected_recommendations)
        num_recommendations_of_trust_subject_transaction_context = self.get_num_of_trust_subject_transaction_context(selected_recommendations)
        num_transactions_by_recommender_transaction_context = self.get_num_transaction_per_recommender(selected_recommendations)
        num_transactions_by_transaction_context = self.get_num_task_contextx(selected_recommendations)

        
        
        # Selected unverified transactions
        unverified_transactions = set(selected_recommendations).difference(set(selected_updated_recommendations))
        
        
        num_unverified_recommendation_transactions = self.get_num_recommendation_transactions(unverified_transactions)
        num_unverified_recommendations_of_trust_subject = self.get_num_of_trust_subject(unverified_transactions)
        num_unverified_recommendations_of_trust_subject_transaction_context = self.get_num_of_trust_subject_transaction_context(unverified_transactions)
        num_unverified_trust_transactions_by_recommender_id = self.get_recommender_id(unverified_transactions)
        num_unverified_trust_transactions_by_recommender_transaction_context = self.get_num_transaction_per_recommender(unverified_transactions)
        num_unverified_trust_transactions_by_transaction_context = self.get_num_task_contextx(unverified_transactions)
        num_unverified_trust_transactions_by_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(unverified_transactions)
        
                
        # Selected verified transactions
        
        verified_transactions = selected_updated_recommendations
        
        num_verified_transactions = len(verified_transactions)
        num_verified_recommendation_transactions = len(verified_transactions)
        
        num_verified_recommendations_of_trust_subject = self.get_num_of_trust_subject(verified_transactions)
        num_verified_recommendations_of_trust_subject_transaction_context = self.get_num_of_trust_subject_transaction_context(verified_transactions)
        num_verified_trust_transactions_by_recommender_id = self.get_recommender_id(verified_transactions)
        num_verified_trust_transactions_by_recommender_transaction_context = self.get_num_transaction_per_recommender(verified_transactions)
        num_verified_trust_transactions_by_transaction_context = self.get_num_task_contextx(verified_transactions)
        num_verified_trust_transactions_by_trustee_and_transaction_context = self.get_num_trustee_and_transaction_context(verified_transactions)
        
        
        
        # Action
        for transaction in selected_recommendations:
            self.transaction_manager.add_direct_recommendation(transaction)
    
        # Update Transacitons
        # for transaction in selected_updated_recommendations:
        #     self.transaction_manager.update_transaction(transaction, TransactionStatus.VERIFIED)
        

        # Assertion
        
        self.assertEqual(len(self.transaction_manager.trust_transactions), num_transactions)
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), num_task_contexts)
        self.assertEqual(len(self.transaction_manager.transactions_by_report_id), num_report_ids)
        self.assertEqual(len(self.transaction_manager.transactions_by_trustee_and_transaction_context), num_trustee_and_transaction_context)
        self.assertEqual(len(self.transaction_manager.transactions_by_recommender_id), num_transactions_by_recommender_id)
        self.assertEqual(len(self.transaction_manager.transactions_by_recommender_transaction_context), num_transactions_by_recommender_transaction_context)
        self.assertEqual(len(self.transaction_manager.recommendations_of_trust_subject), num_recommendations_of_trust_subject)
        self.assertEqual(len(self.transaction_manager.recommendations_of_trust_subject_transaction_context), num_recommendations_of_trust_subject_transaction_context)
        self.assertEqual(len(self.transaction_manager.transactions_by_transaction_context), num_transactions_by_transaction_context)
        self.assertEqual(len(self.transaction_manager.recommendation_transactions), num_recommendation_transactions)
        
        
        self.assertEqual(len(self.transaction_manager.unverified_recommendation_transactions), num_unverified_recommendation_transactions)
        self.assertEqual(len(self.transaction_manager.unverified_recommendations_of_trust_subject), num_unverified_recommendations_of_trust_subject)
        self.assertEqual(len(self.transaction_manager.unverified_recommendations_of_trust_subject_transaction_context), num_unverified_recommendations_of_trust_subject_transaction_context)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_recommender_id), num_unverified_trust_transactions_by_recommender_id)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_recommender_transaction_context), num_unverified_trust_transactions_by_recommender_transaction_context)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_transaction_context), num_unverified_trust_transactions_by_transaction_context)
        self.assertEqual(len(self.transaction_manager.unverified_trust_transactions_by_trustee_and_transaction_context), num_unverified_trust_transactions_by_trustee_and_transaction_context)
        
        self.assertEqual(len(self.transaction_manager.verified_recommendation_transactions), num_verified_recommendation_transactions)
        self.assertEqual(len(self.transaction_manager.verified_recommendations_of_trust_subject), num_verified_recommendations_of_trust_subject)
        self.assertEqual(len(self.transaction_manager.verified_recommendations_of_trust_subject_transaction_context), num_verified_recommendations_of_trust_subject_transaction_context)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_recommender_id), num_verified_trust_transactions_by_recommender_id)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_recommender_transaction_context), num_verified_trust_transactions_by_recommender_transaction_context)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_transaction_context), num_verified_trust_transactions_by_transaction_context)
        self.assertEqual(len(self.transaction_manager.verified_trust_transactions_by_trustee_and_transaction_context), num_verified_trust_transactions_by_trustee_and_transaction_context)
        

if __name__ == '__main__':
    unittest.main()
    
            
