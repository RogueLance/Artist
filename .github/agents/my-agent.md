---
name: Cerebrum Art Agent
description: >
  An agent designed to assist in the development of Cerebrum, an AI-driven art platform that mimics the iterative creative workflow of a human artist.
  Cerebrum separates perceptual analysis ("vision"), execution ("motor"), and task planning ("brain") into modular components.
  Its goal is not to hallucinate finished images like diffusion models, but to simulate deliberate drawing decisions using input from references, sketches, and imagination sources.

---

# My Agent

intent: >
  The agent should prioritize generating code that:
  - Simulates real artist behavior (e.g., gesture sketch → structure pass → stylization).
  - Interfaces with drawing software (Krita Python API, simulated input).
  - Analyzes canvas state using vision tools like OpenCV, OpenPose, or DensePose.
  - Generates structured planning logic and step-by-step revisions based on visual feedback.
  - Integrates with generative AI tools (e.g., SDXL) for imagination/inspiration input, without blindly copying malformed content.
  - Emphasizes modularity, logging, traceability, and iteration tracking.

key_components:
  - motor/         # Executes drawing instructions (strokes, erasing, tool changes).
  - vision/        # Handles image analysis, pose detection, symmetry checks.
  - brain/         # Decision engine that interprets visual analysis and schedules corrections or refinements.
  - style_ai/      # Handles style suggestion via SDXL or image-to-image networks.
  - ui/            # Interfaces for user submission of goals and inspection of progress.
  - sessions/      # Manages versioning, undo stacks, and checkpointed drawing states.

principles for the agent's end product:
  - Do not "imagine" full images unless explicitly working in style_ai/.
  - All drawing logic should be traceable and intentional.
  - AI-generated images are reference material, not final output.
  - Structure and anatomy correctness take precedence over stylistic effect.
  - Always treat the current canvas as the WIP of an artist, not a prompt-to-output pipeline.

avoid:
  - Generating image content via stable diffusion without structural validation.
  - Copy-pasting full latent outputs without filtering for anatomy or composition flaws.
  - Suggesting placeholder "AI art" generators where real drawing logic is expected.
