def health_warnings(product, profile):
    warnings = []
    ingredients = product.get("ingredients_text", "").lower()
    additives = product.get("additives_tags", [])
    allergens = product.get("allergens_tags", [])
    nutriments = product.get("nutriments", {})

    # Allergies
    for allergen in profile.get("allergies", []):
        if allergen.lower() in ingredients or allergen.lower() in str(allergens):
            warnings.append(f"⚠️ Allergy risk: {allergen}")

    # Diabetes
    if "diabetes" in profile.get("diseases", []):
        sugar = nutriments.get("sugars_100g", 0)
        try:
            sugar_val = float(sugar)
            if sugar_val > 5:
                warnings.append(f"⚠️ High sugar ({sugar_val}g/100g) – risky for diabetes")
        except ValueError:
            pass

    # Additive warnings
    additive_risks = {
        "en:e621": "MSG – may cause headaches",
        "en:e211": "Sodium Benzoate – asthma trigger",
        "en:e951": "Aspartame – not recommended for PKU",
        "en:e102": "Tartrazine – may affect behavior in children"
    }
    for a in additives:
        if a in additive_risks:
            warnings.append(f"⚠️ {additive_risks[a]}")

    return warnings
