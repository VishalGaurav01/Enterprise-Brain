import os
import random

# pyrefly: ignore [missing-import]
from faker import Faker
from sqlalchemy import create_engine, MetaData, insert, text
from sqlalchemy.sql import sqltypes

fake = Faker()

def generate_mock_data(column):
    name = column.name.lower()
    
    # Check if it's an enum
    if hasattr(column.type, 'enums'):
        return random.choice(column.type.enums)
        
    # Check if it's a Postgres UUID type
    type_str = str(column.type).lower()
    if 'uuid' in type_str:
        return fake.uuid4()
        
    if isinstance(column.type, sqltypes.String) or 'varchar' in type_str:
        if 'email' in name:
            return f"{random.randint(1000,99999)}_{fake.unique.email()}"
        elif 'name' in name:
            return f"{fake.name()} {random.randint(100,999)}"
        elif 'uuid' in name or 'id' in name:
            return fake.uuid4()
        elif 'phone' in name:
            return fake.phone_number()[:20]
        elif 'password' in name or 'hash' in name:
            return fake.sha256()
        elif 'role' in name:
            return random.choice(['Admin', 'User', 'Manager'])
        elif 'status' in name:
            return random.choice(['Active', 'Inactive', 'Pending'])
        else:
            length = getattr(column.type, 'length', 20)
            length = length if length else 20
            base = fake.word()
            return f"{base}_{random.randint(100,999)}"[:length]
            
    elif isinstance(column.type, sqltypes.Integer):
        return random.randint(1, 100)
    elif isinstance(column.type, sqltypes.Float) or isinstance(column.type, sqltypes.Numeric):
        return round(random.uniform(10.0, 1000.0), 2)
    elif isinstance(column.type, sqltypes.Boolean):
        return random.choice([True, False])
    elif isinstance(column.type, sqltypes.Date):
        return fake.date_between(start_date='-2y', end_date='today')
    elif isinstance(column.type, sqltypes.DateTime):
        return fake.date_time_between(start_date='-2y', end_date='now')
    return fake.word()

def seed_database(db_url, rows_per_table=50):
    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    primary_keys = {}

    print("Cleaning up database before seeding...")
    with engine.begin() as conn:
        for table in reversed(metadata.sorted_tables):
            try:
                conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
            except Exception:
                pass
                
    for table in metadata.sorted_tables:
        if table.name == "alembic_version":
            continue
        print(f"Seeding table {table.name}...")
        
        # Ensure we know the primary key
        pk_col = list(table.primary_key.columns)[0] if table.primary_key.columns else None
        
        rows_to_insert = []
        try:
            for _ in range(rows_per_table):
                row_data = {}
                for column in table.columns:
                    # Don't manually seed autoincrement primary keys or default timestamps
                    if (column.primary_key and column.autoincrement) or (column.server_default is not None):
                        continue
                        
                    if column.foreign_keys:
                        fk = list(column.foreign_keys)[0]
                        ref_table = fk.column.table.name
                        if ref_table in primary_keys and primary_keys[ref_table]:
                            row_data[column.name] = random.choice(primary_keys[ref_table])
                        else:
                            # Fallback if the referenced table is empty
                            if not column.nullable:
                                raise Exception(f"ref table {ref_table} has no data.")
                            row_data[column.name] = None
                    else:
                        if column.nullable and random.random() < 0.1:
                            row_data[column.name] = None
                        else:
                            row_data[column.name] = generate_mock_data(column)
                            
                rows_to_insert.append(row_data)
        except Exception as e:
            print(f"Skipping {table.name} due to generation error: {e}")
            continue
            
        if rows_to_insert:
            with engine.begin() as conn:
                try:
                    stmt = insert(table).values(rows_to_insert)
                    if pk_col is not None:
                        stmt = stmt.returning(pk_col)
                    
                    result = conn.execute(stmt)
                    
                    if pk_col is not None:
                        pks = [row[0] for row in result]
                        primary_keys[table.name] = pks
                        
                    print(f"Successfully seeded {len(rows_to_insert)} rows into {table.name}")
                except Exception as e:
                    print(f"Error seeding {table.name}: {e}")

if __name__ == '__main__':
    print("Starting database seeder...")
    db_url = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@db:5432/brain")
    seed_database(db_url, rows_per_table=50)
    print("Seeding complete.")
