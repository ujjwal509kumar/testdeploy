# main.py (FastAPI Backend)
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from health_rules import health_warnings
import json
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("food-scanner-api")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load product data
product_list = []
logger.info("Loading product data from product.json")
try:
    with open("product.json", "r", encoding="utf-8") as f:
        count = 0
        for line in f:
            try:
                product = json.loads(line)
                product_list.append(product)
                count += 1
            except Exception as e:
                logger.error(f"Error parsing product JSON: {e}")
                continue
        logger.info(f"Successfully loaded {count} products")
except Exception as e:
    logger.error(f"Failed to load product.json: {e}")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"status": "API is running", "products_loaded": len(product_list)}

@app.get("/product/{barcode}")
def get_product(barcode: str, request: Request):
    client_host = request.client.host
    logger.info(f"Product lookup request for barcode {barcode} from {client_host}")
    
    for product in product_list:
        if product.get("code") == barcode:
            logger.info(f"Product found for barcode {barcode}")
            return product
    
    logger.warning(f"Product not found for barcode {barcode}")
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/analyze")
async def analyze(request: Request):
    client_host = request.client.host
    logger.info(f"Analyze request received from {client_host}")
    
    try:
        body = await request.json()
        product = body.get("product")
        profile = body.get("profile")

        if not product or not profile:
            logger.warning("Missing product or profile in analyze request")
            raise HTTPException(status_code=400, detail="Missing product or profile")

        logger.info(f"Analyzing product {product.get('code', 'unknown')} for profile {profile.get('id', 'unknown')}")
        warnings = health_warnings(product, profile)
        logger.info(f"Analysis complete with {len(warnings)} warnings")

        return {
            "product_name": product.get("product_name", ""),
            "barcode": product.get("code", ""),
            "keywords": product.get("_keywords", []),
            "brand": product.get("brands", ""),
            "quantity": product.get("quantity", ""),
            "ingredients": product.get("ingredients_text", ""),
            "nutrition_grade": product.get("nutrition_grades_tags", []),
            "labels": product.get("labels_tags", []),
            "categories": product.get("categories", []),
            "manufacturing_places": product.get("manufacturing_places", ""),
            "packaging": product.get("packaging", ""),
            "image_url": product.get("image_url", ""),
            "nutriments": product.get("nutriments", {}),
            "additives": product.get("additives_tags", []),
            "allergens": product.get("allergens_tags", []),
            "food_processing": product.get("nova_group", ""),
            "environment_impact": product.get("environment_impact_level_tags", []),
            "warnings": warnings
        }
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# Updated for Render deployment
if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting FastAPI server on 0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)