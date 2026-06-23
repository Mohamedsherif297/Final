# Face Encoding Guide

## Overview

This system now uses **pre-computed face encodings** for faster startup times. Instead of encoding 38+ images every time the program runs, encodings are generated once and loaded from a pickle file.

## Performance Comparison

| Method | Startup Time | When Used |
|--------|-------------|-----------|
| **Old Method** (encode each run) | ~30-45 seconds | Every program start |
| **New Method** (load encodings) | ~0.1-0.5 seconds | Every program start |
| **Savings** | **60-90x faster!** | 🚀 |

## How It Works

### 1. Initial Setup (One Time)

Generate encodings from your face images:

```bash
# Generate encodings from default location
python generate_encodings.py

# Or specify custom paths
python generate_encodings.py --faces-dir path/to/faces --output path/to/encodings.pkl
```

This creates `pi_minimal/known_faces/encodings.pkl` containing:
- Pre-computed 128-dimensional face encodings
- Associated person names
- Metadata (generation timestamp, image paths)

### 2. Run Your Application

The application automatically loads from `encodings.pkl`:

```bash
# Using ai_controller.py
python run_all_integrated.py

# Or using pi_minimal/main.py
cd pi_minimal
python main.py
```

**Output:**
```
[AI] Loading pre-computed encodings from pi_minimal/known_faces/encodings.pkl
[AI] Loaded 38 encodings in 0.15s
[AI] Generated at: 2026-06-23 14:30:22
[AI]   - Nahrawy: 38 encodings
```

### 3. Update Encodings (When Dataset Changes)

**When to regenerate:**
- Add new person images
- Remove person folders
- Update existing images
- Change image quality

**How to update:**
```bash
python generate_encodings.py
```

## File Structure

```
pi_minimal/known_faces/
├── encodings.pkl          ← Pre-computed encodings (load this)
├── images/                ← Source images (scan this)
│   ├── Nahrawy/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   └── Person2/
│       └── photo.jpg
└── README.txt
```

## Script Options

### Generate Encodings

```bash
# Basic usage (uses defaults)
python generate_encodings.py

# Custom directories
python generate_encodings.py \
  --faces-dir /custom/path/to/faces \
  --output /custom/path/to/encodings.pkl

# Verify existing encodings
python generate_encodings.py --verify
```

### Script Output

The script provides detailed progress:

```
============================================================
FACE ENCODINGS GENERATOR
============================================================
Scanning directory: pi_minimal/known_faces/images
------------------------------------------------------------
Found 1 person folder(s): Nahrawy
------------------------------------------------------------

Processing: Nahrawy
  Found 38 image(s)
  ✓ Processed 5/38 images...
  ✓ Processed 10/38 images...
  ✓ Completed Nahrawy: 38 encodings

============================================================
ENCODING COMPLETE
============================================================
Total images processed: 38
Total encodings generated: 38
Time taken: 12.34 seconds

Saving encodings to: pi_minimal/known_faces/encodings.pkl
✓ Encodings saved successfully!

Breakdown by person:
  - Nahrawy: 38 encodings
============================================================
```

## Fallback Behavior

If `encodings.pkl` is missing, the system automatically:
1. Detects the missing file
2. Falls back to real-time encoding from images
3. Suggests running `generate_encodings.py`

**Example:**
```
[AI] Encodings file not found: pi_minimal/known_faces/encodings.pkl
[AI] Generating encodings from images (this may take a while)...
[AI] Generated 38 encodings in 28.45s
[AI] Tip: Run 'python generate_encodings.py' to pre-compute encodings for faster startup
```

## Troubleshooting

### Issue: "No face detected in image"

**Cause:** Image doesn't contain a clear face or face is too small

**Solution:**
- Use front-facing photos with good lighting
- Ensure face is clearly visible and not obscured
- Minimum recommended size: 200x200 pixels

### Issue: "Multiple faces detected"

**Cause:** Image contains more than one person

**Solution:**
- Use photos with only the target person
- Crop images to show only one face
- The script will use the first detected face but may reduce accuracy

### Issue: Encodings file corrupted

**Cause:** Interrupted generation or file corruption

**Solution:**
```bash
# Delete corrupted file
rm pi_minimal/known_faces/encodings.pkl

# Regenerate
python generate_encodings.py
```

### Issue: Wrong directory structure

**Cause:** Images not in person subdirectories

**Solution:**
Ensure structure is:
```
known_faces/images/
  PersonName/
    image.jpg
```

NOT:
```
known_faces/images/
  image.jpg
```

## Best Practices

1. **Image Quality**
   - Use high-resolution images (>800x800 recommended)
   - Good, even lighting
   - Front-facing or slightly angled faces
   - Multiple expressions per person (5-10 images ideal)

2. **Dataset Updates**
   - Regenerate encodings after ANY changes to images
   - Keep `encodings.pkl` in version control (if desired)
   - Document when encodings were last updated

3. **Performance**
   - More images per person = better recognition accuracy
   - But: More images = larger encodings.pkl file
   - Balance: 5-15 varied images per person

4. **Automation**
   - Add encoding generation to your deployment script
   - Use `--verify` to check encodings before deployment

## Technical Details

**Encoding Format:**
- Each face → 128-dimensional floating-point vector
- Uses dlib's ResNet-based face recognition model
- Euclidean distance for matching (threshold: 0.5)

**Pickle File Contents:**
```python
{
    "encodings": [array(...), array(...), ...],  # 128-d vectors
    "names": ["Person1", "Person1", "Person2"],  # Corresponding names
    "image_paths": ["path/to/img1.jpg", ...],    # Source images
    "generated_at": "2026-06-23 14:30:22",       # Timestamp
    "total_images": 38,                          # Count
    "person_folders": ["Person1", "Person2"]     # Unique people
}
```

**File Size:**
- ~1 KB per encoding
- 38 encodings ≈ 40 KB
- 100 encodings ≈ 100 KB

## Integration with Existing Code

Both `ai_controller.py` and `pi_minimal/main.py` now:
1. **First:** Try to load from `encodings.pkl`
2. **Fallback:** Generate from images if file missing
3. **Display:** Show detailed timing and person breakdown

No changes needed to your main application code!

## Quick Reference

```bash
# Generate encodings (do this first!)
python generate_encodings.py

# Verify encodings
python generate_encodings.py --verify

# Run application (automatically loads encodings)
python run_all_integrated.py

# Update after adding new images
python generate_encodings.py
```

---

**Last Updated:** June 23, 2026
