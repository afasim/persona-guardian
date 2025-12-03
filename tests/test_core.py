"""Basic tests for persona_guardian.core module."""
import os
from pathlib import Path
from persona_guardian.core import TraitConfig, load_trait_config


def test_trait_config_creation():
    """Test creating a TraitConfig instance."""
    cfg = TraitConfig(
        name="test_trait",
        description="A test trait description",
        positive_prompt_template="Positive: {description}",
        negative_prompt_template="Negative: {description}",
        probe_questions=["Question 1?", "Question 2?"],
    )
    
    assert cfg.name == "test_trait"
    assert cfg.description == "A test trait description"
    assert cfg.layer_index == -1  # default value
    assert len(cfg.probe_questions) == 2


def test_trait_config_with_custom_layer():
    """Test TraitConfig with custom layer index."""
    cfg = TraitConfig(
        name="test",
        description="desc",
        positive_prompt_template="pos",
        negative_prompt_template="neg",
        probe_questions=["q1"],
        layer_index=15,
    )
    
    assert cfg.layer_index == 15


def test_load_sycophancy_config():
    """Test loading the sycophancy.yaml configuration file."""
    config_path = "traits/sycophancy.yaml"
    
    # Skip if file doesn't exist (e.g., when running tests outside repo)
    if not os.path.exists(config_path):
        return
    
    cfg = load_trait_config(config_path)
    
    assert cfg.name == "sycophancy"
    assert "sycophancy" in cfg.description.lower()
    assert len(cfg.probe_questions) == 5
    assert cfg.layer_index == -1
    assert "{description}" in cfg.positive_prompt_template
    assert "{description}" in cfg.negative_prompt_template


def test_trait_config_fields():
    """Test that all required fields are present."""
    cfg = TraitConfig(
        name="test",
        description="test description",
        positive_prompt_template="pos template",
        negative_prompt_template="neg template",
        probe_questions=["q1", "q2", "q3"],
    )
    
    # Verify all fields are accessible
    assert hasattr(cfg, 'name')
    assert hasattr(cfg, 'description')
    assert hasattr(cfg, 'positive_prompt_template')
    assert hasattr(cfg, 'negative_prompt_template')
    assert hasattr(cfg, 'probe_questions')
    assert hasattr(cfg, 'layer_index')


if __name__ == "__main__":
    # Simple test runner for manual testing
    print("Running tests...")
    test_trait_config_creation()
    print("✓ test_trait_config_creation passed")
    
    test_trait_config_with_custom_layer()
    print("✓ test_trait_config_with_custom_layer passed")
    
    test_load_sycophancy_config()
    print("✓ test_load_sycophancy_config passed")
    
    test_trait_config_fields()
    print("✓ test_trait_config_fields passed")
    
    print("\nAll tests passed!")
