import argparse
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# File to store company details and last invoice number
CONFIG_FILE = "config.json"

def load_config():
    """
    Load stored configuration from JSON file.
    
    Returns:
        dict: Configuration data if file exists, else an empty dictionary.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

def save_config(config):
    """
    Save configuration to JSON file.
    
    Args:
        config (dict): Configuration data to be saved.
    """
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

class InvoiceGenerator:
    def __init__(self, company_name, company_address, invoice_prefix):
        """
        Initialize InvoiceGenerator with company details and invoice prefix.
        
        Args:
            company_name (str): Name of the company.
            company_address (str): Address of the company.
            invoice_prefix (str): Prefix for invoice numbers.
        """
        self.company_name = company_name
        self.company_address = company_address
        self.invoice_prefix = invoice_prefix
        self.config = load_config()
        
        # Use stored values if not explicitly provided
        self.company_name = self.company_name or self.config.get("company_name", "Default Company")
        self.company_address = self.company_address or self.config.get("company_address", "Default Address")
        self.invoice_prefix = self.invoice_prefix or self.config.get("invoice_prefix", "INV")
        
        # Ensure invoice number is maintained
        self.last_invoice_number = self.config.get("last_invoice_number", 0)

    def get_next_invoice_number(self):
        """
        Generate the next invoice number.
        
        Returns:
            str: Next invoice number in the sequence.
        """
        self.last_invoice_number += 1
        save_config({
            "company_name": self.company_name,
            "company_address": self.company_address,
            "invoice_prefix": self.invoice_prefix,
            "last_invoice_number": self.last_invoice_number
        })
        return f"{self.invoice_prefix}{self.last_invoice_number:04d}"

    def generate_invoice(self):
        """
        Generate an invoice by accepting user input and creating a PDF.
        """
        invoice_number = input("Enter Invoice Number (Press Enter to auto-generate): ") or self.get_next_invoice_number()
        customer_name = input("Enter Customer Name: ")
        customer_address = input("Enter Customer Address: ")
        invoice_date = input("Enter Invoice Date (YYYY-MM-DD) [Press Enter for today]: ") or datetime.now().strftime("%Y-%m-%d")
        
        # Collect item details
        items = []
        while True:
            desc = input("Enter Item Description (or type 'done' to finish): ")
            if desc.lower() == "done":
                break
            qty = int(input("Enter Quantity: "))
            price = float(input("Enter Price per Unit: "))
            items.append({"desc": desc, "qty": qty, "price": price})

        # Display invoice details for confirmation
        print("\nInvoice Summary:")
        print(f"Invoice Number: {invoice_number}")
        print(f"Customer: {customer_name}, {customer_address}")
        print(f"Date: {invoice_date}")
        print("Items:")
        total = 0
        for item in items:
            line_total = item["qty"] * item["price"]
            total += line_total
            print(f" - {item['desc']}: {item['qty']} x {item['price']} = {line_total}")
        print(f"Total Amount: {total}")

        confirm = input("Confirm and generate invoice? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.create_pdf(invoice_number, customer_name, customer_address, invoice_date, items, total)
            print(f"Invoice {invoice_number} generated successfully!")
        else:
            print("Invoice creation cancelled.")

    def create_pdf(self, invoice_number, customer_name, customer_address, invoice_date, items, total):
        """
        Create an invoice as a PDF file.
        
        Args:
            invoice_number (str): Invoice number.
            customer_name (str): Name of the customer.
            customer_address (str): Address of the customer.
            invoice_date (str): Invoice date.
            items (list): List of items in the invoice.
            total (float): Total amount of the invoice.
        """
        pdf_filename = f"Invoice_{invoice_number}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        
        # Add company and customer details
        c.drawString(100, 800, f"{self.company_name}")
        c.drawString(100, 785, f"{self.company_address}")
        c.drawString(100, 760, f"Invoice Number: {invoice_number}")
        c.drawString(100, 745, f"Date: {invoice_date}")
        c.drawString(100, 730, f"Customer: {customer_name}")
        c.drawString(100, 715, f"Address: {customer_address}")
        
        # Add items
        y_position = 690
        for item in items:
            c.drawString(100, y_position, f"{item['desc']}: {item['qty']} x {item['price']} = {item['qty'] * item['price']}")
            y_position -= 15
        
        # Add total amount
        c.drawString(100, y_position - 20, f"Total Amount: {total}")
        
        # Save PDF
        c.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Command-line Invoice Generator")
    parser.add_argument("--company_name", type=str, help="Company Name")
    parser.add_argument("--company_address", type=str, help="Company Address")
    parser.add_argument("--invoice_prefix", type=str, help="Prefix for Invoice Number")
    args = parser.parse_args()
    
    invoice_gen = InvoiceGenerator(args.company_name, args.company_address, args.invoice_prefix)
    
    while True:
        invoice_gen.generate_invoice()
        choice = input("Do you want to generate another invoice? (yes/no): ").strip().lower()
        if choice != "yes":
            print("Exiting Invoice Generator. Goodbye!")
            break
