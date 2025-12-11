import csv

# a) Read the CSV
with open("products.csv", "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

# b) Print each row in clean format
print("Product List")
for r in rows:
    print(f"ID: {r['product_id']}, Name: {r['product_name']}, "f"Category: {r['category']}, Price: {r['price']}, Qty: {r['quantity']}")

# c) Total number of rows
print("\nTotal rows:", len(rows))

# d) Total products priced above 500
above_500 = sum(1 for r in rows if float(r["price"]) > 500)
print("Products priced above 500:", above_500)

# e) Average price of all products
avg_price = sum(float(r["price"]) for r in rows) / len(rows)
print("Average price:", avg_price)

# f) List products from a specific category
user_cat = input("\nEnter category to filter: ")

print(f"\nProducts in category '{user_cat}':")
for r in rows:
    if r["category"].lower() == user_cat.lower():
        print(r["product_name"])

# g) Total quantity of all items in stock
total_qty = sum(int(r["quantity"]) for r in rows)
print("\nTotal quantity in stock:", total_qty)
