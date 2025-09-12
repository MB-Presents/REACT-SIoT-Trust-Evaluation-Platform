from experiments.settings import Settings
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings
from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import TrafficLightApplicationSettings
from trust.settings import TrustManagementSettings


def collect_settings():
    settings = {
        "General Settings": vars(Settings),
        "Accident Simulation Settings": vars(AccidentSettings),
        "Traffic Light Application Settings": vars(TrafficLightApplicationSettings),
        "Trust Management Settings": vars(TrustManagementSettings)
    }
    return settings

def write_report_to_file(settings, filename):
    with open(filename, 'w') as file:
        file.write("========================================\n")
        file.write(" SIoT Experiment Configuration Report\n")
        file.write("========================================\n\n")
           
        for category, settings_dict in settings.items():
            file.write(f"--- {category} ---\n")
            for key, value in sorted(settings_dict.items()):
                if key.startswith('__') and key.endswith('__'):
                    continue  # Skip internal Python attributes
                if isinstance(value, list) or isinstance(value, dict):
                    formatted_value = '\n    '.join(str(value).split(','))
                else:
                    formatted_value = value
                file.write(f"{key}: {formatted_value}\n")
            file.write("\n")
        