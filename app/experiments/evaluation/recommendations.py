from data_models.report_management.report.report_models import ReportType


from data_models.events.simulation_events import VerificationState
from data_models.report_management.report_manager import ReportManager
from sklearn.metrics import classification_report, confusion_matrix


def evaluate(report_manager: ReportManager, report_type: ReportType) -> dict:
    
    ground_trhuth = []
    prediction = []
    
    for report_id, report in report_manager.reports.items():
        if report.request_type == report_type and (report.trustworthiness == VerificationState.AUTHENTIC or report.trustworthiness == VerificationState.NOT_AUTHENTIC):
            
            prediction.append(report.trustworthiness == VerificationState.AUTHENTIC)
            ground_trhuth.append(report.simulation_event.is_authentic)
    
    confussion_matrix = confusion_matrix(ground_trhuth, prediction)
    dict_classification_report = classification_report(ground_trhuth, prediction,output_dict=True)
    
    
    evaluation_report = {
        "confussion_matrix": confussion_matrix,
        "classification_report": dict_classification_report
    }
        
    return evaluation_report 


