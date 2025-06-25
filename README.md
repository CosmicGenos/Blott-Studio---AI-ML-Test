## Project Setup Instructions (Windows, Conda, Python 3.10, DeepInfra API)

This guide will help you set up and run the [Blott-Studio---AI-ML-Test](https://github.com/CosmicGenos/Blott-Studio---AI-ML-Test.git) project on your Windows machine using Conda, Python 3.10, and DeepInfra API for LLM access.

### **1. Clone the Repository**

```bash
git clone https://github.com/CosmicGenos/Blott-Studio---AI-ML-Test.git
cd Blott-Studio---AI-ML-Test
```

### **2. Create and Activate a Conda Environment**

Create a new Conda environment in the project directory with Python 3.10:

```bash
conda create -p ./testenv python=3.10 -y
conda activate ./testenv
```

### **3. Install Python Dependencies**

Install all required packages using `uv` and the requirements file:

```bash
uv pip install -r requirements.txt
```

### **4. Set Up PostgreSQL Database and User**

Ensure PostgreSQL is installed and running. Then:

- Open the SQL Shell (psql) or use pgAdmin.
- Enter the following commands to create the required user and database:

```sql
CREATE USER root WITH ENCRYPTED PASSWORD '1234';
CREATE DATABASE transaction_db;
GRANT ALL PRIVILEGES ON DATABASE transaction_db TO root;
```

### **5. Configure Environment Variables**

Create a `.env` file in your project root with the following content:

```
DATABASE_URL=postgresql://root:1234@localhost/transaction_db
DEEPINFRA_API_KEY=your_deepinfra_api_key_here
```

**Replace `your_deepinfra_api_key_here` with your actual DeepInfra API key.**  
This key is used to access affordable, open-source LLMs via DeepInfra.

To export the `DEEPINFRA_API_KEY` for your session (if needed):

```bash
set DEEPINFRA_API_KEY=your_deepinfra_api_key_here
```
*(On Windows Command Prompt. For PowerShell, use `$env:DEEPINFRA_API_KEY="your_deepinfra_api_key_here"`)*

### **6. Run the FastAPI Application**

From the project root, start the API server:

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### **7. API Endpoints Overview**

| Method | Endpoint                                                      | Description                                  |
|--------|---------------------------------------------------------------|----------------------------------------------|
| POST   | `/api/v1/analyze-risk`                                        | Webhook: Input transaction data              |
| GET    | `/api/v1/admin-notifications/notifications/high-risk`         | Get high risk notifications (admin)          |
| GET    | `/api/v1/admin-notifications/notifications/medium-risk`       | Get medium risk notifications (admin)        |
| GET    | `/api/v1/admin-notifications/notifications/normal`            | Get low risk notifications (admin)           |

- **Webhook endpoint** is for inputting transaction data.
- **Admin endpoints** return notifications filtered by risk level.

### **8. Usage Notes**

- API documentation is available at `/docs`.
- Ensure PostgreSQL is running and accessible with the specified credentials.
- The database user must be `root` with password `1234`.
- The `DEEPINFRA_API_KEY` must be set in your environment or `.env` file for LLM analysis.

### **9. Troubleshooting**

- If you encounter authentication errors, double-check your `.env` file and PostgreSQL user/password.
- If LLM analysis fails, ensure your DeepInfra API key is valid and exported to the environment.
- On Windows, manage PostgreSQL users with SQL Shell or pgAdmin.
- To deactivate your Conda environment, run:
  ```bash
  conda deactivate
  ```

This setup ensures your environment, dependencies, database, and external LLM integration are all configured for development and testing, with clear instructions for Windows and Conda.

