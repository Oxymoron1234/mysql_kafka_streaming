### Steps to Execute the Workflow

This document provides step-by-step instructions to set up and execute the workflow involving MySQL, Docker, Kafka, and Python scripts.

---

### **Prerequisites**

1. Docker and Docker Compose installed on your system.
2. MySQL Workbench or any MySQL DBA tool installed.
3. Python 3.7 or higher installed with necessary libraries.
4. Access to a Confluent Kafka cluster (local or remote).
5. Required Python dependencies:
   - `confluent-kafka`
   - `fastavro`
   - `mysql-connector-python`
   - (Ensure these are installed via `pip install -r requirements.txt`.)

---

### **Steps**

#### **Step 1: Start the MySQL Server Using Docker**

1. Navigate to the directory containing the `docker-compose.yml` file.
2. Run the following command to start the MySQL server in detached mode:
   ```bash
   docker-compose up -d
   ```
3. Verify the MySQL server is running:
   ```bash
   docker ps
   ```

   Ensure the container for MySQL is listed and healthy.

---

#### **Step 2: Populate the Database**

1. Open the `data/product.sql` file in a text editor.
2. Copy the SQL script from `product.sql`.
3. Open MySQL Workbench or your preferred DBA tool and connect it to the MySQL instance running in Docker:
   - Host: `localhost`
   - Port: `3306`
   - Username: As configured in `docker-compose.yml` (e.g., `root`).
   - Password: As configured in `docker-compose.yml`.
4. Paste the SQL script into the query editor of your DBA tool and execute it to populate the database.

---

#### **Step 3: Configure `config.py`**

1. Download the `schema_api_key` file and `bootstrap_api` file, and place them in the same directory as the Python scripts.
2. Open `config.py` in a text editor.
3. Edit the following configuration variables in `config.py`:
   - **Database connection settings:**

     ```python
     MYSQL_HOST = 'localhost'
     MYSQL_USER = '<your_mysql_user>'
     MYSQL_PASSWORD = '<your_mysql_password>'
     MYSQL_DB = '<your_database_name>'
     ```
   - **Confluent Kafka settings:**

     ```python
     bootstrap_file_path = '<your_bootstrap_server>'
     schema_file_path = '<your_schema_api_key>'
     ```

     examples:
     ```python
     schema_file_path = 'api-key-B5OCH6TADT2Z5G5W.txt'
     bootstrap_file_path = "api-key-7IAK4M6LTPU3LXG7.txt"
     ```
   - Follow the comments in `config.py` for additional configurations.

---

#### **Step 4: Run `send_data_to_db.py`**

1. Open a terminal and navigate to the directory containing the Python scripts.
2. Execute the script to send data to the MySQL database:
   ```bash
   python send_data_to_db.py
   ```

   - This script connects to the database and populates it with necessary data.

---

#### **Step 5: Run `confluent_avro_data_producer.py`**

1. Execute the producer script to fetch data from the database, apply transformations, and send it to the Kafka topic:
   ```bash
   python confluent_avro_data_producer.py
   ```
2. Verify the script is:
   - Fetching data from MySQL.
   - Transforming the data.
   - Sending data to the Kafka topic (`products_update`).

---

#### **Step 6: Run `confluent_avro_data_consumer.py`**

1. Execute the consumer script to pull data from the Kafka topic:
   ```bash
   python confluent_avro_data_consumer.py
   ```
2. This script will:
   - Create 5 different Kafka consumers.
   - Pull data from the `products_update` topic.
   - Automatically create and append data into respective JSON files. If the files do not exist, they will be created.

---

### **Expected Output**

1. The MySQL database will be populated with data from the `product.sql` file.
2. Data transformations will be applied, and the results will be sent to the `products_update` Kafka topic.
3. JSON files will be created/appended with data pulled by the consumers from the Kafka topic.

---

### **Additional Notes**

- To monitor the Kafka topic and consumers, you can use tools like the Kafka CLI or the Confluent Control Center.
- Ensure your Kafka cluster is running, and the `products_update` topic is correctly configured before starting the producer.
- If you encounter errors:
  - Check the logs for MySQL, Kafka, or Python scripts.
  - Verify all configurations in `config.py`.
