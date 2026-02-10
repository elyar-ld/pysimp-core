import pytest
from src.pysimp.layers.layer_a import LayerA

def test_layer_a_saturation():
    """
    Test basic functionality of Layer A's saturation calculation.
    """
    layer = LayerA()
    result = layer.calculate_saturation({})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
