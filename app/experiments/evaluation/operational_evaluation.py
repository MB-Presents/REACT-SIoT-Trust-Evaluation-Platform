from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Union

from typing import List

import numpy as np




from experiments.settings import Settings
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentStatus

if TYPE_CHECKING:
    from core.simulation.report_manager import ReportManager
    from core.models.uniform.components.report import SendingPacket

from core.models.uniform.components.report_models import ReportType


class PerformanceAccidentRecord:

    def __init__(self, accident: SendingPacket, time_report_scheduling, time_to_accident, time_to_hospital, time_total):
        # self.accident = accident
        self.time_report_scheduling = time_report_scheduling
        self.time_to_accident = time_to_accident
        self.time_to_hospital = time_to_hospital
        self.time_total = time_total


class PerformanceSimulationRun:

    def __init__(self) -> None:
        self.accident_records: List[PerformanceAccidentRecord] = []

        self.total_time_report_scheduling = 0
        self.total_time_to_accident = 0
        self.total_time_to_hospital = 0
        self.total_time_per_accident = 0

        self.average_time_report_scheduling = 0
        self.average_time_to_accident = 0
        self.average_time_to_hospital = 0
        self.average_time_per_accident = 0

    def add(self, operational_performance_accident_record: PerformanceAccidentRecord):
        self.accident_records.append(operational_performance_accident_record)

    def compute_overall_times(self):
        
        if len(self.accident_records) == 0:
            self.average_time_report_scheduling = np.nan
            self.average_time_to_accident = np.nan
            self.average_time_to_hospital = np.nan
            self.average_time_per_accident = np.nan
            
            return
        

        for accident_record in self.accident_records:
            self.total_time_report_scheduling += accident_record.time_report_scheduling
            self.total_time_to_accident += accident_record.time_to_accident
            self.total_time_to_hospital += accident_record.time_to_hospital
            self.total_time_per_accident += accident_record.time_total

        self.average_time_report_scheduling = self.total_time_report_scheduling / len(self.accident_records)
        self.average_time_to_accident = self.total_time_to_accident / len(self.accident_records)
        self.average_time_to_hospital = self.total_time_to_hospital / len(self.accident_records)
        self.average_time_per_accident = self.total_time_per_accident / len(self.accident_records)

    # def print_evaluation_records(self, prefix='/performance'):

    #     file_path = get_file_path(prefix + f"/performance_in_simulation_run.csv", "performance_evaluation")
    #     file_path.parent.mkdir(parents=True, exist_ok=True)

    #     f = open(file_path, "a")

    #     output = f"Report ID,\t Report Type,\tReport Authenticity,\tEvent ID,\tEvent Type,\tGround Truth,\tPrediction Type,\tPrediction Correct,\tAuthenticity Score \t, Event Catalyst \t, Object of Interest\t, Reporters \n"

    #     f.write(output)

    #     for record in self.accident_records:
    #         output = f"{record.accident.report_id},\t {record.time_report_scheduling},\t {record.time_to_accident},\t {record.time_to_hospital},\t {record.time_total}\n"
    #         f.write(output)

    #     result_of_total_times = f"Total Time Report Scheduling,\t {self.total_time_report_scheduling},\t Total Time to Accident,\t {self.total_time_to_accident},\t Total Time to Hospital,\t {self.total_time_to_hospital},\t Total Time per Accident,\t {self.total_time_per_accident}\n"

    #     result_of_average_times = f"Average Time Report Scheduling,\t {self.average_time_report_scheduling},\t Average Time to Accident,\t {self.average_time_to_accident},\t Average Time to Hospital,\t {self.average_time_to_hospital},\t Average Time per Accident,\t {self.average_time_per_accident}\n"

    #     f.write(result_of_total_times)
    #     f.write(result_of_average_times)

    #     f.close()


def evaluate(report_manager: ReportManager):
    
    performance_simulation_run = PerformanceSimulationRun()
    accident_reports = report_manager.get_reports_by_type(ReportType.EmergencyReport)
    
    
    
    for accident_key, accident in accident_reports.items():
        
        if accident.event_status != AccidentStatus.COMPLETE_SOLVED:
            continue
        
        report_time = accident.report_status_history[1]['time']
        report_scheduled_time = accident.report_status_history[2]['time']
        report_arrived_accident_time = accident.report_status_history[3]['time']
        report_arrived_hospital_time = accident.report_status_history[5]['time']
        
        time_report_processing: int = report_scheduled_time - report_time
        time_scheduled_report_accident: int = report_arrived_accident_time - report_scheduled_time
        time_accident_hospital : int = report_arrived_hospital_time - report_arrived_accident_time
            
        time_report_solved : int = report_arrived_hospital_time - report_time


        performance_record_accident = PerformanceAccidentRecord(accident, time_report_processing, time_scheduled_report_accident, time_accident_hospital, time_report_solved)


        performance_simulation_run.add(performance_record_accident) 

    performance_simulation_run.compute_overall_times()
    # performance_simulation_run.print_evaluation_records()



    return performance_simulation_run