import json
import shutil
from pathlib import Path

SOURCE = Path.home() / "Downloads" / "archive (3)"
DEST = Path.home() / "DisasterResponseSystem" / "dataset"

SPLITS = {
    "train": "train",
    "valid": "val",
    "test": "test",
}

# Map COCO category names to our two YOLO classes.
# YOLO class 0 = person; class 1 = dog.
CLASS_MAP = {
    "person": 0,
    "dog": 1,
}

def main():
    total_images = 0
    total_boxes = 0

    for source_split, target_split in SPLITS.items():
        image_dir = SOURCE / source_split
        annotation_file = image_dir / "_annotations.coco.json"

        if not annotation_file.exists():
            raise FileNotFoundError(
                f"Missing annotation file: {annotation_file}"
            )

        with annotation_file.open(encoding="utf-8") as f:
            coco = json.load(f)

        categories = {
            category["id"]: category["name"].strip().lower()
            for category in coco["categories"]
        }

        images = {
            image["id"]: image
            for image in coco["images"]
        }

        annotations_by_image = {}
        for annotation in coco["annotations"]:
            annotations_by_image.setdefault(
                annotation["image_id"], []
            ).append(annotation)

        output_images = DEST / "images" / target_split
        output_labels = DEST / "labels" / target_split
        output_images.mkdir(parents=True, exist_ok=True)
        output_labels.mkdir(parents=True, exist_ok=True)

        split_images = 0
        split_boxes = 0

        for image_id, image_info in images.items():
            filename = image_info["file_name"]
            source_image = image_dir / filename

            if not source_image.exists():
                print(f"WARNING: Missing image: {source_image}")
                continue

            # Copy each image, keeping its original filename.
            shutil.copy2(
                source_image,
                output_images / source_image.name
            )

            width = image_info["width"]
            height = image_info["height"]

            if width <= 0 or height <= 0:
                raise ValueError(
                    f"Invalid dimensions for {filename}: "
                    f"{width} x {height}"
                )

            lines = []

            for annotation in annotations_by_image.get(image_id, []):
                category_name = categories.get(
                    annotation["category_id"], ""
                )

                if category_name not in CLASS_MAP:
                    continue

                bbox = annotation.get("bbox")
                if not bbox or len(bbox) != 4:
                    continue

                x, y, box_width, box_height = map(float, bbox)

                if box_width <= 0 or box_height <= 0:
                    continue

                # COCO [x, y, width, height] to YOLO
                center_x = (x + box_width / 2) / width
                center_y = (y + box_height / 2) / height
                normalized_width = box_width / width
                normalized_height = box_height / height

                # Clip boxes to the image boundaries.
                left = max(0.0, x)
                top = max(0.0, y)
                right = min(float(width), x + box_width)
                bottom = min(float(height), y + box_height)

                if right <= left or bottom <= top:
                    continue

                center_x = ((left + right) / 2) / width
                center_y = ((top + bottom) / 2) / height
                normalized_width = (right - left) / width
                normalized_height = (bottom - top) / height

                class_id = CLASS_MAP[category_name]

                lines.append(
                    f"{class_id} "
                    f"{center_x:.6f} {center_y:.6f} "
                    f"{normalized_width:.6f} "
                    f"{normalized_height:.6f}"
                )

            label_file = output_labels / (
                source_image.stem + ".txt"
            )

            label_file.write_text(
                "\n".join(lines) + ("\n" if lines else ""),
                encoding="utf-8"
            )

            split_images += 1
            split_boxes += len(lines)

        total_images += split_images
        total_boxes += split_boxes

        print(
            f"{source_split} -> {target_split}: "
            f"{split_images} images, {split_boxes} person/dog boxes"
        )

    yaml_text = """path: /Users/REPLACE_ME/DisasterResponseSystem/dataset
train: images/train
val: images/val
test: images/test

names:
  0: person
  1: dog
"""

    # Use the actual home directory instead of a fixed username.
    yaml_text = yaml_text.replace(
        "/Users/REPLACE_ME",
        str(Path.home())
    )

    (DEST / "data.yaml").write_text(
        yaml_text, encoding="utf-8"
    )

    print("\nDataset preparation finished.")
    print(f"Images copied: {total_images}")
    print(f"Person/dog bounding boxes: {total_boxes}")
    print(f"Dataset location: {DEST}")
    print(f"Configuration: {DEST / 'data.yaml'}")

if __name__ == "__main__":
    main()
