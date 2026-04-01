# app/utils/image_upload.py

import os
from uuid import uuid4
from typing import List
import uuid
from fastapi import UploadFile


def process_and_save_image(file, folder):
    # ✅ CREATE FOLDER IF NOT EXISTS
    os.makedirs(folder, exist_ok=True)

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(folder, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path


def upload_images(files: List[UploadFile], folder: str) -> List[str]:
    if not files:
        return []

    image_paths = []

    for file in files:
        path = process_and_save_image(file, folder)
        if path:
            image_paths.append(path)

    return image_paths