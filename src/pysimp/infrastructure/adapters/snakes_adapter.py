
from typing import List, Any
import snakes.plugins
snakes.plugins.load('gv', 'snakes.nets', 'nets')
from snakes.nets import PetriNet, Place, Transition
from ...domain.services.layer_b import LayerB
from ...domain.entities.trace import SurgicalTrace

class SnakesLayerBAdapter(LayerB):
    """
    Adapter for Snakes library to validate Petri Net structures.
    """
    def __init__(self):
        pass

    def _build_net(self, template: Any) -> PetriNet:
        """
        Builds a Snakes PetriNet from the template definition.
        Assuming 'template.structure_definition' is a dict like:
        {
            'places': ['p_start', 'p_ready', 'p_end'],
            'transitions': [
                {'id': 't1', 'input': 'p_start', 'output': 'p_ready'},
                {'id': 't2', 'input': 'p_ready', 'output': 'p_end'}
            ],
            'initial_marking': 'p_start'
        }
        """
        net = PetriNet('TraceValidation')
        definition = template.structure_definition
        
        # Add Places
        for p_name in definition.get('places', []):
            net.add_place(Place(p_name))
            
        # Add Transitions
        for t_def in definition.get('transitions', []):
            t_id = t_def['id']
            net.add_transition(Transition(t_id))
            
            # Input Arcs (Place -> Transition)
            inputs = t_def.get('input', [])
            if isinstance(inputs, str): inputs = [inputs]
            for input_place in inputs:
                net.add_input(input_place, t_id, snakes.nets.Value('token'))
                
            # Output Arcs (Transition -> Place)
            outputs = t_def.get('output', [])
            if isinstance(outputs, str): outputs = [outputs]
            for output_place in outputs:
                net.add_output(output_place, t_id, snakes.nets.Value('token'))
                
        # Set Initial Marking
        initial_place = definition.get('initial_marking')
        if initial_place:
             # Basic token net for now
             net.place(initial_place).add('token')

        return net

    def validate_structure(self, trace_events: List[Any], template: Any) -> bool:
        """
        Validates if the sequence of trace events is structurally possible in the PN.
        This is a reachability check: M0 --t1--> M1 --t2--> ...
        """
        try:
            net = self._build_net(template)
        except Exception as e:
            print(f"Error building net: {e}")
            return False

        # Attempt to fire transitions in order
        for event in trace_events:
            t_id = event.surgit_id
            
            # Find the transition object
            try:
                transition = net.transition(t_id)
            except KeyError:
                print(f"Transition {t_id} not found in template.")
                return False
            
            # Check if enabled
            modes = transition.modes()
            if not modes:
                # Transition is not enabled (token missing in input place)
                print(f"Validation Failed: {t_id} cannot fire in current state. Trace invalid.")
                return False
            
            # Fire the transition (pick first mode, usually 'token')
            transition.fire(modes[0])
            
        return True

    def check_reachability(self, start_state: Any, target_state: Any) -> bool:
        # Placeholder for complex reachability analysis
        return True
