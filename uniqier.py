location = "Norway"
file_path = f"email_addresses({location}).txt"
# Remove duplicates
with open(file_path, "r") as file:
    unique_emails = set(file.read().splitlines())

with open(file_path, "w") as file:
    for email in unique_emails:
        file.write(f"{email}\n")

print(f"Emails saved to {file_path}")