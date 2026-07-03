"""Main MCP server entry point for CISO Assistant"""

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("ciso-assistant")

# Import all tools to register them with the MCP server
from .tools.read_tools import (
    get_risk_scenarios,
    get_risk_scenario,
    get_applied_controls,
    get_audits_progress,
    get_folders,
    get_perimeters,
    get_risk_matrices,
    get_risk_matrix_details,
    get_risk_assessments,
    get_threats,
    get_assets,
    get_incidents,
    get_security_exceptions,
    get_frameworks,
    get_business_impact_analyses,
    get_requirement_assessments,
    get_requirement_assessment_observations,
    get_quantitative_risk_studies,
    get_quantitative_risk_scenarios,
    get_quantitative_risk_hypotheses,
    get_task_templates,
    get_task_template_details,
    get_vulnerabilities,
    get_vulnerability,
    get_asset_classes,
    get_users,
)

from .tools.detail_tools import (
    get_applied_control,
    get_requirement_assessment,
    get_asset,
    get_user,
    get_entity_assessment,
    get_attack_path,
    get_operational_scenario,
)

from .tools.evidence_tools import (
    get_evidences,
    get_evidence,
    create_evidence,
    update_evidence,
    delete_evidence,
    attach_evidence_file,
)

from .tools.risk_acceptance_tools import (
    get_risk_acceptances,
    get_risk_acceptance,
    create_risk_acceptance,
    update_risk_acceptance,
    delete_risk_acceptance,
    submit_risk_acceptance,
    draft_risk_acceptance,
    accept_risk_acceptance,
    reject_risk_acceptance,
    revoke_risk_acceptance,
)

from .tools.policy_tools import (
    get_policies,
    get_policy,
    create_policy,
    update_policy,
    delete_policy,
)

from .tools.findings_tools import (
    get_findings_assessments,
    get_findings_assessment,
    create_findings_assessment,
    update_findings_assessment,
    delete_findings_assessment,
    get_findings,
    get_finding,
    create_finding,
    update_finding,
    delete_finding,
)

from .tools.timeline_comment_tools import (
    get_timeline_entries,
    get_timeline_entry,
    create_timeline_entry,
    update_timeline_entry,
    delete_timeline_entry,
    get_comments,
    create_comment,
    update_comment,
    delete_comment,
)

from .tools.audit_tools import (
    get_compliance_assessment,
    update_compliance_assessment,
    delete_compliance_assessment,
    sync_compliance_assessment_to_applied_controls,
    get_compliance_assessment_global_score,
    get_compliance_assessment_quality_check,
    get_statement_of_applicability,
    get_controls_coverage,
    get_evidence_coverage,
    get_compliance_timeline,
    compare_compliance_assessments,
    map_compliance_assessment_from,
)

from .tools.applied_control_ops_tools import (
    delete_applied_control,
    duplicate_applied_control,
    merge_applied_controls,
    sync_applied_control_to_reference,
    get_applied_controls_todo,
    get_applied_controls_to_review,
    get_applied_controls_analytics,
)

from .tools.chat_tools import (
    get_chat_sessions,
    create_chat_session,
    delete_chat_session,
    get_indexed_documents,
    delete_indexed_document,
    get_questionnaire_runs,
    get_questionnaire_run,
    delete_questionnaire_run,
    get_agent_runs,
    get_agent_actions,
    set_agent_action_state,
)

from .tools.integrations_tools import (
    get_integration_providers,
    get_integration_configurations,
    get_integration_configuration,
    create_integration_configuration,
    update_integration_configuration,
    delete_integration_configuration,
    test_integration_connection,
    list_integration_remote_objects,
    run_integration_rpc,
)

from .tools.webhooks_tools import (
    get_webhook_event_types,
    get_webhook_endpoints,
    create_webhook_endpoint,
    update_webhook_endpoint,
    delete_webhook_endpoint,
    get_audit_sinks,
    create_audit_sink,
    update_audit_sink,
    delete_audit_sink,
    replay_audit_sink,
)

from .tools.doc_management_tools import (
    get_managed_documents,
    get_managed_document,
    create_managed_document,
    delete_managed_document,
    get_document_revisions,
    get_document_revision,
    update_document_revision,
    submit_document_revision_for_review,
    approve_document_revision,
    publish_document_revision,
    request_changes_on_document_revision,
)

from .tools.custom_fields_tools import (
    get_custom_field_definitions,
    get_custom_field_definition,
    create_custom_field_definition,
    update_custom_field_definition,
    delete_custom_field_definition,
)

from .tools.metrology_tools import (
    get_metric_definitions,
    create_metric_definition,
    update_metric_definition,
    delete_metric_definition,
    get_metric_instances,
    create_metric_instance,
    update_metric_instance,
    delete_metric_instance,
    get_custom_metric_samples,
    create_custom_metric_sample,
    get_dashboards,
    create_dashboard,
    delete_dashboard,
    get_dashboard_widgets,
)

from .tools.resilience_tools import (
    update_business_impact_analysis,
    delete_business_impact_analysis,
    get_business_impact_analysis_metrics,
    get_asset_assessments,
    create_asset_assessment,
    update_asset_assessment,
    delete_asset_assessment,
    get_escalation_thresholds,
    create_escalation_threshold,
    delete_escalation_threshold,
    get_dora_incident_reports,
    get_dora_incident_report,
    validate_dora_incident_report,
    delete_dora_incident_report,
)

from .tools.pmbok_tools import (
    get_projects,
    get_project,
    create_project,
    update_project,
    delete_project,
    get_accreditations,
    create_accreditation,
    update_accreditation,
    delete_accreditation,
    get_generic_collections,
    create_generic_collection,
    delete_generic_collection,
    get_responsibility_matrices,
    create_responsibility_matrix,
    delete_responsibility_matrix,
    cycle_responsibility_matrix_cell,
    get_responsibility_roles,
)

from .tools.sec_intel_tools import (
    get_security_advisories,
    get_security_advisory,
    create_security_advisory,
    delete_security_advisory,
    sync_kev_advisories,
    sync_euvd_advisories,
    enrich_security_advisory,
    get_cwes,
    get_cwe,
    sync_cwe_catalog,
)

from .tools.library_tools import (
    get_stored_library_content,
    get_stored_library_tree,
    delete_stored_library,
    unload_stored_library,
    get_loaded_library_content,
    get_loaded_library_tree,
    delete_loaded_library,
    update_loaded_library,
    get_available_loaded_library_updates,
)

from .tools.analysis_tools import (
    get_all_audits_with_metrics,
    get_audit_gap_analysis,
)

from .tools.library_tools import (
    get_stored_libraries,
    get_loaded_libraries,
    import_stored_library,
)

from .tools.write_tools import (
    create_folder,
    create_perimeter,
    create_asset,
    create_threat,
    create_applied_control,
    create_risk_assessment,
    create_risk_scenario,
    create_business_impact_analysis,
    create_compliance_assessment,
    create_quantitative_risk_study,
    create_quantitative_risk_scenario,
    create_quantitative_risk_hypothesis,
    refresh_quantitative_risk_study_simulations,
    create_task_template,
    create_vulnerability,
)

from .tools.update_tools import (
    update_asset,
    update_risk_scenario,
    update_applied_control,
    update_requirement_assessment,
    update_requirement_assessments,
    update_quantitative_risk_study,
    update_quantitative_risk_scenario,
    update_quantitative_risk_hypothesis,
    update_task_template,
    delete_task_template,
    update_vulnerability,
    delete_vulnerability,
)

from .tools.tprm_tools import (
    # Read tools
    get_entities,
    get_entity_assessments,
    get_representatives,
    get_solutions,
    get_contracts,
    # Write tools
    create_entity,
    create_entity_assessment,
    create_representative,
    create_solution,
    create_contract,
    # Update tools
    update_entity,
    update_entity_assessment,
    update_representative,
    update_solution,
    update_contract,
)

from .tools.ebios_rm_tools import (
    # Read tools
    get_ebios_rm_studies,
    get_feared_events,
    get_ro_to_couples,
    get_stakeholders,
    get_strategic_scenarios,
    get_attack_paths,
    get_operational_scenarios,
    get_elementary_actions,
    get_operating_modes,
    get_kill_chains,
    # Write tools
    create_ebios_rm_study,
    create_feared_event,
    create_ro_to_couple,
    create_stakeholder,
    create_strategic_scenario,
    create_attack_path,
    create_operational_scenario,
    create_elementary_action,
    create_operating_mode,
    create_kill_chain_step,
    # Update tools
    update_ebios_rm_study,
    update_feared_event,
    update_ro_to_couple,
    update_stakeholder,
    update_strategic_scenario,
    update_attack_path,
    update_operational_scenario,
    update_operating_mode,
    update_kill_chain_step,
)

# Register all tools with MCP decorators
mcp.tool()(get_risk_scenarios)
mcp.tool()(get_risk_scenario)
mcp.tool()(get_applied_controls)
mcp.tool()(get_audits_progress)
mcp.tool()(get_folders)
mcp.tool()(get_perimeters)
mcp.tool()(get_risk_matrices)
mcp.tool()(get_risk_matrix_details)
mcp.tool()(get_risk_assessments)
mcp.tool()(get_threats)
mcp.tool()(get_assets)
mcp.tool()(get_incidents)
mcp.tool()(get_security_exceptions)
mcp.tool()(get_frameworks)
mcp.tool()(get_business_impact_analyses)
mcp.tool()(get_requirement_assessments)
mcp.tool()(get_requirement_assessment_observations)
mcp.tool()(get_quantitative_risk_studies)
mcp.tool()(get_quantitative_risk_scenarios)
mcp.tool()(get_quantitative_risk_hypotheses)
mcp.tool()(get_task_templates)
mcp.tool()(get_task_template_details)
mcp.tool()(get_vulnerabilities)
mcp.tool()(get_vulnerability)
mcp.tool()(get_asset_classes)
mcp.tool()(get_users)

mcp.tool()(get_applied_control)
mcp.tool()(get_requirement_assessment)
mcp.tool()(get_asset)
mcp.tool()(get_user)
mcp.tool()(get_entity_assessment)
mcp.tool()(get_attack_path)
mcp.tool()(get_operational_scenario)

mcp.tool()(get_evidences)
mcp.tool()(get_evidence)
mcp.tool()(create_evidence)
mcp.tool()(update_evidence)
mcp.tool()(delete_evidence)
mcp.tool()(attach_evidence_file)

mcp.tool()(get_risk_acceptances)
mcp.tool()(get_risk_acceptance)
mcp.tool()(create_risk_acceptance)
mcp.tool()(update_risk_acceptance)
mcp.tool()(delete_risk_acceptance)
mcp.tool()(submit_risk_acceptance)
mcp.tool()(draft_risk_acceptance)
mcp.tool()(accept_risk_acceptance)
mcp.tool()(reject_risk_acceptance)
mcp.tool()(revoke_risk_acceptance)

mcp.tool()(get_policies)
mcp.tool()(get_policy)
mcp.tool()(create_policy)
mcp.tool()(update_policy)
mcp.tool()(delete_policy)

mcp.tool()(get_findings_assessments)
mcp.tool()(get_findings_assessment)
mcp.tool()(create_findings_assessment)
mcp.tool()(update_findings_assessment)
mcp.tool()(delete_findings_assessment)
mcp.tool()(get_findings)
mcp.tool()(get_finding)
mcp.tool()(create_finding)
mcp.tool()(update_finding)
mcp.tool()(delete_finding)

mcp.tool()(get_timeline_entries)
mcp.tool()(get_timeline_entry)
mcp.tool()(create_timeline_entry)
mcp.tool()(update_timeline_entry)
mcp.tool()(delete_timeline_entry)
mcp.tool()(get_comments)
mcp.tool()(create_comment)
mcp.tool()(update_comment)
mcp.tool()(delete_comment)

mcp.tool()(get_compliance_assessment)
mcp.tool()(update_compliance_assessment)
mcp.tool()(delete_compliance_assessment)
mcp.tool()(sync_compliance_assessment_to_applied_controls)
mcp.tool()(get_compliance_assessment_global_score)
mcp.tool()(get_compliance_assessment_quality_check)
mcp.tool()(get_statement_of_applicability)
mcp.tool()(get_controls_coverage)
mcp.tool()(get_evidence_coverage)
mcp.tool()(get_compliance_timeline)
mcp.tool()(compare_compliance_assessments)
mcp.tool()(map_compliance_assessment_from)

mcp.tool()(delete_applied_control)
mcp.tool()(duplicate_applied_control)
mcp.tool()(merge_applied_controls)
mcp.tool()(sync_applied_control_to_reference)
mcp.tool()(get_applied_controls_todo)
mcp.tool()(get_applied_controls_to_review)
mcp.tool()(get_applied_controls_analytics)

mcp.tool()(get_chat_sessions)
mcp.tool()(create_chat_session)
mcp.tool()(delete_chat_session)
mcp.tool()(get_indexed_documents)
mcp.tool()(delete_indexed_document)
mcp.tool()(get_questionnaire_runs)
mcp.tool()(get_questionnaire_run)
mcp.tool()(delete_questionnaire_run)
mcp.tool()(get_agent_runs)
mcp.tool()(get_agent_actions)
mcp.tool()(set_agent_action_state)

mcp.tool()(get_integration_providers)
mcp.tool()(get_integration_configurations)
mcp.tool()(get_integration_configuration)
mcp.tool()(create_integration_configuration)
mcp.tool()(update_integration_configuration)
mcp.tool()(delete_integration_configuration)
mcp.tool()(test_integration_connection)
mcp.tool()(list_integration_remote_objects)
mcp.tool()(run_integration_rpc)

mcp.tool()(get_webhook_event_types)
mcp.tool()(get_webhook_endpoints)
mcp.tool()(create_webhook_endpoint)
mcp.tool()(update_webhook_endpoint)
mcp.tool()(delete_webhook_endpoint)
mcp.tool()(get_audit_sinks)
mcp.tool()(create_audit_sink)
mcp.tool()(update_audit_sink)
mcp.tool()(delete_audit_sink)
mcp.tool()(replay_audit_sink)

mcp.tool()(get_managed_documents)
mcp.tool()(get_managed_document)
mcp.tool()(create_managed_document)
mcp.tool()(delete_managed_document)
mcp.tool()(get_document_revisions)
mcp.tool()(get_document_revision)
mcp.tool()(update_document_revision)
mcp.tool()(submit_document_revision_for_review)
mcp.tool()(approve_document_revision)
mcp.tool()(publish_document_revision)
mcp.tool()(request_changes_on_document_revision)

mcp.tool()(get_custom_field_definitions)
mcp.tool()(get_custom_field_definition)
mcp.tool()(create_custom_field_definition)
mcp.tool()(update_custom_field_definition)
mcp.tool()(delete_custom_field_definition)

mcp.tool()(get_metric_definitions)
mcp.tool()(create_metric_definition)
mcp.tool()(update_metric_definition)
mcp.tool()(delete_metric_definition)
mcp.tool()(get_metric_instances)
mcp.tool()(create_metric_instance)
mcp.tool()(update_metric_instance)
mcp.tool()(delete_metric_instance)
mcp.tool()(get_custom_metric_samples)
mcp.tool()(create_custom_metric_sample)
mcp.tool()(get_dashboards)
mcp.tool()(create_dashboard)
mcp.tool()(delete_dashboard)
mcp.tool()(get_dashboard_widgets)

mcp.tool()(update_business_impact_analysis)
mcp.tool()(delete_business_impact_analysis)
mcp.tool()(get_business_impact_analysis_metrics)
mcp.tool()(get_asset_assessments)
mcp.tool()(create_asset_assessment)
mcp.tool()(update_asset_assessment)
mcp.tool()(delete_asset_assessment)
mcp.tool()(get_escalation_thresholds)
mcp.tool()(create_escalation_threshold)
mcp.tool()(delete_escalation_threshold)
mcp.tool()(get_dora_incident_reports)
mcp.tool()(get_dora_incident_report)
mcp.tool()(validate_dora_incident_report)
mcp.tool()(delete_dora_incident_report)

mcp.tool()(get_projects)
mcp.tool()(get_project)
mcp.tool()(create_project)
mcp.tool()(update_project)
mcp.tool()(delete_project)
mcp.tool()(get_accreditations)
mcp.tool()(create_accreditation)
mcp.tool()(update_accreditation)
mcp.tool()(delete_accreditation)
mcp.tool()(get_generic_collections)
mcp.tool()(create_generic_collection)
mcp.tool()(delete_generic_collection)
mcp.tool()(get_responsibility_matrices)
mcp.tool()(create_responsibility_matrix)
mcp.tool()(delete_responsibility_matrix)
mcp.tool()(cycle_responsibility_matrix_cell)
mcp.tool()(get_responsibility_roles)

mcp.tool()(get_security_advisories)
mcp.tool()(get_security_advisory)
mcp.tool()(create_security_advisory)
mcp.tool()(delete_security_advisory)
mcp.tool()(sync_kev_advisories)
mcp.tool()(sync_euvd_advisories)
mcp.tool()(enrich_security_advisory)
mcp.tool()(get_cwes)
mcp.tool()(get_cwe)
mcp.tool()(sync_cwe_catalog)

mcp.tool()(get_stored_library_content)
mcp.tool()(get_stored_library_tree)
mcp.tool()(delete_stored_library)
mcp.tool()(unload_stored_library)
mcp.tool()(get_loaded_library_content)
mcp.tool()(get_loaded_library_tree)
mcp.tool()(delete_loaded_library)
mcp.tool()(update_loaded_library)
mcp.tool()(get_available_loaded_library_updates)

mcp.tool()(get_all_audits_with_metrics)
mcp.tool()(get_audit_gap_analysis)

mcp.tool()(get_stored_libraries)
mcp.tool()(get_loaded_libraries)
mcp.tool()(import_stored_library)

mcp.tool()(create_folder)
mcp.tool()(create_perimeter)
mcp.tool()(create_asset)
mcp.tool()(create_threat)
mcp.tool()(create_applied_control)
mcp.tool()(create_risk_assessment)
mcp.tool()(create_risk_scenario)
mcp.tool()(create_business_impact_analysis)
mcp.tool()(create_compliance_assessment)
mcp.tool()(create_quantitative_risk_study)
mcp.tool()(create_quantitative_risk_scenario)
mcp.tool()(create_quantitative_risk_hypothesis)
mcp.tool()(refresh_quantitative_risk_study_simulations)
mcp.tool()(create_task_template)
mcp.tool()(create_vulnerability)
mcp.tool()(update_vulnerability)
mcp.tool()(delete_vulnerability)

mcp.tool()(update_asset)
mcp.tool()(update_risk_scenario)
mcp.tool()(update_applied_control)
mcp.tool()(update_requirement_assessment)
mcp.tool()(update_requirement_assessments)
mcp.tool()(update_quantitative_risk_study)
mcp.tool()(update_quantitative_risk_scenario)
mcp.tool()(update_quantitative_risk_hypothesis)
mcp.tool()(update_task_template)
mcp.tool()(delete_task_template)

# TPRM tools
mcp.tool()(get_entities)
mcp.tool()(get_entity_assessments)
mcp.tool()(get_representatives)
mcp.tool()(get_solutions)
mcp.tool()(get_contracts)
mcp.tool()(create_entity)
mcp.tool()(create_entity_assessment)
mcp.tool()(create_representative)
mcp.tool()(create_solution)
mcp.tool()(create_contract)
mcp.tool()(update_entity)
mcp.tool()(update_entity_assessment)
mcp.tool()(update_representative)
mcp.tool()(update_solution)
mcp.tool()(update_contract)

# EBIOS RM tools
mcp.tool()(get_ebios_rm_studies)
mcp.tool()(get_feared_events)
mcp.tool()(get_ro_to_couples)
mcp.tool()(get_stakeholders)
mcp.tool()(get_strategic_scenarios)
mcp.tool()(get_attack_paths)
mcp.tool()(get_operational_scenarios)
mcp.tool()(get_elementary_actions)
mcp.tool()(get_operating_modes)
mcp.tool()(get_kill_chains)
mcp.tool()(create_ebios_rm_study)
mcp.tool()(create_feared_event)
mcp.tool()(create_ro_to_couple)
mcp.tool()(create_stakeholder)
mcp.tool()(create_strategic_scenario)
mcp.tool()(create_attack_path)
mcp.tool()(create_operational_scenario)
mcp.tool()(create_elementary_action)
mcp.tool()(create_operating_mode)
mcp.tool()(create_kill_chain_step)
mcp.tool()(update_ebios_rm_study)
mcp.tool()(update_feared_event)
mcp.tool()(update_ro_to_couple)
mcp.tool()(update_stakeholder)
mcp.tool()(update_strategic_scenario)
mcp.tool()(update_attack_path)
mcp.tool()(update_operational_scenario)
mcp.tool()(update_operating_mode)
mcp.tool()(update_kill_chain_step)


def run_server():
    """Run the MCP server"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
