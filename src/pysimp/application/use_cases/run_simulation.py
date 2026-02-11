
from pysimp.application.interfaces.repository import TraceRepository
from pysimp.domain.entities.trace import SurgicalTrace
from pysimp.domain.services.layer_a import LayerA
from pysimp.domain.services.layer_d import LayerD
from pysimp.domain.services.layer_e import LayerE
from pysimp.domain.services.layer_b import LayerB
from typing import List, Any, Optional, Dict

from pysimp.domain.services.layer_c import LayerC

from pysimp.domain.entities.report import (
    SimulationReport, StepMetric, NoiseMetric, CEMetric, PCPMetric, 
    TraceabilityEntry, ShapleyDecomposition
)
from pysimp.domain.entities.trace import SurgitType

class RunSimulation:
    def __init__(self, trace_repo: TraceRepository, layer_b_adapter: Optional[LayerB] = None):
        self.trace_repo = trace_repo
        self.layer_b = layer_b_adapter
        
    def _run_single_pass(self, trace_events, template, factor_mask=None) -> Dict[str, Any]:
        """
        Helper to run simulation logic with optional factor masking for Shapley.
        factor_mask: {'patient': bool, 'external': bool} - if False, treat noise as 1.0 (ideal).
        If both False, we get Ideal/Normative baseline (assuming intrinsic deviation is unavoidable baseline).
        """
        # 1. Initialize Aggregators
        step_metrics = {} 
        cumulative_sigma_res = 1.0
        z_state = LayerC.initialize_state()
        traceability = []
        
        step_table = []
        noise_table = []
        ce_table = []

        if not template: return {}

        for i, event in enumerate(trace_events):
             # A.I.3 Pauses
             if getattr(event, 'is_pause', False):
                 decay = template.dynamics_definition.get('provenance_decay', 1.0)
                 z_state.provenance_vector = LayerC.update_provenance(
                     z_state.provenance_vector, 0.0, lambda h: h * decay
                 )
                 noise_table.append(NoiseMetric(
                     step_id="PAUSE", n_t=1.0, e_t=1.0, 
                     pause_duration=(event.timestamp_end - event.timestamp_start).total_seconds()
                 ))
                 continue

             surgit_def = template.get_surgit(event.surgit_id)
             if not surgit_def: continue

             # Step ID
             step_id = None
             step_weight = 1.0
             for s_id, step in template.steps.items():
                 if event.surgit_id in step.surgits:
                     step_id = s_id
                     step_weight = step.weight_wt
                     break
             if not step_id: continue
             
             if step_id not in step_metrics:
                 step_metrics[step_id] = {'deviations': [], 'weight': step_weight}

             # Factor Masking for Shapley
             use_pat = factor_mask.get('patient', True) if factor_mask else True
             use_ext = factor_mask.get('external', True) if factor_mask else True
             
             n_t = event.noise_patient if use_pat else 1.0
             e_t = event.noise_external if use_ext else 1.0
             
             delta_intr = surgit_def.intrinsic_deviation
             sigma = surgit_def.mitigation_factor
             scope = surgit_def.security_scope

             # Calculate Deviations
             delta_tot = LayerA.calculate_total_deviation(delta_intr, n_t, e_t)
             
             # Layer A' Logic
             sigma_effective = cumulative_sigma_res
             if scope == "imm": sigma_effective *= sigma
             if scope == "res": 
                 sigma_effective *= sigma
                 cumulative_sigma_res *= sigma

             delta_final = LayerA.apply_mitigation(delta_tot, sigma_effective)
             step_metrics[step_id]['deviations'].append(delta_final)

             # Layer C: State
             decay = template.dynamics_definition.get('provenance_decay', 1.0)
             z_state = LayerC.transition_kernel(z_state, delta_final, n_t, e_t, decay_rate=decay)
             
             # Capture Traceability (A.III.2)
             traceability.append(TraceabilityEntry(
                 step_index=i, step_id=step_id, 
                 clinical_state_burden=z_state.clinical_state.get('general_burden', 0.0),
                 provenance_vector=list(z_state.provenance_vector)
             ))
             
             # Capture Metadata (A.III.1 Tables)
             noise_table.append(NoiseMetric(step_id=step_id, n_t=n_t, e_t=e_t))
             if event.surgit_type in [SurgitType.CE_SUBSTITUTION, SurgitType.CE_ADDITION]:
                 ce_table.append(CEMetric(
                     step_id=step_id, ce_type=event.surgit_type.value, 
                     timestamp=event.timestamp_start.isoformat()
                 ))

        # 2. Aggregation (Layer D)
        step_entropies = []
        rho_sim = 0.0
        
        for s_id, metrics in step_metrics.items():
            deviations = metrics['deviations']
            w_t = metrics['weight']
            
            pi_t = LayerD.calculate_step_linearity(deviations)
            delta_t = LayerD.calculate_step_deviation(pi_t)
            s_q_t = LayerD.calculate_step_entropy(pi_t, template.tsallis_q)
            
            step_table.append(StepMetric(
                step_id=s_id, m_t=0.0, pi_t=pi_t, delta_t=delta_t, 
                s_q_t=s_q_t, rho_t=delta_t, w_t=w_t
            ))
            
            step_entropies.append(s_q_t)
            rho_sim += w_t * delta_t # Approx rho using delta
            
        s_q_sim = LayerD.calculate_global_entropy(step_entropies, template.tsallis_q)
        
        alpha = template.weight_alpha
        beta = template.weight_beta
        global_score = LayerD.calculate_global_score(rho_sim, s_q_sim, alpha, beta)
        
        return {
            "score": global_score,
            "rho": rho_sim,
            "entropy": s_q_sim,
            "step_table": step_table,
            "noise_table": noise_table,
            "ce_table": ce_table,
            "traceability": traceability
        }

    def execute(self, trace_id: str, template: Any = None, q: float = 1.0) -> SimulationReport:
        """
        Orchestrates the simulation and returns a formal Annex III Report.
        """
        trace = self.trace_repo.get_trace(trace_id)
        if not trace: raise ValueError(f"Trace {trace_id} not found")

        # A.I.4 Validation (Skipping detail for brevity, assumed checked or check here)
        if template and self.layer_b:
            if not self.layer_b.validate_structure(trace.events, template):
                raise ValueError("Validation Failed (Handle gracefully in prod)") # Simplified

        # 1. Run Actual Simulation
        actual_res = self._run_single_pass(trace.events, template)
        
        # 2. Run Ideal Simulation (Baseline) for Decomposition
        # Ideal: No Patient Noise (n=1), No External Noise (e=1)
        ideal_res = self._run_single_pass(trace.events, template, factor_mask={'patient': False, 'external': False})
        
        # 3. Parameter Isolation (Simplified Decomposition)
        # Phi_Internal/Intrinsic is covered in Ideal Score.
        # Decomposition: Global Score = Ideal + Phi_Pat + Phi_Ext
        
        # Run with ONLY Patient noise (External = 1)
        pat_res = self._run_single_pass(trace.events, template, factor_mask={'patient': True, 'external': False})
        phi_patient = pat_res['score'] - ideal_res['score']
        
        # Run with ONLY External noise (Patient = 1)
        ext_res = self._run_single_pass(trace.events, template, factor_mask={'patient': False, 'external': True})
        phi_external = ext_res['score'] - ideal_res['score']
        
        # Phi Decision/Interaction: Residual difference (Total - (Ideal + Pat + Ext))
        # This captures interaction effects (synergy) or unaccounted factors assigned to 'Decision'
        phi_dec = actual_res['score'] - (ideal_res['score'] + phi_patient + phi_external)
        
        # 4. Layer E: PCP Calculation
        pcp_table = []
        if getattr(template, "calibration_coeffs", None):
            # Simplified using global metrics
            # E4 Linear Predictor
            eta = LayerE.calculate_linear_predictor(
                alpha_k=template.calibration_coeffs.get('alpha', 0.0),
                beta_delta=template.calibration_coeffs.get('beta_delta', 0.0),
                delta_sim=actual_res['rho'], # Using rho as proxy for Delta_SIM check defs
                beta_s=template.calibration_coeffs.get('beta_s', 0.0),
                s_q_sim=actual_res['entropy']
            )
            prob = LayerE.predict_pcp_probability(eta)
            pcp_table.append(PCPMetric(complication_type="General", p_k_sim=prob, eta_k=eta))

        # 5. Assemble Report
        decomp = ShapleyDecomposition(
            score_ideal=ideal_res['score'],
            phi_intrinsic=0.0, # Covered in Ideal? Or separate? Let's say Ideal Base
            phi_patient=phi_patient,
            phi_external=phi_external,
            phi_decision=phi_dec
        )
        
        return SimulationReport(
            trace_id=trace_id,
            GlobalMetrics={
                "S_q(SIM)": actual_res['entropy'],
                "rho_SIM": actual_res['rho'],
                "Score_SIM": actual_res['score']
            },
            StepTable=actual_res['step_table'],
            NoiseTable=actual_res['noise_table'],
            CETable=actual_res['ce_table'],
            PCPTable=pcp_table,
            Traceability=actual_res['traceability'],
            ShapleyDecomposition=decomp
        )
