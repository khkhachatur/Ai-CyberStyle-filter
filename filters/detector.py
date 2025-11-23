from ultralytics import YOLO
import numpy as np

# Face model
MODEL_FACE_PATH = "models/yolov8n-face.pt"
model_face = YOLO(MODEL_FACE_PATH)

# Body model (COCO detector)
MODEL_BODY_PATH = "models/yolo11n.pt"
model_body = YOLO(MODEL_BODY_PATH)


# MODEL_FACE_PATH = "models/yolo11n-face.pt"
# model_face = YOLO(MODEL_FACE_PATH)   

def detect_face(image_pil):
    img_np = np.array(image_pil)
    results = model_face(img_np, verbose=False)

    if not results or len(results[0].boxes) == 0:
        return None  # no face detected

    # pick largest face
    faces = []
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = box.tolist()
        area = (x2-x1) * (y2-y1)
        faces.append((area, (x1,y1,x2,y2)))

    _, face_box = max(faces, key=lambda x: x[0])
    return face_box
