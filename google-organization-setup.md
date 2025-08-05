# Google Cloud Organization Setup Guide

This guide explains how to create a Google Cloud Organization, which is essential for proper GDPR compliance and centralized resource management.

## Why You Need a Google Cloud Organization

- **GDPR Compliance**: Required for organization-level policies that restrict data to EU regions
- **Centralized Control**: Manage permissions, billing, and policies across all projects
- **Resource Location Policies**: Enforce EU-only resource creation
- **Audit and Compliance**: Better logging and monitoring capabilities
- **Identity Management**: Centralized user and service account management

## Prerequisites

- Business domain (recommended) or personal domain
- Administrative access to domain DNS settings
- EU-based business information (for GDPR compliance)

## Option 1: Google Workspace Organization (Recommended for Businesses)

### Step 1: Set up Google Workspace

1. **Sign up for Google Workspace**
   - Go to [Google Workspace](https://workspace.google.com)
   - Click "Get started"
   - Choose your plan (Business Starter is sufficient)

2. **Domain Setup**
   - Use your business domain (e.g., `yourcompany.eu`)
   - **For GDPR**: Use EU domain extensions (.eu, .de, .fr, etc.) when possible
   - Enter EU-based business information

3. **Verify Domain Ownership**
   - Add the provided TXT record to your domain's DNS
   - Wait for verification (can take up to 24 hours)

4. **Complete Workspace Setup**
   - Create admin account
   - Set up users (optional)
   - Configure basic settings

### Step 2: Access Google Cloud Console

1. **Sign in to Google Cloud**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Sign in with your Workspace admin account
   - Accept Google Cloud terms

2. **Verify Organization Creation**
   ```bash
   # Install gcloud CLI if not already installed
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Authenticate
   gcloud auth login
   
   # List organizations
   gcloud organizations list
   ```

   You should see output like:
   ```
   DISPLAY_NAME        ID            DIRECTORY_CUSTOMER_ID
   yourcompany.eu      123456789012  C01abc2de
   ```

### Step 3: Configure Organization for GDPR

1. **Set Organization-Level Policies**
   ```bash
   # Get organization ID
   ORG_ID=$(gcloud organizations list --format="value(name)")
   
   # Create EU-only policy
   cat > eu-only-policy.yaml << EOF
   constraint: constraints/gcp.resourceLocations
   listPolicy:
     allowedValues:
       - "in:europe-locations"
     deniedValues: []
   EOF
   
   # Apply policy
   gcloud resource-manager org-policies set-policy eu-only-policy.yaml \
     --organization=$ORG_ID
   ```

2. **Verify Policy Application**
   ```bash
   gcloud resource-manager org-policies describe constraints/gcp.resourceLocations \
     --organization=$ORG_ID
   ```

## Option 2: Cloud Identity Organization (Free Alternative)

### Step 1: Create Cloud Identity Account

1. **Sign up for Cloud Identity**
   - Go to [Cloud Identity](https://cloud.google.com/identity)
   - Click "Get started for free"
   - Choose "Set up Cloud Identity for my organization"

2. **Domain Configuration**
   - Enter your domain name
   - If you don't have a domain, you can purchase one through Google
   - **For GDPR**: Choose EU-based domain registrar and use EU contact info

3. **Business Information**
   - **Important**: Use EU-based business address
   - Enter accurate contact information
   - Select appropriate business size

### Step 2: Verify Domain

1. **Choose Verification Method**
   - DNS TXT record (recommended)
   - HTML file upload
   - Google Analytics
   - Google Tag Manager

2. **DNS TXT Record Method**
   ```bash
   # Add this TXT record to your domain DNS
   # Name: @
   # Value: google-site-verification=abc123xyz789...
   
   # Check DNS propagation
   dig TXT yourdomain.com
   ```

3. **Complete Verification**
   - Return to Cloud Identity setup
   - Click "Verify domain"
   - Wait for confirmation

### Step 3: Access Google Cloud

1. **Sign in to Google Cloud Console**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Use your Cloud Identity admin account

2. **Organization Auto-Creation**
   - Organization is automatically created upon first sign-in
   - Verify with: `gcloud organizations list`

## Option 3: Personal Gmail Account (Not Recommended for GDPR)

⚠️ **Limited GDPR Compliance**: Personal Gmail accounts cannot create organizations with proper policy controls.

### Limitations:
- No organization-level policies
- Cannot restrict resource locations centrally
- Limited audit capabilities
- No centralized billing
- Reduced compliance features

### If You Must Use Personal Gmail:
1. Create projects directly without organization
2. Manually configure each project for EU regions
3. Set up individual project-level logging
4. Consider upgrading to Cloud Identity later

## Post-Organization Setup

### 1. Create GDPR-Compliant Project Structure

```bash
# Set default organization
gcloud config set resource_manager/organization $ORG_ID

# Create EU project
gcloud projects create your-eu-vertex-project \
  --name="EU Vertex AI Project" \
  --organization=$ORG_ID

# Link billing (required for Vertex AI)
gcloud billing projects link your-eu-vertex-project \
  --billing-account=BILLING_ACCOUNT_ID
```

### 2. Set Up IAM Structure

```bash
# Create groups for different roles
gcloud identity groups create vertex-ai-users@yourdomain.com \
  --display-name="Vertex AI Users" \
  --description="Users with access to Vertex AI"

# Grant organization-level permissions
gcloud organizations add-iam-policy-binding $ORG_ID \
  --member="group:vertex-ai-users@yourdomain.com" \
  --role="roles/aiplatform.user"
```

### 3. Enable Required APIs

```bash
# Enable APIs for the organization
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable cloudbilling.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable logging.googleapis.com
```

## Organization Management Best Practices

### 1. Folder Structure
```
Organization: yourcompany.eu
├── Folder: Production
│   └── Project: prod-vertex-ai-eu
├── Folder: Development  
│   └── Project: dev-vertex-ai-eu
└── Folder: Compliance
    └── Project: audit-logs-eu
```

### 2. Policy Inheritance
- Set restrictive policies at organization level
- Allow exceptions at folder/project level if needed
- Regularly audit policy compliance

### 3. Billing Organization
```bash
# Create separate billing accounts for different departments
gcloud billing accounts list
gcloud billing projects link PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

## Troubleshooting

### Common Issues

1. **Domain Verification Fails**
   - Check DNS propagation: `nslookup -type=TXT yourdomain.com`
   - Wait up to 24 hours for DNS changes
   - Ensure TXT record is at root domain (@)

2. **Organization Not Created**
   - Make sure you're signing in with the domain admin account
   - Check if Google Workspace/Cloud Identity is fully activated
   - Contact Google Support if organization doesn't appear

3. **Policy Application Fails**
   - Verify you have Organization Policy Administrator role
   - Check organization ID is correct
   - Ensure proper YAML formatting

### Getting Help

- **Google Cloud Support**: Available with paid support plans
- **Community**: [Google Cloud Community](https://www.googlecloudcommunity.com)
- **Documentation**: [Cloud Resource Manager](https://cloud.google.com/resource-manager/docs)

## Cost Considerations

### Google Workspace
- Business Starter: €5.20/user/month
- Business Standard: €10.40/user/month
- Required for full organization features

### Cloud Identity (Free Tier)
- Free for up to 50 users
- Basic identity management
- Limited admin features

### Recommendations
- Start with Cloud Identity Free if budget is tight
- Upgrade to Google Workspace for full enterprise features
- Consider Workspace only for admin accounts, free accounts for regular users

## Next Steps

After creating your organization:

1. Follow the [Vertex AI GDPR Setup Guide](vertex-gdpr-setup-guide.md)
2. Create projects in EU regions
3. Set up service accounts with proper permissions
4. Configure logging and monitoring
5. Test your Vertex AI setup with the provided scripts

## Security Considerations

- Use strong passwords and 2FA for admin accounts
- Regularly review organization policies
- Monitor access logs and unusual activities
- Keep contact information up to date
- Backup important configuration and policies