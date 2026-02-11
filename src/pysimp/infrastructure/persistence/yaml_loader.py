
import yaml
from pathlib import Path
from typing import Union
from pysimp.domain.entities.template import NormativeTemplate
from pysimp.domain.entities.surgit import Surgit

from pysimp.domain.entities.step import Step

class YamlTemplateLoader:
    """
    Infrastructure service to load NormativeTemplate from a YAML file.
    Supports Annex I hierarchy: Procedure -> Steps -> Surgits
    """
    
    @staticmethod
    def load(file_path: Union[str, Path]) -> NormativeTemplate:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
            
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
        # Parse Steps and their Surgits
        steps_dict = {}
        if 'steps' in data:
            for step_id, step_data in data['steps'].items():
                surgits_in_step = {}
                for s_id, s_data in step_data.get('surgits', {}).items():
                    delta_intr = s_data.get('intrinsic_deviation')
                    if delta_intr is None:
                        # Backward compatibility: base_probability = pi = 1 - delta
                        base_prob = s_data.get('base_probability', 1.0)
                        delta_intr = 1.0 - base_prob
                    
                    surgits_in_step[s_id] = Surgit(
                        id=s_id,
                        name=s_data['name'],
                        description=s_data.get('description'),
                        intrinsic_deviation=delta_intr,
                        mitigation_factor=s_data.get('mitigation_factor', 1.0),
                        security_scope=s_data.get('security_scope', 'imm'),
                        complexity_weight=s_data.get('complexity_weight', 0.1),
                        is_mandatory=s_data.get('is_mandatory', True),
                        is_safety=s_data.get('is_safety', False)
                    )
                
                steps_dict[step_id] = Step(
                    id=step_id,
                    name=step_data['name'],
                    description=step_data.get('description'),
                    weight_wt=step_data.get('weight_wt', 1.0),
                    surgits=surgits_in_step
                )
        else:
            # Fallback for old flattened format (though we are migrating to hierarchy)
            # This handles potential legacy or simple lists by putting them in a "DEFAULT" step
            # ... (Implementation simplified for now to enforce new structure)
            pass

        return NormativeTemplate(
            procedure_type=data['procedure_type'],
            version=data['version'],
            steps=steps_dict,
            complication_set_k=data.get('complication_set_k', []),
            calibration_coefficients=data.get('calibration_coefficients', {}),
            forbidden_states=data.get('forbidden_states', []),
            dynamics_definition=data.get('dynamics_definition', {}),
            shapley_convention=data.get('shapley_convention', 'default'),
            tsallis_q=data.get('tsallis_q', 1.0),
            weight_alpha=data.get('weight_alpha', 1.0),
            weight_beta=data.get('weight_beta', 1.0),
            structure_definition=data['structure_definition']
        )
