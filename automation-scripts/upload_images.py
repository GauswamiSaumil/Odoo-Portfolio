import os
from xmlrpc import client
import base64


# Odoo credentials
url = "/"
db = ""
username = "xmlrpcuser@admin.com"
password = "xmlrpcuser"

# Folders and paths
base_folder_path = "path"

# XML-RPC setup
common = client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
if not uid:
    print("Authentication failed. Please check credentials.")
    exit()

models = client.ServerProxy(f"{url}/xmlrpc/2/object")

def fetch_product_mapping():
    """
    Fetch all products and create a mapping of references to IDs.
    """
    product_records = models.execute_kw(
        db, uid, password, 'product.template', 'search_read',
        [[('default_code', '!=', False)]],
        {'fields': ['id', 'default_code']}
    )
    return {record['default_code']: record['id'] for record in product_records}

def upload_images(base_folder_path, product_map):
    """
    Upload images for products based on the mapping of references to IDs.
    """
    for item in os.listdir(base_folder_path):
        item_path = os.path.join(base_folder_path, item)
        
        # Case 1: If it's a folder
        if os.path.isdir(item_path):
            product_reference = item  # The folder name is the product reference
            image_files = [f for f in os.listdir(item_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            if image_files:
                image_path = os.path.join(item_path, image_files[0])  # Take the first image
            else:
                print(f"No image found in folder: {product_reference}")
                continue

        # Case 2: If it's a file
        elif os.path.isfile(item_path) and item.lower().endswith(('png', 'jpg', 'jpeg')):
            product_reference = os.path.splitext(item)[0]  # The file name (without extension) is the product reference
            image_path = item_path

        else:
            # Skip non-image files and directories without images
            continue

        # Match the product reference with the mapping
        product_id = product_map.get(product_reference)
        if product_id:
            try:
                # Read the image
                with open(image_path, "rb") as img_file:
                    base64_image = base64.b64encode(img_file.read()).decode('utf-8')

                # Upload the image
                models.execute_kw(
                    db, uid, password, 'product.template', 'write',
                    [[product_id], {'image_1920': base64_image}]
                )
                print(f"Uploaded image for product: {product_reference}")
            except Exception as e:
                print(f"Error uploading image for product {product_reference}: {e}")
        else:
            print(f"No product found for reference: {product_reference}")

# Fetch the product mapping
product_map = fetch_product_mapping()

# Run the script
upload_images(base_folder_path, product_map)
