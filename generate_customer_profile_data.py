import random
import psycopg2

def generate_random_customer_data(num_customers):
    """Generate random customer data."""
    customers = []
    for _ in range(num_customers):
        age = random.randint(18, 70)  # Age between 18 and 70
        income = round(random.uniform(2000, 25000), 0)  # Income between 3,000 and 20,000
        spending_category_percentage = random.randint(20, 80)  # Spending 20% to 80% of income
        savings_goal = round(random.uniform(5000, 100000), 0)  # Savings goal between 5,000 and 50,000
        risk_tolerance = random.randint(1, 5)  # Risk tolerance on a scale of 1 to 5
        #types = random.choice(['Saver','Spender','Investor'])
        customers.append((age, income, spending_category_percentage, savings_goal, risk_tolerance))
    return customers

def batch_insert_customers(data, batch_size=100):
    """Insert customer records into a PostgreSQL table in batches."""
    # Database connection parameters - replace with your actual details
    conn_params = "dbname='xxxx' user='xxxxx' host='xxxxxxxx' password='xxxxxxxx'"
    conn = psycopg2.connect(conn_params)
    cursor = conn.cursor()

    # Prepare the SQL insert statement
    insert_query = "INSERT INTO customer_profiles_fin (age, income, spending, target_savings_goal, risk_tolerance) VALUES (%s, %s, %s, %s, %s)"

    # Insert data in batches
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        cursor.executemany(insert_query, batch)
        print(f"Inserted... {i}")
        conn.commit()

    print(f"Inserted {len(data)} records into the database.")

    # Clean up
    cursor.close()
    conn.close()

# Generate random customer data
num_customers = 100000  # Specify the number of random customer profiles to generate
customers = generate_random_customer_data(num_customers)

# Batch insert into the database
batch_insert_customers(customers, batch_size=50)

