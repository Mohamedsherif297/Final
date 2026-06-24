#!/usr/bin/env python3
"""
Dataset Collection Script
Automatically collects face images for training the face recognition system.

Features:
- Runs for 2 minutes
- Captures ~1 image per second (~120 images total)
- Uses face_recognition for face detection (no MediaPipe required)
- Automatically generates encodings after collection
- Saves to known_faces/images/<PERSON_NAME>/
"""
import argparse
import os
import time
import cv2
import sys
from pathlib import Path

try:
    import face_recognition
    FACE_RECOG_AVAILABLE = True
except ImportError:
    print("ERROR: face_recognition not installed")
    print("Install with: pip3 install face_recognition")
    sys.exit(1)

# Configuration
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
COLLECTION_DURATION_SECONDS = 120  # 2 minutes
CAPTURE_INTERVAL_SECONDS = 1.0  # 1 image per second
KNOWN_FACES_DIR = "pi_minimal/known_faces/images"
ENCODINGS_FILE = "pi_minimal/known_faces/encodings.pkl"


class DatasetCollector:
    """Automatic face dataset collection using face_recognition library"""
    
    def __init__(self, person_name: str, output_dir: str, duration: int = 120, interval: float = 1.0):
        self.person_name = person_name
        self.output_dir = output_dir
        self.duration = duration
        self.interval = interval
        
        # Create person directory
        self.person_dir = os.path.join(output_dir, person_name)
        os.makedirs(self.person_dir, exist_ok=True)
        
        # Statistics
        self.images_captured = 0
        self.faces_detected = 0
        self.no_face_count = 0
        
        print(f"Dataset Collector initialized")
        print(f"Person: {person_name}")
        print(f"Output directory: {self.person_dir}")
        print(f"Duration: {duration} seconds")
        print(f"Capture interval: {interval} seconds")
        print(f"Expected images: ~{int(duration / interval)}")
        print(f"Using face_recognition for detection (no MediaPipe)")
    
    def get_next_filename(self) -> str:
        """Get next available filename in sequence"""
        existing_files = []
        if os.path.exists(self.person_dir):
            for fname in os.listdir(self.person_dir):
                if fname.startswith(self.person_name) and fname.endswith('.jpg'):
                    try:
                        # Extract number from filename
                        num_str = fname.replace(self.person_name + '_', '').replace('.jpg', '')
                        existing_files.append(int(num_str))
                    except ValueError:
                        continue
        
        # Get next number
        next_num = max(existing_files) + 1 if existing_files else 1
        return os.path.join(self.person_dir, f"{self.person_name}_{next_num:03d}.jpg")
    
    def detect_face(self, frame):
        """Detect face using face_recognition library"""
        # Resize frame for faster detection (optional, but helps on Pi)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(rgb, model="hog")
        
        if face_locations:
            # Scale back up face locations since frame was scaled down
            top, right, bottom, left = face_locations[0]
            face_bbox = (top * 2, right * 2, bottom * 2, left * 2)
            return True, face_bbox
        return False, None
    
    def draw_info(self, frame, face_detected: bool, time_remaining: int, 
                  images_captured: int, faces_detected: int):
        """Draw collection information on frame"""
        # Background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (630, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Text information
        color = (0, 255, 0) if face_detected else (0, 165, 255)
        
        cv2.putText(frame, f"Person: {self.person_name}", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Time remaining: {time_remaining}s", (20, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.putText(frame, f"Images captured: {images_captured}", (20, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        status = "FACE DETECTED" if face_detected else "No face"
        cv2.putText(frame, f"Status: {status}", (20, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def collect(self, display: bool = True):
        """Run collection process"""
        print("\n" + "=" * 60)
        print("STARTING DATASET COLLECTION")
        print("=" * 60)
        print(f"Press 'q' to stop early")
        print(f"Starting in 3 seconds...")
        time.sleep(3)
        
        # Open camera
        cap = cv2.VideoCapture(CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        if not cap.isOpened():
            print("ERROR: Cannot open camera")
            return False
        
        start_time = time.time()
        last_capture_time = 0
        
        print("\n[COLLECTING] Move your head to different angles and distances...")
        print("[COLLECTING] Try different expressions and lighting conditions...")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("WARNING: Failed to read frame")
                    continue
                
                current_time = time.time()
                elapsed = current_time - start_time
                time_remaining = max(0, int(self.duration - elapsed))
                
                # Check if collection is complete
                if elapsed >= self.duration:
                    print("\n[COMPLETE] Collection time finished!")
                    break
                
                # Detect face
                face_detected, detection = self.detect_face(frame)
                if face_detected:
                    self.faces_detected += 1
                
                # Capture image at intervals
                if current_time - last_capture_time >= self.interval:
                    if face_detected:
                        # Save image
                        filename = self.get_next_filename()
                        cv2.imwrite(filename, frame)
                        self.images_captured += 1
                        last_capture_time = current_time
                        
                        print(f"[{self.images_captured:3d}] Captured: {os.path.basename(filename)} "
                              f"(Time: {int(elapsed)}s / {self.duration}s)")
                    else:
                        self.no_face_count += 1
                        if self.no_face_count % 5 == 0:
                            print(f"[WARN] No face detected for {self.no_face_count} intervals")
                
                # Draw information
                if display:
                    display_frame = frame.copy()
                    self.draw_info(display_frame, face_detected, time_remaining,
                                 self.images_captured, self.faces_detected)
                    
                    # Draw face bounding box if detected
                    if face_detected and detection:
                        top, right, bottom, left = detection
                        cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    cv2.imshow("Dataset Collection", display_frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n[STOPPED] Collection stopped by user")
                    break
        
        except KeyboardInterrupt:
            print("\n[STOPPED] Collection interrupted by user")
        
        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()
        
        # Print summary
        print("\n" + "=" * 60)
        print("COLLECTION SUMMARY")
        print("=" * 60)
        print(f"Duration: {int(elapsed)} seconds")
        print(f"Images captured: {self.images_captured}")
        print(f"Face detection hits: {self.faces_detected}")
        print(f"Missed captures (no face): {self.no_face_count}")
        print(f"Success rate: {self.images_captured / max(1, self.images_captured + self.no_face_count) * 100:.1f}%")
        print(f"Saved to: {self.person_dir}")
        print("=" * 60)
        
        return self.images_captured > 0


def generate_encodings_for_person(person_name: str, person_dir: str, encodings_file: str):
    """Generate face encodings for collected images"""
    print("\n" + "=" * 60)
    print("GENERATING FACE ENCODINGS")
    print("=" * 60)
    
    import pickle
    import numpy as np
    
    # Load existing encodings if they exist
    existing_encodings = []
    existing_names = []
    existing_paths = []
    
    if os.path.exists(encodings_file):
        try:
            print(f"Loading existing encodings from: {encodings_file}")
            with open(encodings_file, "rb") as f:
                data = pickle.load(f)
            existing_encodings = list(data.get("encodings", []))
            existing_names = list(data.get("names", []))
            existing_paths = list(data.get("image_paths", []))
            print(f"Loaded {len(existing_encodings)} existing encodings")
        except Exception as e:
            print(f"Warning: Could not load existing encodings: {e}")
    
    # Process new images
    new_encodings = []
    new_names = []
    new_paths = []
    failed_images = []
    
    image_files = sorted([f for f in os.listdir(person_dir) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    print(f"Processing {len(image_files)} images for {person_name}...")
    
    for idx, filename in enumerate(image_files, 1):
        image_path = os.path.join(person_dir, filename)
        
        # Skip if already processed
        if image_path in existing_paths:
            continue
        
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Generate encodings
            encodings = face_recognition.face_encodings(image)
            
            if not encodings:
                failed_images.append((filename, "No face detected"))
                print(f"  [{idx:3d}/{len(image_files)}] ⚠️  No face: {filename}")
                continue
            
            if len(encodings) > 1:
                print(f"  [{idx:3d}/{len(image_files)}] ⚠️  Multiple faces: {filename} (using first)")
            
            # Store encoding
            new_encodings.append(encodings[0])
            new_names.append(person_name)
            new_paths.append(image_path)
            
            if idx % 10 == 0:
                print(f"  [{idx:3d}/{len(image_files)}] ✓ Processed...")
        
        except Exception as e:
            failed_images.append((filename, str(e)))
            print(f"  [{idx:3d}/{len(image_files)}] ✗ Error: {filename} - {e}")
    
    # Combine with existing encodings
    all_encodings = existing_encodings + new_encodings
    all_names = existing_names + new_names
    all_paths = existing_paths + new_paths
    
    # Save updated encodings
    if new_encodings:
        print(f"\nSaving {len(all_encodings)} total encodings to: {encodings_file}")
        
        os.makedirs(os.path.dirname(encodings_file), exist_ok=True)
        
        data = {
            "encodings": all_encodings,
            "names": all_names,
            "image_paths": all_paths,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_images": len(all_encodings),
            "person_folders": sorted(list(set(all_names)))
        }
        
        with open(encodings_file, "wb") as f:
            pickle.dump(data, f)
        
        print("✓ Encodings saved successfully!")
    else:
        print("\n⚠️  No new encodings generated")
    
    # Summary
    print("\n" + "=" * 60)
    print("ENCODING SUMMARY")
    print("=" * 60)
    print(f"New images processed: {len(image_files)}")
    print(f"New encodings generated: {len(new_encodings)}")
    print(f"Failed images: {len(failed_images)}")
    print(f"Total encodings in database: {len(all_encodings)}")
    
    if failed_images:
        print(f"\nFailed images:")
        for fname, reason in failed_images:
            print(f"  - {fname}: {reason}")
    
    print("=" * 60)
    
    # Show breakdown by person
    if all_encodings:
        print("\nEncodings by person:")
        unique_names = set(all_names)
        for name in sorted(unique_names):
            count = sum(1 for n in all_names if n == name)
            print(f"  - {name}: {count} encodings")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Automatic face dataset collection and encoding generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect dataset for person named "John"
  python3 collect_dataset.py John
  
  # Collect with custom duration
  python3 collect_dataset.py John --duration 60
  
  # Collect without display (headless)
  python3 collect_dataset.py John --no-display
  
  # Custom output directory
  python3 collect_dataset.py John --output /custom/path
        """
    )
    
    parser.add_argument(
        "person_name",
        help="Name of the person for dataset collection"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=COLLECTION_DURATION_SECONDS,
        help=f"Collection duration in seconds (default: {COLLECTION_DURATION_SECONDS})"
    )
    
    parser.add_argument(
        "--interval",
        type=float,
        default=CAPTURE_INTERVAL_SECONDS,
        help=f"Capture interval in seconds (default: {CAPTURE_INTERVAL_SECONDS})"
    )
    
    parser.add_argument(
        "--output",
        default=KNOWN_FACES_DIR,
        help=f"Output directory for images (default: {KNOWN_FACES_DIR})"
    )
    
    parser.add_argument(
        "--encodings-file",
        default=ENCODINGS_FILE,
        help=f"Path to encodings file (default: {ENCODINGS_FILE})"
    )
    
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Run without displaying video (headless mode)"
    )
    
    parser.add_argument(
        "--no-encodings",
        action="store_true",
        help="Skip automatic encoding generation after collection"
    )
    
    args = parser.parse_args()
    
    # Validate person name
    if not args.person_name or args.person_name.strip() == "":
        print("ERROR: Person name cannot be empty")
        return 1
    
    person_name = args.person_name.strip()
    
    # Create collector
    collector = DatasetCollector(
        person_name=person_name,
        output_dir=args.output,
        duration=args.duration,
        interval=args.interval
    )
    
    # Run collection
    success = collector.collect(display=not args.no_display)
    
    if not success:
        print("\nERROR: No images were collected")
        return 1
    
    # Generate encodings
    if not args.no_encodings:
        person_dir = os.path.join(args.output, person_name)
        generate_encodings_for_person(person_name, person_dir, args.encodings_file)
    else:
        print("\n[SKIPPED] Encoding generation disabled")
        print("To generate encodings later, run: python3 generate_encodings.py")
    
    print("\n✓ Dataset collection complete!")
    print(f"\nNext steps:")
    print(f"  1. Review collected images in: {os.path.join(args.output, person_name)}")
    print(f"  2. Remove any bad images (blurry, wrong person, etc.)")
    print(f"  3. If you removed images, run: python3 generate_encodings.py")
    print(f"  4. Run your application: python3 run_all_integrated.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
