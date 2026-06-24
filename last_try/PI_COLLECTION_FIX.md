# Raspberry Pi Dataset Collection - Fixed for No MediaPipe

## ✅ What Was Fixed

The `collect_dataset.py` script now uses **only face_recognition** for face detection instead of MediaPipe.

- ❌ Before: Required MediaPipe (not available on your Pi)
- ✅ After: Uses face_recognition only (already installed on your Pi)

## 📥 Pull the Fix

On your Raspberry Pi:

```bash
cd ~/surveillance-car/last_try

# Stash any local changes
git stash

# Pull the fix
git pull origin main

# Should show:
# Updating eeb73a1..4ab9d32
# Fast-forward
#  collect_dataset.py | 57 +++++++++++++++++++++-------------------
```

## 🚀 Now Try Collection

```bash
# Collect your face data (2 minutes)
python3 collect_dataset.py Mohamed

# Should work now! No MediaPipe error
```

## 📊 What to Expect

### During Collection

```
Dataset Collector initialized
Person: Mohamed
Output directory: pi_minimal/known_faces/images/Mohamed
Duration: 120 seconds
Capture interval: 1.0 seconds
Expected images: ~120
Using face_recognition for detection (no MediaPipe)

============================================================
STARTING DATASET COLLECTION
============================================================
Press 'q' to stop early
Starting in 3 seconds...

[COLLECTING] Move your head to different angles and distances...
[COLLECTING] Try different expressions and lighting conditions...
[  1] Captured: Mohamed_001.jpg (Time: 1s / 120s)
[  2] Captured: Mohamed_002.jpg (Time: 2s / 120s)
...
```

### Performance Note

- Face detection may be slightly slower than MediaPipe (1-2 FPS vs 5-10 FPS)
- This is normal on Raspberry Pi
- Still captures 1 image per second as designed
- Frame resizing is used to optimize performance

## 🐛 If You Still Have Issues

### Issue: "face_recognition not installed"

```bash
pip3 install face_recognition
```

### Issue: Slow detection / camera lag

This is normal on Pi. The script automatically:
- Resizes frames for faster detection
- Only processes frames when needed
- Still captures 1 image/second

### Issue: "No face detected"

Make sure:
- Good lighting (even, not too dark)
- Face centered in frame
- Stay 1-3 feet from camera
- Face camera directly

### Issue: Camera not opening

```bash
# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL'); cap.release()"
```

## ✅ Complete Workflow

```bash
# 1. Pull latest code
cd ~/surveillance-car/last_try
git stash
git pull origin main

# 2. Collect dataset
python3 collect_dataset.py Mohamed

# 3. Run system
python3 run_all_integrated.py
```

## 💡 Tips for Best Results

1. **Lighting**: Use even, natural lighting
2. **Movement**: Slowly move head to different angles
3. **Distance**: Vary distance from camera (1-4 feet)
4. **Expressions**: Try neutral, smiling, talking
5. **Duration**: Full 2 minutes for best coverage

## 🎯 Success Indicators

You'll know it's working when:
- No MediaPipe error ✅
- Camera opens with preview ✅
- Green boxes around your face ✅
- Images captured counter increases ✅
- ~120 images collected after 2 minutes ✅
- Automatic encoding generation ✅

## 📝 What Changed Technically

**Old (MediaPipe):**
```python
mp_face = mp.solutions.face_detection.FaceDetection()
results = mp_face.process(rgb)
```

**New (face_recognition):**
```python
face_locations = face_recognition.face_locations(rgb, model="hog")
```

Both detect faces, but face_recognition is already installed on your Pi!

---

**Now ready to use!** 🚀

No MediaPipe required - works with your existing Raspberry Pi setup!
