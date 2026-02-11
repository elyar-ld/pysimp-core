
import sys
import os
import math

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pysimp.domain.services.layer_e import LayerE

def test_layer_e_bridge():
    # 1. Test Logit/Sigmoid Link
    p = 0.5
    logit_p = LayerE.logit(p)
    sigmoid_logit = LayerE.sigmoid(logit_p)
    print(f"Logit(0.5) = {logit_p} (Expected 0.0)")
    print(f"Sigmoid(0.0) = {sigmoid_logit} (Expected 0.5)")
    assert abs(logit_p) < 1e-9
    assert abs(sigmoid_logit - 0.5) < 1e-9
    
    # 2. Test Linear Predictor (E4)
    # alpha = -2.0 (Baseline risk low)
    # beta_delta = 1.0 (Saturation impact)
    # beta_s = 2.0 (Entropy impact)
    # Delta_SIM = 0.5
    # S_q_SIM = 0.25
    # eta = -2.0 + 1.0*0.5 + 2.0*0.25 = -2.0 + 0.5 + 0.5 = -1.0
    
    eta = LayerE.calculate_linear_predictor(
        alpha_k=-2.0, 
        beta_delta=1.0, 
        delta_sim=0.5, 
        beta_s=2.0, 
        s_q_sim=0.25
    )
    print(f"Linear Predictor eta = {eta} (Expected -1.0)")
    assert abs(eta - (-1.0)) < 1e-9
    
    # 3. Test PCP Probability (E3)
    # P = sigmoid(-1.0) = 1 / (1 + e^1) approx 0.2689
    prob = LayerE.predict_pcp_probability(eta)
    expected_prob = 1.0 / (1.0 + math.exp(1.0))
    print(f"PCP Probability P = {prob} (Expected {expected_prob})")
    assert abs(prob - expected_prob) < 1e-9
    
    print("Layer E Bridge Verification Passed!")

if __name__ == "__main__":
    test_layer_e_bridge()
