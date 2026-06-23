# Raspberry Pi Setup Guide - New Features

## 📥 Pull Latest Changes

On your Raspberry Pi, navigate to your project directory and pull the latest code:

```bash
cd /path/to/your/project
git pull origin main
```

You should see:
```
Updating 9c38791..ae339ce
Fast-forward
 last_try/BEFORE_AFTER_COMPARISON.md       | 522 ++++++++++++++++++++
 last_try/CHANGES_SUMMARY.md              | 244 ++++++++++
 last_try/DATASET_COLLECTION_GUIDE.md     | 812 ++++++++++++++++++++++++++++++
 last_try/ENCODING_GUIDE.md               | 421 ++++++++++++++++
 last_try/FEATURES_SUMMARY.md             | 318 ++++++++++++
 last_try/QUICK_START.md                  | 178 +++++++
 last_try/README_ENCODINGS.md             | 523 ++++++++++++++++++++
 last_try/README_NEW_FEATURES.md          | 612 +++++++++++++++++++++++
 last_try/ai_controller.py                |  85 +++-
 last_try/collect_dataset.py              | 456 +++++++++++++++++
 last_try/generate_encodings.py           | 271 ++++++++++
 last_try/manage_encodings.sh             | 178 +++++++
 last_try/pi_minimal/main.py              |  79 ++-
 13 files changed, 4244 insertions(+), 28 deletions(-)
```

## ✅ Verify Files

Check that the new files are present:

```bash
cd last_try
ls -lh collect_dataset.py generate_encodings.py manage_encodings.sh
```

## 🚀 Quick Start on Raspberry Pi

### 1. First Time: Collect Your Dataset

```bash
cd last_try

# Collect face images for yourself (2 minutes)
python3 collect_dataset.py YourName

# During collection:
# - Move your head to different angles
# - Change distance from camera
# - Try different expressions
# - Face will be detected automatically
```

**What happens:**
- Camera opens with preview
- Captures ~120 images over 2 minutes
- Automatically generates encodings
- Saves to `pi_minimal/known_faces/images/YourName/`
- Updates `pi_minimal/known_faces/encodings.pkl`

### 2. Run the System

```bash
# Option A: Full integrated system
python3 run_all_integrated.py

# Option B: Minimal version with display
cd pi_minimal
python3 main.py --display

# Option C: Test without GPIO (if needed)
cd pi_minimal
python3 main.py --display --dry-run
```

### 3. Verify Encodings

```bash
# Check pre-computed encodings
python3 generate_encodings.py --verify

# Should show:
# - Total encodings
# - People in database
# - Generation timestamp
```

## 📊 What You'll See

### During Collection

Video window shows:
- Person name
- Time remaining
- Images captured count
- Face detection status
- Green box around detected face

Console output:
```
[  1] Captured: YourName_001.jpg (Time: 1s / 120s)
[  2] Captured: YourName_002.jpg (Time: 2s / 120s)
...
[118] Captured: YourName_118.jpg (Time: 120s / 120s)

============================================================
COLLECTION SUMMARY
============================================================
Images captured: 118
Success rate: 98.3%
```

### During Recognition

Visual overlay shows:
```
Tracking: YourName
Distance: 0.3245
Confidence: 67.5%
Face Size: 180x220px
Action: FORWARD
```

Console debug output:
```
[AI DEBUG] Best distance: 0.3245, Face size: 180x220px, Threshold: 0.5
```

## 🔧 Common Tasks

### Add Another Person

```bash
# Just run collection again with different name
python3 collect_dataset.py PersonName

# Encodings automatically merge with existing data
```

### Update Existing Person

```bash
# Collect more images (adds to existing)
python3 collect_dataset.py YourName

# Or regenerate all encodings
python3 generate_encodings.py
```

### Test Without Motors

```bash
cd pi_minimal
python3 main.py --display --dry-run

# Shows all debug info, no GPIO required
# Perfect for testing recognition
```

## ⚡ Performance Improvements

### Before (Old System)
```bash
[AI] Starting AI controller...
# ... wait 30-45 seconds ...
[AI] Loaded 38 known faces
```

### After (New System)
```bash
[AI] Starting AI controller...
[AI] Loading pre-computed encodings from pi_minimal/known_faces/encodings.pkl
[AI] Loaded 38 encodings in 0.15s  # ⚡ 200x faster!
[AI]   - YourName: 38 encodings
```

## 🐛 Troubleshooting

### Issue: Camera not working

```bash
# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL'); cap.release()"

# If fails, try different index
python3 -c "import cv2; cap = cv2.VideoCapture(1); print('OK' if cap.isOpened() else 'FAIL'); cap.release()"
```

### Issue: "mediapipe not installed"

```bash
# Install required packages
pip3 install mediapipe opencv-python face_recognition numpy

# Or use requirements file
cd pi_minimal
pip3 install -r requirements.txt
```

### Issue: "No face detected" during collection

**Solutions:**
- Ensure good lighting (even, not too bright/dark)
- Position face in center of frame
- Stay 1-3 feet from camera
- Face camera directly

### Issue: Low recognition confidence

**Solutions:**
```bash
# Collect more images with better variety
python3 collect_dataset.py YourName --duration 180

# Review and delete bad images
ls pi_minimal/known_faces/images/YourName/
# Delete blurry or bad images

# Regenerate encodings
python3 generate_encodings.py
```

### Issue: Slow startup still

**Solution:**
```bash
# Verify encodings file exists
ls -lh pi_minimal/known_faces/encodings.pkl

# If missing, generate it
python3 generate_encodings.py

# Verify it worked
python3 generate_encodings.py --verify
```

## 📖 Documentation

All documentation is now in the `last_try/` directory:

- **`README_NEW_FEATURES.md`** - Start here for complete overview
- **`QUICK_START.md`** - Quick commands and reference
- **`DATASET_COLLECTION_GUIDE.md`** - Detailed collection guide
- **`ENCODING_GUIDE.md`** - Encoding system documentation
- **`FEATURES_SUMMARY.md`** - Feature descriptions

## 🎯 Recommended Workflow

### First Run (Setup)

```bash
# 1. Pull latest code
cd /path/to/project/last_try
git pull origin main

# 2. Install dependencies (if needed)
pip3 install mediapipe opencv-python face_recognition numpy

# 3. Collect your face data
python3 collect_dataset.py YourName

# 4. Verify encodings
python3 generate_encodings.py --verify

# 5. Test recognition
python3 run_all_integrated.py
```

### Daily Use

```bash
# Just run the system
cd /path/to/project/last_try
python3 run_all_integrated.py

# Or with display for debugging
cd pi_minimal
python3 main.py --display
```

### Adding New People

```bash
# 1. Collect their data
python3 collect_dataset.py NewPerson

# 2. Run system
python3 run_all_integrated.py
```

## 💡 Tips for Best Results

### Collection Tips

1. **Lighting**: Even, diffused lighting works best
2. **Movement**: Vary angles and distances during collection
3. **Expressions**: Try neutral, smiling, and talking expressions
4. **Duration**: 2 minutes (120 images) is optimal
5. **Review**: Delete obviously bad images after collection

### Recognition Tips

1. **Monitor**: Watch console debug output for distance scores
2. **Confidence**: Aim for >70% confidence for reliable tracking
3. **Distance**: Optimal face size is 150-250px width
4. **Lighting**: Similar lighting to collection environment

### Performance Tips

1. **Encodings**: Always use pre-computed encodings (60-90x faster)
2. **Images**: 100-150 images per person is optimal
3. **Quality**: Delete blurry/bad images before generating encodings
4. **Updates**: Regenerate encodings after any dataset changes

## 🔄 Update Workflow

When you make changes on another machine and want to update the Pi:

```bash
# On Raspberry Pi
cd /path/to/project/last_try
git pull origin main

# If you updated images, regenerate encodings
python3 generate_encodings.py

# Test
python3 run_all_integrated.py
```

## ✅ Verification Checklist

After pulling code, verify:

- [ ] All new files present (`collect_dataset.py`, `generate_encodings.py`, etc.)
- [ ] Modified files updated (`ai_controller.py`, `pi_minimal/main.py`)
- [ ] Scripts are executable (`chmod +x collect_dataset.py manage_encodings.sh`)
- [ ] Dependencies installed (`mediapipe`, `face_recognition`, `opencv-python`)
- [ ] Camera working (test with collection script)
- [ ] Encodings generated (check for `encodings.pkl` file)

## 🎉 Success Indicators

You'll know it's working when:

1. **Collection runs smoothly** - Green box around face, images captured
2. **Encodings generated** - See success message after collection
3. **Fast startup** - "<1 second" loading message
4. **Recognition works** - Correct name shown in overlay
5. **High confidence** - >70% confidence scores
6. **Smooth tracking** - System follows you correctly

## 📞 Support

If you encounter issues:

1. Check documentation in `/last_try/` directory
2. Review troubleshooting sections
3. Test with `--display --dry-run` flags first
4. Verify camera and dependencies

---

**Ready to use on Raspberry Pi!** 🚀

Pull the code, collect your dataset, and enjoy 60-90x faster startup with automatic collection!
