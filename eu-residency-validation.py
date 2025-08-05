#!/usr/bin/env python3
"""
EU Data Residency Validation Script for Vertex AI
Validates that all data and logs are properly configured for EU residency.
"""

import os
import json
from google.cloud import logging_v2
from google.cloud import bigquery
from google.cloud import storage
from google.cloud import resource_manager
import vertexai

def check_vertex_ai_region():
    """Check if Vertex AI is configured for EU region."""
    location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    
    eu_regions = [
        "europe-west1", "europe-west2", "europe-west3", "europe-west4", 
        "europe-west6", "europe-west8", "europe-west9", "europe-west10",
        "europe-central2", "europe-north1"
    ]
    
    if location in eu_regions:
        print(f"✅ Vertex AI region: {location} (EU compliant)")
        return True
    else:
        print(f"❌ Vertex AI region: {location} (NOT EU compliant)")
        return False

def check_project_location_policy():
    """Check if project has location restriction policies."""
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        client = resource_manager.Client()
        
        # This would require org-level permissions to check
        print("⚠️  Project location policy check requires organization admin access")
        print("   Manually verify organization policies restrict resources to EU")
        return None
    except Exception as e:
        print(f"⚠️  Could not check location policy: {e}")
        return None

def check_logging_configuration():
    """Check if logging is configured for EU storage."""
    try:
        client = logging_v2.Client()
        
        # List log sinks to check their destinations
        sinks = list(client.list_sinks())
        
        eu_sinks = []
        non_eu_sinks = []
        
        for sink in sinks:
            destination = sink.destination
            if "europe" in destination.lower() or "eu" in destination.lower():
                eu_sinks.append(sink.name)
            else:
                non_eu_sinks.append(sink.name)
        
        if eu_sinks:
            print(f"✅ Found EU logging sinks: {eu_sinks}")
        
        if non_eu_sinks:
            print(f"⚠️  Found non-EU logging sinks: {non_eu_sinks}")
            
        if not sinks:
            print("⚠️  No custom logging sinks found - logs may use default global storage")
            
    except Exception as e:
        print(f"⚠️  Could not check logging configuration: {e}")

def check_bigquery_datasets():
    """Check if BigQuery datasets are in EU."""
    try:
        client = bigquery.Client()
        datasets = list(client.list_datasets())
        
        eu_datasets = []
        non_eu_datasets = []
        
        for dataset in datasets:
            dataset_ref = client.get_dataset(dataset.dataset_id)
            location = dataset_ref.location
            
            if location == "EU" or location.startswith("europe"):
                eu_datasets.append(f"{dataset.dataset_id} ({location})")
            else:
                non_eu_datasets.append(f"{dataset.dataset_id} ({location})")
        
        if eu_datasets:
            print(f"✅ EU BigQuery datasets: {eu_datasets}")
        
        if non_eu_datasets:
            print(f"❌ Non-EU BigQuery datasets: {non_eu_datasets}")
            
    except Exception as e:
        print(f"⚠️  Could not check BigQuery datasets: {e}")

def check_storage_buckets():
    """Check if Cloud Storage buckets are in EU."""
    try:
        client = storage.Client()
        buckets = list(client.list_buckets())
        
        eu_buckets = []
        non_eu_buckets = []
        
        for bucket in buckets:
            location = bucket.location
            
            if location == "EU" or location.startswith("EUROPE"):
                eu_buckets.append(f"{bucket.name} ({location})")
            else:
                non_eu_buckets.append(f"{bucket.name} ({location})")
        
        if eu_buckets:
            print(f"✅ EU Storage buckets: {eu_buckets}")
        
        if non_eu_buckets:
            print(f"❌ Non-EU Storage buckets: {non_eu_buckets}")
            
    except Exception as e:
        print(f"⚠️  Could not check storage buckets: {e}")

def validate_vertex_ai_connection():
    """Test Vertex AI connection and confirm EU endpoint."""
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("VERTEX_AI_LOCATION")
        
        vertexai.init(project=project_id, location=location)
        
        # The endpoint URL should contain the region
        print(f"✅ Vertex AI initialized successfully in {location}")
        print(f"   Endpoint: https://{location}-aiplatform.googleapis.com")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Vertex AI: {e}")
        return False

def generate_compliance_report():
    """Generate a comprehensive compliance report."""
    print("=" * 60)
    print("EU DATA RESIDENCY VALIDATION REPORT")
    print("=" * 60)
    print()
    
    print("1. VERTEX AI CONFIGURATION")
    print("-" * 30)
    vertex_compliant = check_vertex_ai_region()
    vertex_connected = validate_vertex_ai_connection()
    print()
    
    print("2. LOGGING CONFIGURATION")
    print("-" * 30)
    check_logging_configuration()
    print()
    
    print("3. BIGQUERY DATASETS")
    print("-" * 30)
    check_bigquery_datasets()
    print()
    
    print("4. STORAGE BUCKETS")
    print("-" * 30)
    check_storage_buckets()
    print()
    
    print("5. PROJECT POLICIES")
    print("-" * 30)
    check_project_location_policy()
    print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if vertex_compliant and vertex_connected:
        print("✅ Vertex AI: EU compliant")
    else:
        print("❌ Vertex AI: NOT EU compliant")
    
    print()
    print("RECOMMENDATIONS:")
    print("- Ensure all logging sinks point to EU destinations")
    print("- Create BigQuery datasets with location=EU")
    print("- Use Cloud Storage buckets with location=EU or EUROPE-*")
    print("- Set up organization policies to restrict to EU regions")
    print("- Enable VPC Service Controls for additional protection")

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    generate_compliance_report()