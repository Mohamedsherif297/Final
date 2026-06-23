# Dataset Collection & Debugging Guide

## Overview

This guide covers the new features added to the face recognition system:
1. **Automatic Dataset Collection** - Capture face images automatically
2. **Debugging Information** - View detailed recognition metrics
3. **Visual Overlays** - See real-time confidence and face data

## Features

### 1. Automatic Dataset Collection

Automatically collect face images for training the recognition system without manual intervention.

**Features:**
- ✅ Runs for 2 minutes (configurable)
- ✅ Captures ~1 image per second (~120 images)
- ✅ Uses MediaPipe for face detection
- ✅ No recognition required during collection
- ✅ Automatic directory creation
- ✅ Sequential filename generation
- ✅ Automatic encoding generation after collection
- ✅ Visual feedback during collection

### 2. Debugging Information

**Console Output:**
- Face distance score (similarity metric)
- Face dimensions in pixels (width × height)
- Recognition threshold comparison

**Visual Overlay (on video):**
- Current tracking target
- Face distance score
- Confidence percentage (0-100%)
- Face size in pixels
- Current action (forward, left, right, stop)

## Quick Start

### Collect Dataset for New Person

```bash
# Basic usage
python3 collect_dataset.py PersonName

# Example: Collect for "Alice"
python3 collect_dataset.py Alice
```

**What happens:**
1. Camera opens with preview window
2. Countdown: 3 seconds
3. Collection: 120 seconds (2 minutes)
4. Automatic encoding generation
5. Summary report

**During collection:**
- Move your head to different angles
- Try different distances from camera
- Vary facial expressions
- Change lighting if possible

### Custom Collection

```bash
# Collect for 60 seconds
python3 collect_dataset.py John --duration 60

# Capture every 0.5 seconds (more images)
python3 collect_dataset.py John --interval 0.5

# Headless mode (no display)
python3 collect_dataset.py John --no-display

# Skip automatic encoding generation
python3 collect_dataset.py John --no-encodings

# Custom output directory
python3 collect_dataset.py John --output /custom/path
```

## Usage Examples

### Example 1: Basic Collection

```bash
$ python3 collect_dataset.py Alice

Dataset Collector initialized
Person: Alice
Output directory: pi_minimal/known_faces/images/Alice
Duration: 120 seconds
Capture interval: 1.0 seconds
Expected images: ~120

============================================================
STARTING DATASET COLLECTION
============================================================
Press 'q' to stop early
Starting in 3 seconds...

[COLLECTING] Move your head to different angles and distances...
[COLLECTING] Try different expressions and lighting conditions...
[  1] Captured: Alice_001.jpg (Time: 1s / 120s)
[  2] Captured: Alice_002.jpg (Time: 2s / 120s)
...
[120] Captured: Alice_120.jpg (Time: 120s / 120s)

[COMPLETE] Collection time finished!

============================================================
COLLECTION SUMMARY
============================================================
Duration: 120 seconds
Images captured: 118
Face detection hits: 2580
Missed captures (no face): 2
Success rate: 98.3%
Saved to: pi_minimal/known_faces/images/Alice
============================================================

============================================================
GENERATING FACE ENCODINGS
============================================================
Loading existing encodings from: pi_minimal/known_faces/encodings.pkl
Loaded 38 existing encodings
Processing 118 images for Alice...
  [ 10/118] ✓ Processed...
  [ 20/118] ✓ Processed...
  ...
  [118/118] ✓ Processed...

Saving 156 total encodings to: pi_minimal/known_faces/encodings.pkl
✓ Encodings saved successfully!

============================================================
ENCODING SUMMARY
============================================================
New images processed: 118
New encodings generated: 116
Failed images: 2
Total encodings in database: 154

Failed images:
  - Alice_047.jpg: No face detected
  - Alice_089.jpg: No face detected

Encodings by person:
  - Alice: 116 encodings
  - Nahrawy: 38 encodings
============================================================

✓ Dataset collection complete!

Next steps:
  1. Review collected images in: pi_minimal/known_faces/images/Alice
  2. Remove any bad images (blurry, wrong person, etc.)
  3. If you removed images, run: python3 generate_encodings.py
  4. Run your application: python3 run_all_integrated.py
```

### Example 2: Quick Collection (60 seconds)

```bash
$ python3 collect_dataset.py Bob --duration 60 --interval 0.5

# Collects ~120 images in 60 seconds (faster capture rate)
```

### Example 3: Headless Collection (No Display)

```bash
$ python3 collect_dataset.py Charlie --no-display

# Useful for SSH/remote sessions or automated scripts
```

## Visual Feedback

### During Collection

The video window shows:
- **Person name** being collected
- **Time remaining** (countdown)
- **Images captured** count
- **Status**: "FACE DETECTED" (green) or "No face" (orange)
- **Green bounding box** around detected face

### During Recognition (Normal Operation)

The video overlay shows:
```
Tracking: Alice
Distance: 0.3245
Confidence: 67.5%
Face Size: 180x220px
Action: FORWARD
```

**Meaning:**
- **Tracking**: Person being followed
- **Distance**: Face similarity score (lower = better match)
  - 0.0-0.3: Excellent match
  - 0.3-0.5: Good match (threshold)
  - 0.5+: Poor match (not recognized)
- **Confidence**: Recognition confidence (0-100%)
  - 100% = perfect match (distance 0.0)
  - 0% = no match (distance 1.0+)
- **Face Size**: Face dimensions in pixels (width × height)
- **Action**: Current motor command

## Console Debug Output

When face recognition runs, you'll see debug prints:

```
[AI DEBUG] Best distance: 0.3245, Face size: 180x220px, Threshold: 0.5
[AI DEBUG] Best distance: 0.3198, Face size: 182x224px, Threshold: 0.5
[AI DEBUG] Best distance: 0.3412, Face size: 175x215px, Threshold: 0.5
```

**In pi_minimal/main.py (dry-run mode):**
```
[DEBUG] Distance: 0.3245, Face: 180x220px, Threshold: 0.5
turn_left known=Alice area=0.143 dist=0.3245
```

## File Structure

### Before Collection
```
pi_minimal/known_faces/
├── encodings.pkl
├── images/
│   └── Nahrawy/
│       └── ... (38 images)
└── README.txt
```

### After Collecting "Alice"
```
pi_minimal/known_faces/
├── encodings.pkl              ← Updated with Alice's encodings
├── images/
│   ├── Alice/                 ← NEW PERSON
│   │   ├── Alice_001.jpg
│   │   ├── Alice_002.jpg
│   │   └── ... (118 images)
│   └── Nahrawy/
│       └── ... (38 images)
└── README.txt
```

## Command Reference

### collect_dataset.py

```bash
python3 collect_dataset.py PERSON_NAME [OPTIONS]

Required:
  PERSON_NAME           Name of person to collect data for

Options:
  --duration SECONDS    Collection duration (default: 120)
  --interval SECONDS    Capture interval (default: 1.0)
  --output DIR          Output directory (default: pi_minimal/known_faces/images)
  --encodings-file PATH Encodings file path (default: pi_minimal/known_faces/encodings.pkl)
  --no-display          Run without video display (headless)
  --no-encodings        Skip automatic encoding generation
  -h, --help            Show help message
```

### Examples

```bash
# Standard collection
python3 collect_dataset.py Alice

# Fast collection (more images)
python3 collect_dataset.py Bob --duration 60 --interval 0.5

# Slow collection (careful selection)
python3 collect_dataset.py Charlie --duration 180 --interval 2.0

# Headless mode
python3 collect_dataset.py Dave --no-display

# Manual encoding later
python3 collect_dataset.py Eve --no-encodings

# Custom location
python3 collect_dataset.py Frank --output /data/faces
```

## Workflow

### Complete Workflow: Add New Person

```bash
# Step 1: Collect dataset
python3 collect_dataset.py Alice

# Step 2: Review images (optional)
open pi_minimal/known_faces/images/Alice

# Step 3: Remove bad images (optional)
# Delete any blurry, wrong angle, or incorrect images

# Step 4: Regenerate encodings if you removed images
python3 generate_encodings.py

# Step 5: Test recognition
python3 run_all_integrated.py
# or
cd pi_minimal
python3 main.py --display
```

### Update Existing Person

```bash
# Collect additional images
python3 collect_dataset.py Alice

# The script automatically merges with existing encodings
```

## Troubleshooting

### Issue: "No face detected" during collection

**Causes:**
- Face not in camera view
- Poor lighting
- Face too far or too close
- Camera angle too extreme

**Solutions:**
- Position face in center of frame
- Ensure good, even lighting
- Stay 1-3 feet from camera
- Face camera directly (especially at start)

### Issue: Low capture rate

**Symptoms:**
```
[WARN] No face detected for 5 intervals
[WARN] No face detected for 10 intervals
```

**Solutions:**
- Check lighting conditions
- Ensure face is visible
- Adjust distance from camera
- Check camera is working (test with regular photo app)

### Issue: Many failed encodings

**Symptoms:**
```
Failed images:
  - Alice_012.jpg: No face detected
  - Alice_034.jpg: No face detected
  ...
```

**Causes:**
- Images captured during face movement (blurry)
- Face partially out of frame
- Poor lighting in some frames
- Occlusions (hand, object blocking face)

**Solutions:**
- This is normal - expect 5-10% failure rate
- Failed images are automatically skipped
- If >20% fail, review collection conditions
- Delete failed images and recollect if needed

### Issue: Multiple people in frame

**Symptoms:**
```
⚠️  Multiple faces: Alice_045.jpg (using first)
```

**Solution:**
- Ensure only target person is in frame during collection
- Review and delete images with multiple people
- Regenerate encodings

### Issue: Camera not opening

**Symptoms:**
```
ERROR: Cannot open camera
```

**Solutions:**
```bash
# Check camera index
ls -l /dev/video*

# Try different camera index
python3 collect_dataset.py Alice --camera 1

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

## Best Practices

### Collection Tips

1. **Lighting**
   - Even, diffused lighting is best
   - Avoid strong backlighting
   - Collect in similar lighting to deployment environment

2. **Distance**
   - Start at 2-3 feet from camera
   - Move closer and farther during collection
   - Fill 20-30% of frame with face

3. **Angles**
   - Spend 60% time facing camera directly
   - Spend 40% time at slight angles
   - Include looking left, right, up, down

4. **Expressions**
   - Neutral expression (50%)
   - Smiling (30%)
   - Talking/varied expressions (20%)

5. **Accessories**
   - Collect both with and without glasses
   - Include common hats/headwear if relevant
   - Collect with different hairstyles if varies

### Quality Tips

1. **Image Count**
   - Minimum: 50 images
   - Recommended: 100-150 images
   - Maximum: 200-300 images (diminishing returns)

2. **Review Before Use**
   - Open collected folder
   - Delete very blurry images
   - Remove images with wrong person
   - Remove images with multiple people

3. **Encoding Success Rate**
   - Target: >90% encoding success
   - <80% success = poor collection quality
   - Review and possibly recollect

4. **Testing**
   - Test recognition after collection
   - Verify correct person is identified
   - Check confidence scores (should be >70%)

## Advanced Usage

### Automated Collection Script

```bash
#!/bin/bash
# collect_team.sh - Collect dataset for multiple people

PEOPLE=("Alice" "Bob" "Charlie" "Dave")

for person in "${PEOPLE[@]}"; do
    echo "Collecting dataset for $person"
    echo "Press Enter when ready..."
    read
    
    python3 collect_dataset.py "$person" --duration 120
    
    echo "Collection complete for $person"
    echo "Waiting 30 seconds before next person..."
    sleep 30
done

echo "All collections complete!"
```

### Batch Processing

```bash
# Collect for multiple people with delays
for name in Alice Bob Charlie; do
    python3 collect_dataset.py "$name"
    sleep 60  # Rest between collections
done

# Regenerate all encodings
python3 generate_encodings.py
```

### Custom Integration

```python
# Use in your own script
from collect_dataset import DatasetCollector, generate_encodings_for_person

# Collect dataset
collector = DatasetCollector(
    person_name="Alice",
    output_dir="pi_minimal/known_faces/images",
    duration=120,
    interval=1.0
)
success = collector.collect(display=True)

# Generate encodings
if success:
    generate_encodings_for_person(
        person_name="Alice",
        person_dir="pi_minimal/known_faces/images/Alice",
        encodings_file="pi_minimal/known_faces/encodings.pkl"
    )
```

## Understanding the Metrics

### Face Distance Score

**Range:** 0.0 (perfect match) to 1.0+ (no match)

**Interpretation:**
- **0.0-0.2**: Excellent match, same person with high certainty
- **0.2-0.4**: Good match, same person
- **0.4-0.5**: Marginal match, at threshold
- **0.5-0.6**: Poor match, likely different person
- **0.6+**: Very poor match, definitely different person

**Threshold:** 0.5 (configurable in code)

### Confidence Percentage

**Calculation:** `(1.0 - distance) × 100%`

**Interpretation:**
- **90-100%**: Excellent recognition
- **70-90%**: Good recognition
- **50-70%**: Acceptable recognition
- **30-50%**: Poor recognition (at threshold)
- **0-30%**: Failed recognition

### Face Size

**Typical ranges:**
- **Very close**: 300×350px and larger
- **Optimal**: 150×200px to 250×300px
- **Far**: 80×100px to 150×200px
- **Too far**: <80px (may not detect)

**Recommendations:**
- Collect at various distances
- System works best with 150-250px face width
- Too close: may have partial face
- Too far: may lose track or fail detection

## Debugging Tips

### Enable Verbose Output

```bash
# Run with display for visual feedback
cd pi_minimal
python3 main.py --display --dry-run

# Watch the debug output
[DEBUG] Distance: 0.3245, Face: 180x220px, Threshold: 0.5
turn_left known=Alice area=0.143 dist=0.3245
```

### Check Encoding Quality

```bash
# Verify encodings after collection
python3 generate_encodings.py --verify

# Should show:
# - Total encodings
# - People in database
# - Breakdown by person
```

### Test Recognition

```bash
# Test with display to see overlay
python3 run_all_integrated.py

# Watch overlay for:
# - Correct person name
# - Confidence >70%
# - Consistent tracking
```

## FAQ

**Q: How many images do I need?**
A: 100-150 images per person is optimal. Minimum 50, maximum 300.

**Q: Can I collect for the same person multiple times?**
A: Yes! The script automatically merges with existing encodings.

**Q: What if collection fails (crash, interrupt)?**
A: Partial data is saved. Run collection again - it will add more images.

**Q: Can I delete bad images after collection?**
A: Yes! Delete bad images, then run `python3 generate_encodings.py`.

**Q: Does collection affect existing encodings?**
A: No! Existing encodings are preserved and merged with new ones.

**Q: Can I collect without automatic encoding?**
A: Yes! Use `--no-encodings` flag, then run `generate_encodings.py` later.

**Q: How do I know if recognition is working?**
A: Check the overlay: confidence should be >70% and show correct name.

---

**Last Updated:** June 23, 2026
