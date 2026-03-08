"""
DynamoDB Data Seeding Script
Loads synthetic_data.json into Amazon DynamoDB

Usage:
    python seed_dynamodb.py
    
Prerequisites:
    1. Set AWS credentials in .env file or environment variables
    2. Install dependencies: pip install -r requirements.txt
"""

import boto3
import json
import os
import sys
from pathlib import Path
from decimal import Decimal
from typing import Any, cast
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
TABLE_NAME = os.getenv('DYNAMODB_LAND_RECORDS_TABLE', 'landledger-land-records')


def convert_floats_to_decimals(obj):
    """
    Convert all float values to Decimal for DynamoDB compatibility.
    DynamoDB doesn't support float type directly.
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimals(v) for v in obj]
    return obj


def create_table(dynamodb_client: Any, dynamodb_resource: Any) -> bool:
    """Create the DynamoDB table if it doesn't exist"""
    try:
        # Check if table exists
        dynamodb_client.describe_table(TableName=TABLE_NAME)
        print(f"Table '{TABLE_NAME}' already exists.")
        return True
    except dynamodb_client.exceptions.ResourceNotFoundException:
        print(f"Creating table '{TABLE_NAME}'...")
        
        # Create table with land_id as partition key
        dynamodb_resource.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'land_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'land_id', 'AttributeType': 'N'},
                {'AttributeName': 'location', 'AttributeType': 'S'},
                {'AttributeName': 'survey_number', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'location-index',
                    'KeySchema': [
                        {'AttributeName': 'location', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'survey-number-index',
                    'KeySchema': [
                        {'AttributeName': 'survey_number', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        waiter = dynamodb_client.get_waiter('table_exists')
        print("Waiting for table creation...")
        waiter.wait(TableName=TABLE_NAME)
        print(f"Table '{TABLE_NAME}' created successfully!")
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False


def load_data():
    """Load synthetic data from JSON file"""
    data_path = Path(__file__).parent / 'data' / 'synthetic_data.json'
    
    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        sys.exit(1)
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} records from synthetic_data.json")
    return data


def seed_data(table, records):
    """Insert records into DynamoDB using batch write"""
    print(f"\nSeeding {len(records)} records into DynamoDB...")
    
    success_count = 0
    error_count = 0
    
    # DynamoDB batch_write_item supports up to 25 items per batch
    batch_size = 25
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        try:
            with table.batch_writer() as writer:
                for record in batch:
                    # Convert floats to Decimal
                    item = convert_floats_to_decimals(record)
                    writer.put_item(Item=item)
                    success_count += 1
        except Exception as e:
            print(f"Error in batch {i // batch_size + 1}: {e}")
            error_count += len(batch)
        
        # Progress indicator
        progress = min(i + batch_size, len(records))
        print(f"Progress: {progress}/{len(records)} records processed", end='\r')
    
    print(f"\n\nSeeding complete!")
    print(f"  - Success: {success_count}")
    print(f"  - Errors: {error_count}")


def main():
    print("=" * 60)
    print("LandLedger DynamoDB Data Seeding Script")
    print("=" * 60)
    
    # Validate credentials
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        print("\nError: AWS credentials not found!")
        print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")
        print("\nExample .env file:")
        print("  AWS_ACCESS_KEY_ID=your_access_key_here")
        print("  AWS_SECRET_ACCESS_KEY=your_secret_key_here")
        sys.exit(1)
    
    print(f"\nConfiguration:")
    print(f"  - Region: {AWS_REGION}")
    print(f"  - Table: {TABLE_NAME}")
    print(f"  - Access Key: {AWS_ACCESS_KEY_ID[:8]}...")
    
    # Initialize DynamoDB
    print("\nConnecting to AWS DynamoDB...")
    
    dynamodb_resource: Any = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    dynamodb_client: Any = boto3.client(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    # Create table
    if not create_table(dynamodb_client, dynamodb_resource):
        sys.exit(1)
    
    # Load data
    records = load_data()
    
    # Seed data
    table = dynamodb_resource.Table(TABLE_NAME)
    seed_data(table, records)
    
    print("\n" + "=" * 60)
    print("Data seeding completed successfully!")
    print(f"Your data is now available in DynamoDB table: {TABLE_NAME}")
    print("=" * 60)


if __name__ == '__main__':
    main()
