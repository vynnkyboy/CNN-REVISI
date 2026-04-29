import os
import sys
from pathlib import Path
import re

def get_all_images(folder_path):
    """Get all image files in folder with supported extensions"""
    extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.JPG', '.JPEG', '.PNG', '.BMP', '.TIFF')
    image_files = []
    
    for ext in extensions:
        image_files.extend(Path(folder_path).glob(f'*{ext}'))
    
    return sorted(image_files)  # Sort for consistent ordering

def rename_images_clean(folder_path, prefix):
    """
    Clean rename all images in folder starting from 1
    This will ignore already renamed files
    """
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return 0
    
    # Get all images
    all_images = get_all_images(folder_path)
    
    if not all_images:
        print(f"⚠️  No images found in: {folder_path}")
        return 0
    
    print(f"\n📁 Processing: {folder_path}")
    print(f"   Found {len(all_images)} images total")
    
    # Filter out already renamed files (optional)
    pattern = re.compile(rf'{prefix}_\d+\.')
    new_images = []
    old_images = []
    
    for img in all_images:
        if pattern.search(str(img.name)):
            print(f"   ⏭️  Skipping already renamed: {img.name}")
            continue
        old_images.append(img)
    
    if not old_images:
        print(f"   ℹ️  All images already renamed in this folder!")
        return 0
    
    print(f"   Will rename {len(old_images)} images")
    
    renamed_count = 0
    counter = 1
    
    # Get existing numbers to avoid conflict
    existing_numbers = set()
    for img in all_images:
        if pattern.search(str(img.name)):
            try:
                num = int(img.name.split('_')[-1].split('.')[0])
                existing_numbers.add(num)
            except:
                pass
    
    # Find next available number
    counter = 1
    while counter in existing_numbers:
        counter += 1
    
    for old_path in old_images:
        extension = old_path.suffix
        new_filename = f"{prefix}_{counter:04d}{extension}"
        new_path = old_path.parent / new_filename
        
        # Double check if target exists
        while new_path.exists():
            counter += 1
            new_filename = f"{prefix}_{counter:04d}{extension}"
            new_path = old_path.parent / new_filename
        
        try:
            old_path.rename(new_path)
            print(f"   ✅ Renamed: {old_path.name:30} -> {new_filename}")
            renamed_count += 1
            counter += 1
        except Exception as e:
            print(f"   ❌ Error renaming {old_path.name}: {e}")
    
    return renamed_count

def main():
    print("=" * 70)
    print("🌿 WASTE DATASET IMAGE RENAME TOOL (FIXED VERSION) 🌿")
    print("=" * 70)
    
    # Dataset base path
    base_dir = "../dataset"
    
    if not os.path.exists(base_dir):
        print(f"\n❌ Dataset folder not found: {base_dir}")
        custom_path = input("\nEnter correct dataset path: ").strip()
        if custom_path:
            base_dir = custom_path
        else:
            print("Operation cancelled.")
            sys.exit(1)
    
    # Define folder mappings
    folders = [
        (f"{base_dir}/train/o", "organic_train"),
        (f"{base_dir}/train/r", "inorganic_train"),
        (f"{base_dir}/valid/o", "organic_valid"),
        (f"{base_dir}/valid/r", "inorganic_valid"),
        (f"{base_dir}/test/o", "organic_test"),
        (f"{base_dir}/test/r", "inorganic_test"),
    ]
    
    print("\n📋 Folders to process:")
    print("-" * 50)
    for folder, prefix in folders:
        if os.path.exists(folder):
            img_count = len(get_all_images(folder))
            print(f"  ✓ {folder}")
            print(f"    → {prefix}_####.jpg ({img_count} images)")
        else:
            print(f"  ✗ {folder} (not found)")
    
    print("\n" + "=" * 70)
    confirm = input("\nStart renaming? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Operation cancelled.")
        sys.exit(0)
    
    total_renamed = 0
    
    for folder_path, prefix in folders:
        if os.path.exists(folder_path):
            count = rename_images_clean(folder_path, prefix)
            total_renamed += count
    
    print("\n" + "=" * 70)
    print(f"✅ RENAMING COMPLETED!")
    print(f"   Total images renamed: {total_renamed}")
    print("=" * 70)
    
    # Show final summary
    print("\n📊 FINAL SUMMARY:")
    print("-" * 50)
    for folder, prefix in folders:
        if os.path.exists(folder):
            img_count = len(get_all_images(folder))
            print(f"  {folder}: {img_count} images")

if __name__ == "__main__":
    main()