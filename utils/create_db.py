import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "welvision_db"
}

CREATE_TABLES = {
    "app_settings": """
        CREATE TABLE IF NOT EXISTS app_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            setting_key VARCHAR(100) UNIQUE,
            setting_value LONGTEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            updated_by VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "bf_models": """
        CREATE TABLE IF NOT EXISTS bf_models (
            id INT AUTO_INCREMENT PRIMARY KEY,
            model_name VARCHAR(255) NOT NULL,
            model_path VARCHAR(1000) NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "bf_roller_tracking": """
        CREATE TABLE IF NOT EXISTS bf_roller_tracking (
            roller_type VARCHAR(100),
            employee_id VARCHAR(100),
            report_date DATE,
            start_time TIME,
            end_time TIME,
            total_inspected INT DEFAULT 0,
            total_accepted INT DEFAULT 0,
            total_rejected INT DEFAULT 0,
            total_rust INT DEFAULT 0,
            total_dent INT DEFAULT 0,
            total_damage INT DEFAULT 0,
            total_high_head INT DEFAULT 0,
            total_low_head INT DEFAULT 0,
            others INT DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "bf_threshold_history": """
        CREATE TABLE IF NOT EXISTS bf_threshold_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(255) NOT NULL,
            change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            defect_threshold LONGTEXT NOT NULL,
            size_threshold LONGTEXT NOT NULL,
            model_threshold DECIMAL(10,4) NOT NULL,
            model_name VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "global_roller_limits": """
        CREATE TABLE IF NOT EXISTS global_roller_limits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            min_length DECIMAL(10,3) NOT NULL,
            max_length DECIMAL(10,3) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            updated_by VARCHAR(100),
            min_outer_diameter FLOAT DEFAULT 0,
            max_outer_diameter FLOAT DEFAULT 0,
            min_dimple_diameter FLOAT DEFAULT 0,
            max_dimple_diameter FLOAT DEFAULT 0,
            min_small_diameter FLOAT DEFAULT 0,
            max_small_diameter FLOAT DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "od_models": """
        CREATE TABLE IF NOT EXISTS od_models (
            id INT AUTO_INCREMENT PRIMARY KEY,
            model_name VARCHAR(255) NOT NULL,
            model_path VARCHAR(1000) NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "od_roller_tracking": """
        CREATE TABLE IF NOT EXISTS od_roller_tracking (
            roller_type VARCHAR(100),
            employee_id VARCHAR(100),
            report_date DATE,
            start_time TIME,
            end_time TIME,
            total_inspected INT DEFAULT 0,
            total_accepted INT DEFAULT 0,
            total_rejected INT DEFAULT 0,
            total_rust INT DEFAULT 0,
            total_dent INT DEFAULT 0,
            total_damage INT DEFAULT 0,
            total_damage_on_end INT DEFAULT 0,
            total_spherical INT DEFAULT 0,
            others INT DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "od_threshold_history": """
        CREATE TABLE IF NOT EXISTS od_threshold_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(255) NOT NULL,
            change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            defect_threshold LONGTEXT NOT NULL,
            size_threshold LONGTEXT NOT NULL,
            model_threshold DECIMAL(10,4) NOT NULL,
            model_name VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "roller_data": """
        CREATE TABLE IF NOT EXISTS roller_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            roller_type VARCHAR(100) NOT NULL,
            outer_diameter DECIMAL(10,3) NOT NULL,
            dimple_diameter DECIMAL(10,3) NOT NULL,
            small_diameter DECIMAL(10,3) NOT NULL,
            length_mm DECIMAL(10,3) NOT NULL,
            high_head_pixels INT DEFAULT 0,
            down_head_pixels INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            created_by VARCHAR(100) DEFAULT 'system'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            salt VARCHAR(100) NOT NULL,
            role ENUM('Admin','Super Admin','Operator') NOT NULL,
            is_active TINYINT(1) DEFAULT 1,
            failed_attempts INT DEFAULT 0,
            locked_until DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
}


def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f"Connected to database: {DB_CONFIG['database']}")
        print("=" * 60)

        for name, query in CREATE_TABLES.items():
            print(f"Creating table: {name} ...", end=" ")
            cursor.execute(query)
            print("✅")

        conn.commit()
        cursor.close()
        conn.close()
        print("\n🎯 All tables created successfully!")

    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")

if __name__ == "__main__":
    main()
