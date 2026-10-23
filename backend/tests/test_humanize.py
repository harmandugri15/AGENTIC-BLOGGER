import pytest
from backend.app.services.humanizer import HumanizerEngine

def test_humanizer_engine_loop():
    engine = HumanizerEngine()
    test_text = """# Best Use Cases of AI in Enterprise
Furthermore, in today's fast-paced world, artificial intelligence is a game-changer.
Moreover, it is crucial to delve into the paradigm shift. The comprehensive analysis demonstrates value."""
    
    result = engine.run_humanization_loop(test_text, target_ai_threshold=25.0, max_iterations=3)
    assert result["final_ai_score"] <= result["initial_ai_score"]
    assert "#" not in result["final_text"]
    assert "Furthermore" not in result["final_text"]
    assert result["final_human_score"] >= 70.0
