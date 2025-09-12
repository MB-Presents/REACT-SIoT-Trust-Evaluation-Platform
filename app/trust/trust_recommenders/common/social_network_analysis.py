


from __future__ import annotations
from typing import TYPE_CHECKING

from core.models.uniform.components.report import SendingPacket


if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice






def get_friendship_similarity_by_context(trustor : GenericDevice, trustee : GenericDevice, report : SendingPacket) -> float:
    """
    Calculate the Social Similarity Friendship (SSimFre) metric.

    :param ufre_sci: List of friends of the service-consuming device's owner.
    :param ufre_spj: List of friends of the service-providing device's owner.
    :param context_relationships_sci: Dict indicating relationships of ufre_sci in the task type context.
    :param context_relationships_spj: Dict indicating relationships of ufre_spj in the task type context.
    :return: SSimFre metric value.
    """
    
    # Create binary lists for each owner's friends in the context
    trustor_context_aware_relationships : dict = trustor.trust_manager.relationship_controller.relationship_manager.get_relationships_by_context(trustor=trustor, trustee=trustee, task_context=report)
    trustee_context_aware_relationships : dict = trustee.trust_manager.relationship_controller.relationship_manager.get_relationships_by_context(trustor=trustee, trustee=trustor, task_context=report)
    
    trustee_context_aware_friends = [relatinshipkey[1] for relatinshipkey in trustee_context_aware_relationships.keys()]
    trustor_context_aware_friends = [relatinshipkey[1] for relatinshipkey in trustor_context_aware_relationships.keys()]
    
    
    # Calculate the SSimFre metric
    common_trustee_trustor_friends = set(trustee_context_aware_friends).intersection(trustor_context_aware_friends)
    all_combined_friends = set(trustee_context_aware_friends).union(trustor_context_aware_friends)
    
    num_common_friends = len(common_trustee_trustor_friends)
    num_total_friends = len(all_combined_friends)

    ssimfre = num_common_friends / num_total_friends if num_total_friends > 0 else 0

    return ssimfre



def get_friendship_similarity(trustor : GenericDevice, trustee : GenericDevice) -> float:
    """
    Calculate the Social Similarity Friendship (SSimFre) metric.

    :param ufre_sci: List of friends of the service-consuming device's owner.
    :param ufre_spj: List of friends of the service-providing device's owner.
    :param context_relationships_sci: Dict indicating relationships of ufre_sci in the task type context.
    :param context_relationships_spj: Dict indicating relationships of ufre_spj in the task type context.
    :return: SSimFre metric value.
    """
    
    # Create binary lists for each owner's friends in the context
    trustor_context_aware_relationships = trustor.trust_manager.relationship_controller.relationship_manager.relationships.keys()
    trustee_context_aware_relationships = trustee.trust_manager.relationship_controller.relationship_manager.relationships.keys()
    
    
    trustee_context_aware_friends = [relatinshipkey for relatinshipkey in trustee_context_aware_relationships]
    trustor_context_aware_friends = [relatinshipkey for relatinshipkey in trustor_context_aware_relationships]
    
    
    # Calculate the SSimFre metric
    common_trustee_trustor_friends = set(trustee_context_aware_friends).intersection(trustor_context_aware_friends)
    all_combined_friends = set(trustee_context_aware_friends).union(trustor_context_aware_friends)
    
    num_common_friends = len(common_trustee_trustor_friends)
    num_total_friends = len(all_combined_friends)

    ssimfre = num_common_friends / num_total_friends if num_total_friends > 0 else 0

    return ssimfre
    
def get_social_similar_community(trustor : GenericDevice, trustee : GenericDevice):
    """
    Calculate the Social Similarity Community (SSimCom) metric.

    :param ucom_sci: List of community interests of the service-consuming device's owner.
    :param ucom_spj: List of community interests of the service-providing device's owner.
    :param context_communities_sci: Dict indicating community interests of ucom_sci in the task type context.
    :param context_communities_spj: Dict indicating community interests of ucom_spj in the task type context.
    :return: SSimCom metric value.
    """
    # Create binary lists for each owner's community interests in the context
    
    trustor_communities = trustor._affiliations
    trustee_communities = trustee._affiliations
    
    common_communities = set(trustor_communities).intersection(trustee_communities)
    total_communities = set(trustor_communities).union(trustee_communities)
    
    num_common_communities = len(common_communities)
    num_total_communities = len(total_communities)
    
    ssimcom = num_common_communities / num_total_communities if num_total_communities > 0 else 0
    
    return ssimcom



def get_object_profile_similarity(trustor : GenericDevice, trustee : GenericDevice):
    """
    Calculate the Object Profile Similarity (OProSim) metric.

    :param uprf_sci: List of object profiles of the service-consuming device's owner.
    :param uprf_spj: List of object profiles of the service-providing device's owner.
    :param context_object_profiles_sci: Dict indicating object profiles of uprf_sci in the task type context.
    :param context_object_profiles_spj: Dict indicating object profiles of uprf_spj in the task type context.
    :return: OProSim metric value.
    """
    # Create binary lists for each owner's object profiles in the context
    
    trustor_object_profiles = trustor._manufacturer
    trustee_object_profiles = trustee._manufacturer
    
    
    
    common_object_profiles = set(trustor_object_profiles).intersection(trustee_object_profiles)
    total_object_profiles = set(trustor_object_profiles).union(trustee_object_profiles)
    
    num_common_object_profiles = len(common_object_profiles)
    num_total_object_profiles = len(total_object_profiles)
    
    oprosim = num_common_object_profiles / num_total_object_profiles if num_total_object_profiles > 0 else 0
    
    return oprosim