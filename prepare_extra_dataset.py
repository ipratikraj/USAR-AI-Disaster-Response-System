from pathlib import Path
import json
import shutil

source_root = Path.home() / "Downloads" / "archive (3)"
output_root = Path("datasets/thermal_extra")

# Match the class IDs of the existing model.
class_mapping = {
    "person": 0,
    "dog": 2,
}

splits = ["train", "valid", "test"]
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

for split in splits:
    source_split = source_root / split
    annotation_file = source_split / "_annotations.coco.json"

    if not annotation_file.exists():
        raise FileNotFoundError(f"Missing annotation file: {annotation_file}")

    data = json.loads(annotation_file.read_text())
    categories = {
        category["id"]: category["name"]
        for category in data.get("categories", [])
    }

    images_by_id = {
        image["id"]: image
        for image in data.get("images", [])
    }

    image_output = output_root / "images" / split
    label_output = output_root / "labels" / split

    image_output.mkdir(parents=True, exist_ok=True)
    label_output.mkdir(parents=True, exist_ok=True)

    # Group usable annotations by image.
    annotations_by_image = {}

    for annotation in data.get("annotations", []):
        category_name = categories.get(annotation.get("category_id"))

        # Ignore unused categories and anything outside our mapping.
        if category_name not in class_mapping:
            continue

        annotations_by_image.setdefault(
            annotation["image_id"], []
        ).append(annotation)

    copied_images = 0
    written_labels = 0
    skipped_annotations = 0

    for image_id, image_info in images_by_id.items():
        filename = Path(image_info["file_name"])
        source_image = source_split / filename

        if not source_image.is_file():
            print(f"WARNING: Missing image: {source_image}")
            continue

        if source_image.suffix.lower() not in image_extensions:
            print(f"WARNING: Unsupported image: {source_image}")
            continue

        # Unique names prevent collisions between source filenames.
        output_name = f"{split}_{filename.stem}"
        destination_image = image_output / f"{output_name}{source_image.suffix.lower()}"
        destination_label = label_output / f"{output_name}.txt"

        shutil.copy2(source_image, destination_image)
        copied_images += 1

        width = float(image_info["width"])
        height = float(image_info["height"])

        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid image dimensions: {source_image}")

        lines = []

        for annotation in annotations_by_image.get(image_id, []):
            x, y, box_width, box_height = annotation["bbox"]

            # COCO boxes use [x_min, y_min, width, height].
            # YOLO uses normalized center_x, center_y, width, height.
            if box_width <= 0 or box_height <= 0:
                skipped_annotations += 1
                continue

            if x < 0 or y < 0 or x + box_width > width + 1 or y + box_height > height + 1:
                print(f"WARNING: Out-of-bounds box in {source_image.name}")

            center_x = (x + box_width / 2) / width
            center_y = (y + box_height / 2) / height
            normalized_width = box_width / width
            normalized_height = box_height / height

            values = [
                center_x, center_y,
                normalized_width, normalized_height
            ]

            if not all(0 <= value <= 1 for value in values):
                skipped_annotations += 1
                continue

            class_id = class_mapping[
                categories[annotation["category_id"]]
            ]

            lines.append(
                f"{class_id} "
                + " ".join(f"{value:.6f}" for value in values)
            )

        destination_label.write_text(
            "\n".join(lines) + ("\n" if lines else "")
        )
        written_labels += len(lines)

    print(f"\n{split.upper()}:")
    print(f"  Images copied: {copied_images}")
    print(f"  Bounding boxes written: {written_labels}")
    print(f"  Invalid annotations skipped: {skipped_annotations}")

# Create a dataset configuration using the existing class mapping.
yaml_text = """path: datasets/thermal_extra
train: images/train
val: images/valid
test: images/test
names:
  0: person
  1: car
  2: dog
"""

(output_root / "data.yaml").write_text(yaml_text)

print("\nPrepared dataset at:", output_root.resolve())
print("Configuration:", (output_root / "data.yaml").resolve())
print("\nOriginal images and current model were not modified.")
