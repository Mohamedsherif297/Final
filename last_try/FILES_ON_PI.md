# Files Actually Used on Raspberry Pi

## ✅ Core System Files (6 files)

```
last_try/
├── run_all_integrated.py          # Main program - run this
├── system_state.py                # System state manager
├── ai_controller.py               # AI controller (replaced with no_mediapipe)
├── ai_controller_no_mediapipe.py  # Working AI without MediaPipe
└── requirements.txt               # Python dependencies
```

## ✅ Hardware Drivers (6 files)

```
last_try/hardware/
├── __init__.py                    # Package init
├── motor.py                       # Motor control
├── servo.py                       # Servo control
├── led.py                         # LED control
└── ultrasonic.py                  # Ultrasonic sensor
```

## ✅ Face Database

```
last_try/pi_minimal/known_faces/images/
├── obooda/                        # Face images
├── mezo/                          # Face images
├── karim A/                       # Face images
├── Nahrawy/                       # Face images (NEW)
└── Example_Person/                # Face images
```

## 📊 Total Files

- **Core:** 5 Python files + 1 requirements.txt
- **Hardware:** 5 Python files
- **Face Database:** ~20-30 image files across 5 people

**Total: ~35-40 files** (down from 100+)

---

## 🚀 How to Run on Pi

```bash
cd ~/surveillance-car/last_try
python3 run_all_integrated.py
```

---

## 🔄 How to Update Pi

```bash
# On laptop - push changes
cd "/Users/user/IOT /Final"
git add .
git commit -m "Update"
git push origin main

# On Pi - pull changes
cd ~/surveillance-car
git pull origin main
cd last_try
python3 run_all_integrated.py
```

---

## ⚠️ Note on pi_minimal folder

The `pi_minimal/` folder has read-only permissions and contains:
- `main.py` (not used by run_all_integrated.py)
- `requirements.txt` (not used)
- `known_faces/images/` (USED - face database)

Only the `known_faces/images/` subfolder is actually used by the system.
