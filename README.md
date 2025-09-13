# Vendor Invoice Application

This is a Django-based web application for managing vendors, clients, and invoices. It features user authentication, role-based access control, and invoice generation with print preview and bulk download capabilities.

## Features

-   **User Management:** User registration, login, logout, and role-based access control (Admin, Accountant, Project Manager).
-   **Vendor Management:** Create, view, update, and delete vendor information.
-   **Client Settings:** Configure client company details and logo.
-   **Invoice Management:**
    -   Create, view, update, and delete invoices.
    -   Auto-generated and editable invoice numbers (INV/VEN/YEAR/XXXX).
    -   Dynamic addition/removal of invoice line items.
    -   Automatic calculation of sub-total, discount, tax, and total.
    -   Total amount in words.
-   **Invoice Printing:** Individual invoice print preview with print-friendly layout.
-   **Bulk Invoice Download:** Download selected invoices as HTML files in a ZIP archive.

## Technologies Used

-   Python 3.x
-   Django 5.x
-   MongoDB (via MongoEngine)
-   Bootstrap 5 (for frontend styling)
-   JavaScript (for dynamic formsets and calculations)

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd vendor_invoice_app_vsc
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

-   **Windows:**
    ```bash
    .venv\Scripts\activate
    ```
-   **macOS/Linux:**
    ```bash
    source .venv/bin/activate
    ```

### 4. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 5. Database Setup

This project uses MongoDB for `Vendor`, `Client`, and `Invoice` models, and SQLite for Django's authentication and `Profile` model.

-   **MongoDB:** Ensure you have a MongoDB instance running. The connection settings are typically configured in `vendor_invoice_project/settings.py`. You might need to adjust `MONGO_DATABASE_NAME` and `MONGO_HOST` if your setup is different.

-   **Django Migrations (for SQLite):**
    ```bash
    python manage.py migrate
    ```

### 6. Create a Superuser (Admin)

To access the Django admin panel and manage users/roles, create a superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin username, email, and password.

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be accessible at `http://127.0.0.1:8000/`.

## Usage

1.  **Access the Application:** Open your web browser and go to `http://127.0.0.1:8000/`.
2.  **Register/Login:** Create a new user account or log in with your superuser credentials.
3.  **Manage Vendors:** Navigate to the "Vendors" section to add, view, edit, or delete vendor information.
4.  **Manage Invoices:** Go to the "Invoices" section to create new invoices, view details, print, or download multiple invoices.
5.  **Client Settings:** (Admin only) Configure your company's details and logo in the "Settings" section.
6.  **User Management:** (Admin only) Manage user roles and permissions in the "User Management" section.

## Contributing

Feel free to fork the repository, make improvements, and submit pull requests.

## License

[Specify your license here, e.g., MIT License]
