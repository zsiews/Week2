import json
import requests
import random
from urllib.parse import urlparse

# Configuration variables
display_products_in_console = True  # Set to False to not display products
num_cart_links = 100  # Number of cart links to generate
num_of_random_products = 5  # Number of free random products to add to cart
quantity_per_variant = 1  # Quantity for each variant in the cart link


# Base URL of the products.json file (User Input)
base_url = input("Give Link:\n")

if base_url.endswith("/"):
    base_url = base_url[:-1]
    product_url = f"{base_url}/products.json"
    final_url = f"{base_url}"
else:
    base_parsed = urlparse(base_url)
    parsed = "".join([base_parsed.scheme, "://", base_parsed.netloc, base_parsed.path])
    if parsed.endswith("/"):
        parsed = parsed[:-1]
        product_url = f"{parsed}/products.json"
        final_url = f"{parsed}"


# Fetch JSON data with pagination
def fetch_all_products(product_url, limit=250):
    all_products = {"products": []}
    page = 1
    while True:
        # Construct URL with pagination query parameters
        url = f"{product_url}?limit={limit}&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: HTTP {response.status_code}")

        data = response.json()
        if not data["products"]:
            # Break the loop if no products are returned
            break

        all_products["products"].extend(data["products"])
        page += 1
    return all_products


# Find variants with a price of 0.00
def find_free_variants(products_data):
    free_variants = []
    for product in products_data["products"]:
        for variant in product["variants"]:
            if variant["price"] == "0.00" and variant["available"] == True:
                free_variants.append(
                    {
                        "product_id": product["id"],
                        "variant_id": variant["id"],
                        "title": product["title"],
                        "variant_title": variant["title"],
                        "avaliable": variant["available"],
                    }
                )
    return free_variants


# Function to generate cart links for free random variants
def generate_cart_links(all_products, num_links, num_products, quantity):
    cart_links = []
    free_variants = [
        variant
        for product in all_products["products"]
        for variant in product["variants"]
        if variant["price"] == "0.00"
    ]

    for _ in range(num_links):
        if len(free_variants) < num_products:
            print("Not enough free products to fulfill the request.")
            break
        selected_variants = random.sample(free_variants, k=num_products)
        link = f"{final_url}/cart/" + ",".join(
            [f"{variant['id']}:{quantity}" for variant in selected_variants]
        )
        cart_links.append(link)

    return cart_links


# Main function
def main():
    try:
        products_data = fetch_all_products(product_url)

        if display_products_in_console == True:
            free_variants = find_free_variants(products_data)
            for variant in free_variants:
                print(
                    f"Product ID: {variant['product_id']}, Variant ID: {variant['variant_id']}, Product Title: {variant['title']}, Variant Title: {variant['variant_title']}, Avaliable: {variant['avaliable']}"
                )

        if num_cart_links > 0:
            cart_links = generate_cart_links(
                products_data,
                num_cart_links,
                num_of_random_products,
                quantity_per_variant,
            )
            print("\nGenerated Cart Links:")
            for link in cart_links:
                print(link)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
