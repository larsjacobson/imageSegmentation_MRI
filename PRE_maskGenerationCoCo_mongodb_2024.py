from pymongo import MongoClient import requests import matplotlib.pyplot as plt import matplotlib.patches as patches import os import pydicom from pydicom.filebase import DicomBytesIO import numpy as np from PIL import Image  # MongoDB connection details client = MongoClient('mongodb+srv://larsjacobson:4Mf%239x8E@eojgroup.6ifxr.mongodb.net/?retryWrites=true&w=majority') db = client.prostateSegmentation_MRI collection = db.input  # Directory to save masks mask_dir = '/Users/lars.jacobson/PycharmProjects/imageSegmentation_MRI/train/masks/direct' os.makedirs(mask_dir, exist_ok=True)  sas_token = "?sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2024-01-15T02:00:51Z&st=2024-01-14T18:00:51Z&spr=https&sig=UOwMc5E3aOrM1o1sZLOqzSK5MksMauFOqbyYXDCjf5Y%3D"  # Replace with your SAS token  import numpy as np  def dicom_to_pil(dicom_data):     image_array = dicom_data.pixel_array     print(f"Processing DICOM image with shape: {image_array.shape} and data type: {image_array.dtype}")      if image_array.ndim == 2:         # Normalize the 16-bit image data to 0-255         normalized_image = (image_array - image_array.min()) / (image_array.max() - image_array.min())         image_array_8bit = (normalized_image * 255).astype('uint8')         return np.array(Image.fromarray(image_array_8bit))     else:         print(f"Unsupported image shape: {image_array.shape}")         return None  def get_authenticated_url(base_url):     return base_url + sas_token  # Function to draw annotations (modified to use authenticated URL) from urllib.parse import urlparse, unquote  # ... (Other parts of your script)  def draw_annotations(image_url, annotations, patient_id):     print(f"Processing image: {image_url}")     authenticated_url = get_authenticated_url(image_url)     response = requests.get(authenticated_url)      if response.status_code == 200:         try:             dicom_data = pydicom.dcmread(DicomBytesIO(response.content), force=True)             img_array = dicom_to_pil(dicom_data)             if img_array is None:  # Skip processing if conversion was unsuccessful                 print(f"Skipping image: Unsupported format or failed conversion for URL {image_url}")                 return         except Exception as e:             print(f"Error processing DICOM file: {e}")             return  # Skip this image          # Convert the PIL Image to a NumPy array for Matplotlib         img = np.array(img_array)          # Create a figure and axes         fig, ax = plt.subplots()         plt.imshow(img, cmap='gray')          img_height, img_width = img.shape[:2]  # Get image dimensions          for ann in annotations:             # Scale bbox coordinates to image size             x, y, width, height = ann['bbox']             x_scaled = x * img_width             y_scaled = y * img_height             width_scaled = width * img_width             height_scaled = height * img_height              rect = patches.Rectangle((x_scaled, y_scaled), width_scaled, height_scaled, linewidth=2, edgecolor='r',                                      facecolor='none')             ax.add_patch(rect)          # Save the mask with patient_id as prefix         mask_filename = f"{patient_id}_{os.path.basename(image_url).split('.')[0]}_mask.png"         mask_path = os.path.join(mask_dir, mask_filename).replace("\\", "/")         plt.savefig(mask_path, dpi=300)         plt.close()         print(f"Saved mask to {mask_path}")     else:         print(f"Failed to fetch the image: HTTP {response.status_code}")   # Process each COCO file in the collection for coco_file in collection.find():     patient_id = coco_file['_patient']  # Extract the _patient field from the document     for image in coco_file['images']:         image_url = image['absolute_url']         image_annotations = [ann for ann in coco_file['annotations'] if ann['image_id'] == image['id']]         draw_annotations(image_url, image_annotations, patient_id)  # Pass the patient_id here
