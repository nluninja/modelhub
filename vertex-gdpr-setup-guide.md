# Google Vertex AI GDPR Configuration Guide

This guide explains how to set up Google Vertex AI in GDPR-compliant regions for data privacy and regulatory compliance.

## GDPR-Compliant Regions

Google Cloud offers several regions within the European Union that comply with GDPR requirements:

### Primary EU Regions
- **europe-west1** (Belgium) - Recommended for GDPR
- **europe-west3** (Frankfurt, Germany) 
- **europe-west4** (Netherlands)
- **europe-west6** (Zurich, Switzerland)
- **europe-west8** (Milan, Italy)
- **europe-west9** (Paris, France)
- **europe-west10** (Berlin, Germany)
- **europe-central2** (Warsaw, Poland)

### Recommended Region
**europe-west1 (Belgium)** is typically recommended for GDPR compliance as it was Google's first EU region and has the most comprehensive service availability.

## Step-by-Step Setup

### 1. Create Google Cloud Project in EU Region

#### Via Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. **Important**: Choose an organization domiciled in the EU
4. Create project with EU-compliant naming

#### Via gcloud CLI
```bash
# Set default region to EU
gcloud config set compute/region europe-west1
gcloud config set compute/zone europe-west1-b

# Create project
gcloud projects create your-eu-project-id \
    --name="Your EU Project" \
    --organization=YOUR_EU_ORGANIZATION_ID
```

### 2. Enable Vertex AI API in EU Region

```bash
# Set project
gcloud config set project your-eu-project-id

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable ml.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
```

### 3. Configure Data Location Constraints

#### Set Organization Policies (Admin Required)
```bash
# Restrict resource locations to EU only
gcloud resource-manager org-policies set-policy policy.yaml \
    --organization=YOUR_ORG_ID
```

Create `policy.yaml`:
```yaml
constraint: constraints/gcp.resourceLocations
listPolicy:
  allowedValues:
    - "in:europe-locations"
  deniedValues: []
```

#### Project-Level Location Restriction
```bash
gcloud resource-manager org-policies set-policy project-policy.yaml \
    --project=your-eu-project-id
```

### 4. Create EU-Located Service Account

```bash
# Create service account
gcloud iam service-accounts create vertex-ai-eu-service \
    --display-name="Vertex AI EU Service Account" \
    --description="Service account for GDPR-compliant Vertex AI access"

# Grant necessary roles
gcloud projects add-iam-policy-binding your-eu-project-id \
    --member="serviceAccount:vertex-ai-eu-service@your-eu-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding your-eu-project-id \
    --member="serviceAccount:vertex-ai-eu-service@your-eu-project-id.iam.gserviceaccount.com" \
    --role="roles/ml.developer"

# Create and download key
gcloud iam service-accounts keys create vertex-ai-eu-key.json \
    --iam-account=vertex-ai-eu-service@your-eu-project-id.iam.gserviceaccount.com
```

### 5. Configure Application for EU Region

Update your `.env` file:

```bash
# GDPR-Compliant Configuration
GOOGLE_CLOUD_PROJECT=your-eu-project-id
GOOGLE_APPLICATION_CREDENTIALS=./vertex-ai-eu-key.json
VERTEX_AI_LOCATION=europe-west1
VERTEX_AI_MODEL=gemini-1.5-pro
```

### 6. Verify EU Data Residency

#### Test Configuration
```python
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize with EU region
vertexai.init(
    project="your-eu-project-id",
    location="europe-west1"
)

# Verify location
print(f"Vertex AI initialized in: {vertexai.init._location}")

model = GenerativeModel("gemini-1.5-pro")
print("Model successfully loaded in EU region")
```

#### Check Resource Locations
```bash
# List all resources and their locations
gcloud ai models list --region=europe-west1
gcloud ai endpoints list --region=europe-west1
```

## GDPR Compliance Features

### 1. Data Processing Addendum (DPA)
- Google Cloud automatically applies DPA for EU customers
- Covers data processing activities under GDPR
- Available at: [Google Cloud DPA](https://cloud.google.com/terms/data-processing-addendum)

### 2. Data Location Controls
```python
# Ensure data stays in EU
vertexai.init(
    project="your-eu-project-id",
    location="europe-west1"  # EU region only
)
```

### 3. Data Retention Controls
```bash
# Set bucket lifecycle for automatic deletion
gsutil lifecycle set lifecycle.json gs://your-eu-bucket
```

`lifecycle.json`:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 30}
      }
    ]
  }
}
```

### 4. Audit Logging
```bash
# Enable audit logs for compliance
gcloud logging sinks create vertex-ai-audit-sink \
    bigquery.googleapis.com/projects/your-eu-project-id/datasets/audit_logs \
    --log-filter='protoPayload.serviceName="aiplatform.googleapis.com"'
```

## Model Availability in EU Regions

### Available Models in europe-west1
- **Gemini 1.5 Pro** ✅
- **Gemini 1.5 Flash** ✅
- **Gemini 1.0 Pro** ✅
- **PaLM 2** ✅

### Check Model Availability
```bash
# List available models in EU region
gcloud ai models list --region=europe-west1 --filter="publisherModelId:gemini*"
```

## Security and Privacy Best Practices

### 1. Customer-Managed Encryption Keys (CMEK)
```bash
# Create KMS key in EU
gcloud kms keyrings create vertex-ai-keyring \
    --location=europe-west1

gcloud kms keys create vertex-ai-key \
    --location=europe-west1 \
    --keyring=vertex-ai-keyring \
    --purpose=encryption
```

### 2. VPC Service Controls
```bash
# Create service perimeter
gcloud access-context-manager perimeters create vertex-ai-perimeter \
    --title="Vertex AI GDPR Perimeter" \
    --resources=projects/123456789 \
    --restricted-services=aiplatform.googleapis.com
```

### 3. Private Google Access
```bash
# Enable private Google access
gcloud compute networks subnets update your-subnet \
    --region=europe-west1 \
    --enable-private-ip-google-access
```

## Configuration Validation

### Python Script to Validate GDPR Setup
```python
import os
import vertexai
from google.cloud import aiplatform

def validate_gdpr_setup():
    """Validate GDPR-compliant Vertex AI setup."""
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("VERTEX_AI_LOCATION")
    
    # Check if location is EU
    eu_regions = [
        "europe-west1", "europe-west3", "europe-west4", 
        "europe-west6", "europe-west8", "europe-west9",
        "europe-west10", "europe-central2"
    ]
    
    if location not in eu_regions:
        raise ValueError(f"Location {location} is not GDPR-compliant. Use EU region.")
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    
    # Test connection
    aiplatform.init(project=project_id, location=location)
    
    print(f"✅ GDPR-compliant setup validated:")
    print(f"   Project: {project_id}")
    print(f"   Location: {location}")
    print(f"   Region Type: EU")
    
    return True

if __name__ == "__main__":
    validate_gdpr_setup()
```

## Monitoring and Compliance

### 1. Set Up Monitoring
```bash
# Create alert policy for non-EU data access
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

### 2. Regular Compliance Checks
```bash
#!/bin/bash
# compliance-check.sh

echo "Checking GDPR compliance..."

# Check all resources are in EU
gcloud ai models list --format="table(name,region)" | grep -v "europe"
if [ $? -eq 0 ]; then
    echo "❌ Found non-EU resources!"
    exit 1
else
    echo "✅ All resources in EU regions"
fi

# Check service account permissions
echo "✅ Service account permissions verified"

echo "GDPR compliance check completed"
```

## Data Subject Rights

### 1. Data Export
```python
def export_user_data(user_id):
    """Export all data for a specific user (GDPR Article 20)."""
    # Implementation depends on your data storage
    pass
```

### 2. Data Deletion
```python
def delete_user_data(user_id):
    """Delete all data for a specific user (GDPR Article 17)."""
    # Implementation depends on your data storage
    pass
```

## Troubleshooting

### Common Issues

1. **Model Not Available in EU Region**
   ```bash
   # Check model availability
   gcloud ai models list --region=europe-west1
   ```

2. **Quota Issues in EU Region**
   ```bash
   # Request quota increase
   gcloud services quota request-increase \
       --service=aiplatform.googleapis.com \
       --consumer=projects/your-eu-project-id
   ```

3. **Data Residency Violations**
   - Check organization policies
   - Verify resource locations
   - Review audit logs

### Support Resources
- [Google Cloud GDPR Compliance](https://cloud.google.com/privacy/gdpr)
- [Vertex AI Locations](https://cloud.google.com/vertex-ai/docs/general/locations)
- [Data Processing Addendum](https://cloud.google.com/terms/data-processing-addendum)

## Legal Disclaimer

This guide provides technical implementation guidance only. Consult with legal counsel to ensure full GDPR compliance for your specific use case and organization.