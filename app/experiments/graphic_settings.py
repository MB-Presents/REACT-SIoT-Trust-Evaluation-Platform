


models_names_trust_inference = ['all_negative', 'All_Positive', 'Dynamic_Trust_Model', 'feed_forward_neural_network', 'TGN_Model']

# models_names = ['all_negative', 'All_Positive', 'Dynamic_Trust_Model', 'feed_forward_neural_network', 'TGN_Model']

models_names_mapping = {
    'all_negative': 'All Negative',
    'All_Positive': 'All Positive',
    'Dynamic_Trust_Model': 'Dynamic Trust Model',
    'feed_forward_neural_network': 'Feed Forward Neural Network',
    'TGN_Model': 'TGN-TI Model',
    'ctms_siot': 'CTMS-SIoT',
    'mctse_evaluation_model': 'MCTSE',
    'cbstm_iot': 'CBSTM-IoT',
    'ontology-based-trust-model': 'OBTBS',
    'ontology_based_trust_model': 'OBTBS',
    'context_aware_adaptive_trust_model': 'ICTCS',
}

color_mapping_trust_model_name = {
    'ontology-based-trust-model': 'red',
    'ontology_based_trust_model': 'red',
    'cbstm_iot': 'blue',
    'ctms_siot': 'green',
    'mctse_evaluation_model': 'orange',
    'context_aware_adaptive_trust_model': 'purple'
}
    
color_mapping_light_trust_model_name = {
    'ontology_based_trust_model': 'salmon',
    'cbstm_iot': 'lightblue',
    'ctms_siot': 'lightgreen',
    'mctse_evaluation_model': 'bisque',
    'context_aware_adaptive_trust_model': 'violet'
}



metrics_mapping = {
    'recall': 'Recall',
    'accuracy': 'Accuracy',
    'precision': 'Precision',
    'f1-score': 'F1-Score'
}

title_mapping = {
    'emergency':
        {
            'title': 'Emergency Calls'
        },
    'traffic_light':
        {
            'title': 'Traffic Light Prioritisation Request'
        },
    'combined':
        {
            'title': 'Overall'
        }
}


color_mapping_malicious_degree = {
            0.2: 'green',
            0.3: 'orange',
            0.4: 'purple',
            0.5: 'pink',
            0.6: 'red'
        }


color_mapping_malicious_degree_brighter = {
            0.2: 'lightgreen',
            0.3: 'lightcoral',
            0.4: 'violet',
            0.5: 'lightpink',
            0.6: 'lightcoral'
        }