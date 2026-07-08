export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface DDxItem {
  condition: string;
  confidence: 'low' | 'medium' | 'high';
  supporting_findings: string[];
  against_findings: string[];
  missing_information: string[];
  // Calibrated Confidence (Platt Scaling — backend tarafından doldurulur)
  raw_confidence?: number | null;
  calibrated_confidence?: number | null;
  evidence_support_score?: number | null;
}

export interface TreatmentPhase {
  phase: 'immediate' | 'short_term' | 'long_term';
  timeframe: string;
  actions: string[];
}

export interface MonitoringPlan {
  parameters: string[];
  frequency: string;
  red_flag_thresholds: string[];
}

export interface EvidenceRef {
  source: string;
  title: string;
  summary?: string | null;
  url?: string | null;
  evidence_level?: string | null;
  year?: string | null;
  pmid?: string | null;
}

export interface ClinicalRoadmap {
  risk_level: RiskLevel;
  red_flags: string[];
  differential_diagnosis: DDxItem[];
  recommended_departments: string[];
  immediate_action: string;
  doctor_visit_plan: string;
  tests_to_discuss: string[];
  treatment_topics_to_discuss: string[];
  treatment_phases: TreatmentPhase[];
  monitoring_plan: MonitoringPlan;
  lifestyle_modifications: string[];
  do_not_do: string[];
  follow_up_timeline: string;
  evidence_references: EvidenceRef[];
  safety_validated: boolean;
  disclaimer?: string;
  treatment_guidance?: string[] | null;
  safety_violations?: string[] | null;
  debug_trace?: string[] | null;
}

export default ClinicalRoadmap;
