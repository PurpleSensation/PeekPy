#!/usr/bin/env python3
"""
Test script for multi-column tree layout functionality.
Develops and tests the cols parameter for the tree method.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from PeekPy.log import Log, TextBlockAssembler

def create_test_data():
    """Create test data similar to TransFusion train parameters."""
    return {
        "Optimization": {
            "dropout": 0.1,
            "batch_size": 32,
            "lr": 0.001,
            "gradient_clip": 2,
            "scheduler_rate": 1
        },
        "Regularization": {
            "VAO": False,
            "lambda_dif": 0,
            "lambda_fft": 0.0,
            "lambda_der": 0.3,
            "lambda_off": 0.0,
            "norm_strategy": "percentile_95"
        },
        "Latent Grid": {
            "dynamic_grid": False,
            "grid_size": [64, 64],
            "interpolation": "bilinear",
            "boundary_conditions": "periodic"
        },
        "Architecture": {
            "hidden_dim": 256,
            "n_layers": 4,
            "activation": "relu",
            "normalization": "batch"
        }
    }

def test_text_block_assembler():
    """Test the TextBlockAssembler independently."""
    print("=" * 60)
    print("TESTING TextBlockAssembler")
    print("=" * 60)
    
    # Create a simple 2x2 grid
    assembler = TextBlockAssembler(2, 2, col_widths=[25, 25])
    
    # Add content to each cell
    assembler.add_block(0, 0, ["First Column", "Line 2", "Line 3"])
    assembler.add_block(0, 1, ["Second Column", "More content"])
    assembler.add_block(1, 0, ["Row 2, Col 1"])
    assembler.add_block(1, 1, ["Row 2, Col 2", "Additional line"])
    
    # Render and display
    lines = assembler.render()
    for line in lines:
        print(line)

def test_original_tree():
    """Test the original single-column tree layout."""
    log = Log()
    log.set_debug_level(0)
    data = create_test_data()
    
    print("\n" + "=" * 60)
    print("ORIGINAL TREE (Single Column)")
    print("=" * 60)
    log.tree(data, "Train parameters")

def test_multi_column_tree():
    """Test the new multi-column tree layout."""
    log = Log()
    log.set_debug_level(2)  # Higher debug for more output
    data = create_test_data()
    
    print("\n" + "=" * 80)
    print("🧪 TESTING FIXED MULTI-COLUMN TREE LAYOUT")
    print("=" * 80)
    
    # Test 2 columns
    print("\n📋 TEST: 2 Columns")
    print("-" * 40)
    log.tree(data, "Train parameters (2 cols)", cols=2)
    
    # Test 3 columns  
    print("\n📋 TEST: 3 Columns")
    print("-" * 40)
    log.tree(data, "Train parameters (3 cols)", cols=3)
    
    # Test 4 columns
    print("\n📋 TEST: 4 Columns")
    print("-" * 40)
    log.tree(data, "Train parameters (4 cols)", cols=4)
    
    # Test with more complex data (similar to model parameters)
    model_data = {
        "Embeddings": {
            "sensor_dim": 16,
            "time_dim": 16,
            "value_dim": 32,
            "latent_dim": 128
        },
        "Encoder": {
            "enc_layers": 2,
            "enc_nhead": 2,
            "enc_ff_dim": 256,
            "enc_dropout": 0.1
        },
        "Decoder": {
            "dec_layers": 2,
            "dec_nhead": 2,
            "dec_ff_dim": 256,
            "dec_dropout": 0.1
        },
        "General": {
            "n_epochs": 0,
            "loss_last": "1.0e+00",
            "rmse_last": 1.00,
            "gradient_clip": 2,
            "keep_ratio": 1,
            "lambda_dif": 0,
            "lambda_fft": 0.0,
            "lambda_der": 0.3,
            "lambda_off": 0.0,
            "norm_strategy": "percentile_95",
            "lat_period": 0.5,
            "lat_stride": 1,
            "adaptive_latent": False,
            "latent_use_times": True
        }
    }
    
    print("\n📋 TEST: Complex Model Parameters (3 cols)")
    print("-" * 40)
    log.tree(model_data, "Model parameters", cols=3)
    
    # Test edge cases
    print("\n📋 TEST: Edge Case - Single Item")
    print("-" * 40)
    single_item = {"OnlyOne": {"single": "value"}}
    log.tree(single_item, "Single item test", cols=3)
    
    print("\n✅ TESTING COMPLETED!")
    print("Check for:")
    print("  ✓ Perfect header/content alignment")
    print("  ✓ Consistent column widths")
    print("  ✓ Proper border alignment")
    print("  ✓ Content truncation with ellipsis")

if __name__ == "__main__":
    # Test the new multi-column behavior with comprehensive checks
    test_multi_column_tree()
