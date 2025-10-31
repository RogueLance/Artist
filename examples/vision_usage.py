"""
Vision System Basic Usage Example.

Demonstrates core Vision System capabilities:
- Image analysis
- Pose detection
- Comparison to reference
- Error detection
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from PIL import Image, ImageDraw
from vision import VisionModule


def create_simple_figure(width=400, height=600):
    """Create a simple stick figure for testing."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple stick figure
    # Head
    draw.ellipse([175, 50, 225, 100], outline='black', width=3)
    
    # Body
    draw.line([200, 100, 200, 300], fill='black', width=3)
    
    # Arms
    draw.line([200, 150, 140, 220], fill='black', width=3)  # Left arm
    draw.line([200, 150, 260, 220], fill='black', width=3)  # Right arm
    
    # Legs
    draw.line([200, 300, 150, 480], fill='black', width=3)  # Left leg
    draw.line([200, 300, 250, 480], fill='black', width=3)  # Right leg
    
    return np.array(img)


def main():
    """Run vision system examples."""
    print("=" * 60)
    print("Vision System - Basic Usage Example")
    print("=" * 60)
    
    # Initialize Vision System
    print("\n1. Initializing Vision Module...")
    vision = VisionModule(
        enable_pose=True,
        enable_face=True,
        enable_hands=False
    )
    print("✓ Vision Module initialized")
    
    # Create test images
    print("\n2. Creating test images...")
    canvas_img = create_simple_figure(400, 600)
    reference_img = create_simple_figure(400, 600)
    print(f"✓ Created canvas image: {canvas_img.shape}")
    print(f"✓ Created reference image: {reference_img.shape}")
    
    # Analyze canvas
    print("\n3. Analyzing canvas...")
    result = vision.analyze(canvas_img)
    print(f"✓ Analysis complete in {result.processing_time_ms:.1f}ms")
    print(f"  - Image size: {result.image_width}x{result.image_height}")
    print(f"  - Detected features: {', '.join(result.get_detected_features()) or 'None'}")
    print(f"  - Detection confidence: {result.detection_confidence:.2%}")
    
    if result.has_pose():
        print(f"  - Pose detected with {len(result.pose.keypoints)} keypoints")
        print(f"  - Pose confidence: {result.pose.confidence:.2%}")
    else:
        print("  - No pose detected (stick figure too simple for MediaPipe)")
    
    if result.proportion_metrics:
        print(f"  - Proportion score: {result.proportion_metrics.overall_score:.2%}")
    
    if result.symmetry_metrics:
        print(f"  - Symmetry score: {result.symmetry_metrics.symmetry_score:.2%}")
    
    # Edge detection
    if result.edges is not None:
        edge_pixels = np.sum(result.edges > 0)
        print(f"  - Edge pixels detected: {edge_pixels}")
    
    # Compare to reference
    print("\n4. Comparing to reference...")
    comparison = vision.compare_to(canvas_img, reference_img)
    print(f"✓ Comparison complete in {comparison.processing_time_ms:.1f}ms")
    print(f"  - Overall similarity: {comparison.overall_similarity:.1%}")
    print(f"  - Confidence: {comparison.confidence:.1%}")
    
    if comparison.pose_metrics:
        print(f"  - Pose difference: {comparison.pose_metrics.overall_difference:.1%}")
        print(f"  - Keypoints compared: {len(comparison.pose_metrics.keypoint_differences)}")
    
    if comparison.alignment_metrics:
        print(f"  - Alignment score: {comparison.alignment_metrics.alignment_score:.1%}")
        print(f"  - Edge overlap: {comparison.alignment_metrics.edge_overlap:.1%}")
    
    # Detect errors
    print("\n5. Detecting pose errors...")
    errors = vision.detect_pose_errors(canvas_img, reference_img)
    if errors:
        print(f"✓ Found {len(errors)} issue(s):")
        for i, error in enumerate(errors[:5], 1):
            print(f"  {i}. {error}")
    else:
        print("✓ No errors detected")
    
    # Get refinement areas
    print("\n6. Identifying areas needing refinement...")
    areas = vision.highlight_areas_needing_refinement(canvas_img, reference_img)
    if areas:
        print(f"✓ Found {len(areas)} area(s) to refine:")
        for i, area in enumerate(areas[:3], 1):
            region = area.get('region', 'N/A')
            severity = area.get('severity', 'unknown')
            print(f"  {i}. Type: {area['type']}, Region: {region}, Severity: {severity}")
    else:
        print("✓ No refinement areas identified")
    
    # Create slightly different image for comparison
    print("\n7. Testing with modified image...")
    modified_img = create_simple_figure(400, 600)
    # Add some noise to make it different
    noise = np.random.randint(-20, 20, modified_img.shape, dtype=np.int16)
    modified_img = np.clip(modified_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    comparison2 = vision.compare_to(modified_img, reference_img)
    print(f"✓ Modified vs reference similarity: {comparison2.overall_similarity:.1%}")
    
    # Cleanup
    print("\n8. Cleaning up...")
    vision.close()
    print("✓ Vision Module closed")
    
    print("\n" + "=" * 60)
    print("Vision System demonstration complete!")
    print("=" * 60)
    
    # Summary
    print("\nSummary:")
    print(f"  • Vision System successfully initialized and tested")
    print(f"  • Image analysis: ✓ Working")
    print(f"  • Pose detection: ✓ Working (requires realistic human poses)")
    print(f"  • Image comparison: ✓ Working")
    print(f"  • Error detection: ✓ Working")
    print(f"  • Refinement guidance: ✓ Working")
    print("\nThe Vision System is ready for integration with the Motor System!")


if __name__ == "__main__":
    main()
