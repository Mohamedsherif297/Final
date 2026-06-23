#!/usr/bin/env python3
"""
Generate Face Encodings
Processes all images in known_faces directory and saves encodings to encodings.pkl
Run this script whenever you add/remove/update face images in the dataset
"""
import os
import pickle
import time
from pathlib import Path

try:
    import face_recognition
    FACE_RECOG_AVAILABLE = True
except ImportError:
    FACE_RECOG_AVAILABLE = False
    print("ERROR: face_recognition library not installed")
    print("Install with: pip install face_recognition")
    exit(1)

# Configuration
KNOWN_FACES_DIR = "pi_minimal/known_faces/images"
OUTPUT_FILE = "pi_minimal/known_faces/encodings.pkl"
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


def generate_encodings(faces_dir: str, output_file: str):
    """
    Generate encodings for all face images in the directory
    
    Args:
        faces_dir: Directory containing person subdirectories with images
        output_file: Path to save the encodings pickle file
    
    Returns:
        Number of encodings generated
    """
    if not os.path.isdir(faces_dir):
        print(f"ERROR: Directory not found: {faces_dir}")
        return 0
    
    encodings = []
    names = []
    image_paths = []
    failed_images = []
    
    print(f"Scanning directory: {faces_dir}")
    print("-" * 60)
    
    # Scan all person directories
    person_folders = sorted([d for d in os.listdir(faces_dir) 
                            if os.path.isdir(os.path.join(faces_dir, d))])
    
    if not person_folders:
        print("ERROR: No person folders found in the directory")
        return 0
    
    print(f"Found {len(person_folders)} person folder(s): {', '.join(person_folders)}")
    print("-" * 60)
    
    total_images = 0
    start_time = time.time()
    
    # Process each person's images
    for person_name in person_folders:
        person_dir = os.path.join(faces_dir, person_name)
        print(f"\nProcessing: {person_name}")
        
        # Get all image files
        image_files = [f for f in os.listdir(person_dir) 
                      if f.lower().endswith(SUPPORTED_EXTENSIONS)]
        
        if not image_files:
            print(f"  ⚠️  No images found for {person_name}")
            continue
        
        print(f"  Found {len(image_files)} image(s)")
        
        # Process each image
        for idx, filename in enumerate(image_files, 1):
            image_path = os.path.join(person_dir, filename)
            
            try:
                # Load image
                image = face_recognition.load_image_file(image_path)
                
                # Generate encodings
                face_encodings = face_recognition.face_encodings(image)
                
                if not face_encodings:
                    print(f"  ⚠️  No face detected in: {filename}")
                    failed_images.append((person_name, filename, "No face detected"))
                    continue
                
                if len(face_encodings) > 1:
                    print(f"  ⚠️  Multiple faces detected in: {filename} (using first one)")
                
                # Store the first encoding
                encodings.append(face_encodings[0])
                names.append(person_name)
                image_paths.append(image_path)
                total_images += 1
                
                # Progress indicator
                if idx % 5 == 0:
                    print(f"  ✓ Processed {idx}/{len(image_files)} images...")
            
            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
                failed_images.append((person_name, filename, str(e)))
        
        print(f"  ✓ Completed {person_name}: {len([n for n in names if n == person_name])} encodings")
    
    # Summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"ENCODING COMPLETE")
    print("=" * 60)
    print(f"Total images processed: {total_images}")
    print(f"Total encodings generated: {len(encodings)}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    
    if failed_images:
        print(f"\n⚠️  Failed images: {len(failed_images)}")
        for person, filename, reason in failed_images:
            print(f"  - {person}/{filename}: {reason}")
    
    # Save encodings to pickle file
    if encodings:
        print(f"\nSaving encodings to: {output_file}")
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save data
        data = {
            "encodings": encodings,
            "names": names,
            "image_paths": image_paths,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_images": total_images,
            "person_folders": person_folders
        }
        
        with open(output_file, "wb") as f:
            pickle.dump(data, f)
        
        print(f"✓ Encodings saved successfully!")
        
        # Show breakdown by person
        print("\nBreakdown by person:")
        for person in person_folders:
            count = sum(1 for n in names if n == person)
            print(f"  - {person}: {count} encodings")
    else:
        print("\n✗ No encodings generated. Nothing to save.")
    
    print("=" * 60)
    return len(encodings)


def verify_encodings(encodings_file: str):
    """
    Verify and display information about saved encodings
    
    Args:
        encodings_file: Path to the encodings pickle file
    """
    if not os.path.exists(encodings_file):
        print(f"ERROR: Encodings file not found: {encodings_file}")
        return
    
    try:
        with open(encodings_file, "rb") as f:
            data = pickle.load(f)
        
        print("\n" + "=" * 60)
        print("ENCODINGS FILE INFO")
        print("=" * 60)
        print(f"File: {encodings_file}")
        print(f"Generated at: {data.get('generated_at', 'Unknown')}")
        print(f"Total encodings: {len(data['encodings'])}")
        print(f"Total people: {len(set(data['names']))}")
        
        print("\nPeople in dataset:")
        for person in sorted(set(data['names'])):
            count = sum(1 for n in data['names'] if n == person)
            print(f"  - {person}: {count} encodings")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR reading encodings file: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate face encodings from known faces dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate encodings with default paths
  python generate_encodings.py
  
  # Generate encodings with custom paths
  python generate_encodings.py --faces-dir /path/to/faces --output /path/to/encodings.pkl
  
  # Verify existing encodings file
  python generate_encodings.py --verify
        """
    )
    
    parser.add_argument(
        "--faces-dir",
        default=KNOWN_FACES_DIR,
        help=f"Directory containing known faces (default: {KNOWN_FACES_DIR})"
    )
    
    parser.add_argument(
        "--output",
        default=OUTPUT_FILE,
        help=f"Output file for encodings (default: {OUTPUT_FILE})"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing encodings file without regenerating"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("FACE ENCODINGS GENERATOR")
    print("=" * 60)
    
    if args.verify:
        verify_encodings(args.output)
    else:
        # Generate new encodings
        count = generate_encodings(args.faces_dir, args.output)
        
        if count > 0:
            print(f"\n✓ SUCCESS: Generated {count} face encodings")
            print(f"\nTo use these encodings, ensure your application loads from:")
            print(f"  {args.output}")
        else:
            print("\n✗ FAILED: No encodings were generated")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
