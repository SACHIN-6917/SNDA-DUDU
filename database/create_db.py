import pymysql

# Database connection parameters
db_config = {
    'user': 'root',
    'password': 'sachin6917',
    'host': 'localhost',
    'port': 3306,
}

try:
    # Connect to MySQL Server
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    
    # Create Database
    cursor.execute("CREATE DATABASE IF NOT EXISTS industrial_visit CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("✅ Database 'industrial_visit' created successfully!")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Error: {e}")
