"""
Example usage of the Imagination System.

This script demonstrates how to use the Imagination module to analyze styles
and generate reference images for artistic inspiration.
"""

import numpy as np
from PIL import Image

from imagination import (
    ImaginationModule,
    GenerationParams,
)


def main():
    """Demonstrate imagination module usage."""
    print("=== Cerebrum Imagination System Demo ===\n")
    
    # Initialize the imagination module
    print("1. Initializing Imagination Module...")
    imagination = ImaginationModule(simulation_mode=True)
    print("   ✓ Module initialized\n")
    
    # Create a sample canvas image
    print("2. Creating sample canvas...")
    canvas = np.random.randint(50, 200, (400, 400, 3), dtype=np.uint8)
    # Add some structure
    canvas[150:250, 150:250] = [200, 100, 100]  # Red square
    canvas[180:220, 180:220] = [100, 100, 200]  # Blue center
    print("   ✓ Canvas created (400x400)\n")
    
    # Analyze current style
    print("3. Analyzing current style...")
    style = imagination.tag_style_elements(
        canvas,
        analyze_colors=True,
        analyze_brushwork=True,
        analyze_lighting=True
    )
    print(f"   ✓ Style Analysis Complete:")
    print(f"     - Line Style: {style.line_style.value if style.line_style else 'N/A'}")
    print(f"     - Contrast: {style.contrast_level.value if style.contrast_level else 'N/A'}")
    
    if style.color_palette:
        print(f"     - Color Temperature: {style.color_palette.temperature:.2f} ({'warm' if style.color_palette.temperature > 0.5 else 'cool'})")
        print(f"     - Saturation: {style.color_palette.saturation:.2f}")
        print(f"     - Dominant Colors: {len(style.color_palette.dominant_colors)}")
    
    if style.brushwork:
        print(f"     - Stroke Visibility: {style.brushwork.stroke_visibility:.2f}")
        print(f"     - Texture Intensity: {style.brushwork.texture_intensity:.2f}")
    
    if style.lighting:
        print(f"     - Light Intensity: {style.lighting.intensity:.2f}")
    
    print(f"   Processing time: {style.processing_time_ms:.1f}ms\n")
    
    # Generate a stylized reference
    print("4. Generating stylized reference...")
    params = GenerationParams(
        strength=0.75,
        style_prompt="impressionist oil painting",
        guidance_scale=7.5,
        steps=50
    )
    suggestion = imagination.generate_stylized_reference(
        canvas,
        params,
        target_style=style
    )
    print(f"   ✓ Reference Generated: {suggestion.name}")
    print(f"     - Confidence: {suggestion.confidence:.1%}")
    print(f"     - Transferable Elements:")
    for element in suggestion.transferable_elements:
        print(f"       • {element}")
    print()
    
    # Get multiple style alternatives
    print("5. Suggesting alternative styles...")
    alternatives = imagination.suggest_alternative_style(
        canvas,
        current_style=style,
        n_suggestions=3
    )
    print(f"   ✓ Generated {len(alternatives)} style suggestions:\n")
    
    for i, alt in enumerate(alternatives, 1):
        print(f"   {i}. {alt.name}")
        print(f"      Confidence: {alt.confidence:.1%}")
        print(f"      Transferable: {', '.join(alt.transferable_elements[:3])}")
        if len(alt.transferable_elements) > 3:
            print(f"                    ... and {len(alt.transferable_elements) - 3} more")
        print()
    
    # Compare styles
    print("6. Comparing styles...")
    if alternatives:
        similarity = imagination.compare_styles(canvas, alternatives[0].reference_image)
        print(f"   ✓ Style similarity with '{alternatives[0].name}': {similarity:.1%}\n")
    
    # Extract transferable elements
    print("7. Extracting transferable elements from reference...")
    if alternatives:
        elements = imagination.extract_transferable_elements(
            alternatives[0].reference_image,
            canvas
        )
        print(f"   ✓ Found {len(elements)} transferable elements:")
        for element, info in elements.items():
            print(f"     • {element}:")
            if 'current' in info and 'suggested' in info:
                print(f"       Current: {info['current']:.2f}")
                print(f"       Suggested: {info['suggested']:.2f}")
            print(f"       Confidence: {info['confidence']:.1%}")
        print()
    
    # Demonstrate masked generation
    print("8. Generating with region mask...")
    mask = np.zeros((400, 400), dtype=np.float32)
    mask[100:300, 100:300] = 1.0  # Mask center region
    
    mask_params = GenerationParams(
        strength=0.8,
        style_prompt="watercolor wash"
    )
    masked_result = imagination.generate_with_mask(canvas, mask, mask_params)
    print(f"   ✓ Generated masked region (200x200 center)")
    print(f"     Result shape: {masked_result.shape}\n")
    
    # Save results (optional)
    print("9. Saving results...")
    try:
        # Save original canvas
        Image.fromarray(canvas).save("/tmp/canvas_original.png")
        print("   ✓ Saved: /tmp/canvas_original.png")
        
        # Save first suggestion
        if alternatives:
            Image.fromarray(alternatives[0].reference_image).save("/tmp/suggestion_1.png")
            print("   ✓ Saved: /tmp/suggestion_1.png")
        
        # Save masked result
        Image.fromarray(masked_result).save("/tmp/masked_result.png")
        print("   ✓ Saved: /tmp/masked_result.png")
    except Exception as e:
        print(f"   Note: Could not save images: {e}")
    
    print()
    
    # Clean up
    print("10. Cleaning up...")
    imagination.close()
    print("    ✓ Module closed\n")
    
    print("=== Demo Complete ===")
    print("\nKey Takeaways:")
    print("• Style analysis extracts transferable features (color, lighting, brushwork)")
    print("• Generated references are inspiration, not final output")
    print("• Only specific elements should be transferred to maintain artistic intent")
    print("• Masking allows region-specific style exploration")


if __name__ == "__main__":
    main()
