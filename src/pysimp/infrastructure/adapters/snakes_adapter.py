import snakes.plugins
snakes.plugins.load('gv', 'snakes.nets', 'nets')
from snakes.nets import PetriNet, Place, Transition, Value, Variable
from ...domain.services.layer_b import LayerB
from typing import List, Any, Set

class SnakesLayerBAdapter(LayerB):
    """
    Adapter for Snakes library to validate Petri Net structures.
    Implements SIM v1.2.0 Layer B: Normative Structural Layer.
    """

    def _build_net(self, template: Any) -> PetriNet:
        """
        Builds a Snakes PetriNet from the template definition (B1, B2).
        """
        net = PetriNet('ProcedureNet')
        definition = template.structure_definition
        
        # Add Places
        for p_name in definition.get('places', []):
            net.add_place(Place(p_name))
            
        # Add Transitions (B2: Surgit <-> Transition)
        for t_def in definition.get('transitions', []):
            t_id = t_def['id']
            # Using simple Transition class. Time constraints would use specialized classes if needed.
            net.add_transition(Transition(t_id))
            
            # Input Arcs
            inputs = t_def.get('input', [])
            if isinstance(inputs, str): inputs = [inputs]
            for input_place in inputs:
                # Value('token') indicates a simple black token.
                # In Layer B3, tokens have (ID, Context), but for structural reachability of a single trace, 
                # a black token representing "Current State" is sufficient for validity checking.
                net.add_input(input_place, t_id, Value('token'))
                
            # Output Arcs
            outputs = t_def.get('output', [])
            if isinstance(outputs, str): outputs = [outputs]
            for output_place in outputs:
                net.add_output(output_place, t_id, Value('token'))
                
        # Set Initial Marking (B11: Start State M0)
        initial_places = definition.get('initial_marking', [])
        if isinstance(initial_places, str): initial_places = [initial_places]
        
        for p_start in initial_places:
            net.place(p_start).add('token')

        return net

    def validate_structure(self, trace_events: List[Any], template: Any) -> bool:
        """
        Validates a trace against the normative Petri Net (B11).
        Checks:
        1. Fireability (Sequence Validity)
        2. Forbidden States (B12)
        3. Mandatory Transitions (B6 - Computed at end)
        """
        try:
            net = self._build_net(template)
        except Exception as e:
            print(f"Layer B Error: Failed to build Peti Net - {e}")
            return False

        # Track fired transitions for B6 (Mandatory Check)
        fired_transitions = set()
        
        # B12: Parse Forbidden States (List of Lists of Places that cannot be simultaneously marked)
        forbidden_markings = template.forbidden_states or [] # e.g., [['p_error', 'p_safe']]
        
        # Validate Initial State
        if self._is_forbidden(net, forbidden_markings):
            print("Layer B Violation: Initial state is forbidden.")
            return False

        # Attempt to fire transitions in order (B11)
        for event in trace_events:
            t_id = event.surgit_id
            
            if not net.has_transition(t_id):
                print(f"Layer B Violation: Transition {t_id} not found in normative net.")
                return False
            
            transition = net.transition(t_id)
            modes = transition.modes()
            
            if not modes:
                print(f"Layer B Violation: Transition {t_id} is not enabled in current state. Trace logic invalid.")
                # Retrieve current tokens for debugging
                current_marking = {p.name: p.tokens for p in net.place()}
                print(f"Current Marking: {current_marking}")
                return False
            
            # Fire!
            transition.fire(modes[0])
            fired_transitions.add(t_id)
            
            # Check B12: Forbidden States after firing
            if self._is_forbidden(net, forbidden_markings):
                print(f"Layer B Violation: State after {t_id} is forbidden.")
                return False
                
        # End of Trace Validation
        # B6: Check Mandatory Transitions
        # Get all mandatory surgits from template
        mandatory_surgits = self._get_mandatory_surgits(template)
        missing = mandatory_surgits - fired_transitions
        
        if missing:
            print(f"Layer B Violation: Mandatory transitions skipped (B6): {missing}")
            return False
            
        return True

    def _is_forbidden(self, net: PetriNet, forbidden_markings: List[List[str]]) -> bool:
        """
        Checks if current network marking matches any forbidden state definition.
        A forbidden state (list of places) is matched if ALL places in the list have at least one token.
        """
        for forbidden_set in forbidden_markings:
            # Check if all places in this forbidden set have tokens
            if all(len(net.place(p_name).tokens) > 0 for p_name in forbidden_set):
                return True
        return False
        
    def _get_mandatory_surgits(self, template: Any) -> Set[str]:
        """
        Extracts IDs of all mandatory surgits from the template steps.
        """
        mandatory = set()
        for step in template.steps.values():
            for s_id, surgit in step.surgits.items():
                if surgit.is_mandatory:
                    mandatory.add(s_id)
        return mandatory

    def check_reachability(self, start_state: Any, target_state: Any) -> bool:
        # Placeholder for complex reachability analysis
        return True
