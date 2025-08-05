# How to Deploy GPT-4 Models on Azure OpenAI

This guide walks you through deploying GPT-4 models (including GPT-4 Turbo) on Azure OpenAI Service.

## Prerequisites

- Azure subscription with billing enabled
- Access to Azure OpenAI Service (requires approval)
- Sufficient quota for GPT-4 models

## Step 1: Request Access to Azure OpenAI Service

1. **Apply for Access**
   - Go to [Azure OpenAI Access Request Form](https://aka.ms/oai/access)
   - Fill out the application form with your use case details
   - Wait for approval (can take several days to weeks)

2. **Check Approval Status**
   - You'll receive an email notification when approved
   - Access will be granted to your Azure subscription

## Step 2: Create Azure OpenAI Resource

### Via Azure Portal

1. **Navigate to Azure Portal**
   - Go to [portal.azure.com](https://portal.azure.com)
   - Sign in with your approved Azure account

2. **Create Resource**
   - Click "Create a resource"
   - Search for "Azure OpenAI"
   - Click "Create" on the Azure OpenAI service

3. **Configure Resource**
   - **Subscription**: Select your subscription
   - **Resource Group**: Create new or select existing
   - **Region**: Choose supported region (e.g., East US, West Europe)
   - **Name**: Give your resource a unique name
   - **Pricing Tier**: Select Standard S0

4. **Review and Create**
   - Review your settings
   - Click "Create"
   - Wait for deployment to complete

### Via Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name myResourceGroup --location eastus

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name myOpenAIResource \
  --resource-group myResourceGroup \
  --location eastus \
  --kind OpenAI \
  --sku S0 \
  --subscription mySubscription
```

## Step 3: Deploy GPT-4 Model

### Via Azure OpenAI Studio

1. **Access Azure OpenAI Studio**
   - Go to [oai.azure.com](https://oai.azure.com)
   - Select your Azure OpenAI resource

2. **Navigate to Deployments**
   - Click on "Deployments" in the left sidebar
   - Click "Create new deployment"

3. **Configure Deployment**
   - **Model**: Select GPT-4 or GPT-4 Turbo
     - `gpt-4` (8K context)
     - `gpt-4-32k` (32K context)
     - `gpt-4-turbo` (128K context)
     - `gpt-4-vision-preview` (for image analysis)
   - **Deployment Name**: Choose a name (e.g., "gpt-4-deployment")
   - **Version**: Select model version (latest recommended)
   - **Deployment Type**: Standard

4. **Set Capacity**
   - **Tokens per Minute Rate Limit**: Set based on your needs
   - Start with 10K TPM for testing, scale as needed
   - Note: Higher limits require more quota

5. **Deploy**
   - Click "Create"
   - Wait for deployment to complete

### Via REST API

```bash
# Get access token
ACCESS_TOKEN=$(az account get-access-token --query accessToken -o tsv)

# Create deployment
curl -X PUT "https://management.azure.com/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.CognitiveServices/accounts/{resource-name}/deployments/{deployment-name}?api-version=2023-05-01" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "model": {
        "format": "OpenAI",
        "name": "gpt-4",
        "version": "0613"
      },
      "raiPolicyName": "Microsoft.Default",
      "scaleSettings": {
        "scaleType": "Standard"
      }
    }
  }'
```

## Step 4: Get Deployment Information

### Via Azure Portal

1. **Navigate to Resource**
   - Go to your Azure OpenAI resource
   - Click "Keys and Endpoint" in the left sidebar

2. **Copy Information**
   - **Endpoint**: `https://your-resource.openai.azure.com/`
   - **Key**: Copy Key 1 or Key 2
   - **Deployment Name**: Note your deployment name

### Via Azure OpenAI Studio

1. **Go to Deployments**
   - Click on your deployment
   - Note the deployment name and model details

2. **Check Playground**
   - Use the Chat playground to test your deployment
   - View code samples in different languages

## Step 5: Configure Your Application

Set environment variables:

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key-here"
export AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name"
```

## Available GPT-4 Models

| Model | Context Window | Description | Use Cases |
|-------|----------------|-------------|-----------|
| `gpt-4` | 8,192 tokens | Original GPT-4 | General tasks, coding, analysis |
| `gpt-4-32k` | 32,768 tokens | Extended context GPT-4 | Long documents, detailed analysis |
| `gpt-4-turbo` | 128,000 tokens | Latest, fastest GPT-4 | Complex tasks, large documents |
| `gpt-4-vision-preview` | 128,000 tokens | GPT-4 with vision | Image analysis, multimodal tasks |

## Regional Availability

GPT-4 models are available in specific regions:

- **East US**
- **East US 2**
- **North Central US**
- **South Central US**
- **West Europe**
- **France Central**
- **UK South**
- **Sweden Central**

*Check the latest [Azure OpenAI Service regions](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability) for updates.*

## Pricing Considerations

### Token-Based Pricing
- **Input tokens**: Cost per 1K tokens for prompts
- **Output tokens**: Cost per 1K tokens for completions
- **Image inputs**: Additional cost for vision models

### Example Pricing (as of 2024)
- GPT-4: ~$0.03/1K input tokens, ~$0.06/1K output tokens
- GPT-4 Turbo: ~$0.01/1K input tokens, ~$0.03/1K output tokens
- GPT-4 Vision: Base cost + image analysis fees

*Check [Azure OpenAI pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/) for current rates.*

## Quota Management

1. **Check Current Quota**
   - Go to Azure OpenAI Studio
   - Navigate to "Quotas" section
   - View TPM (Tokens Per Minute) limits

2. **Request Quota Increase**
   - Click "Request quota increase"
   - Justify your business need
   - Wait for approval

## Best Practices

### Security
- Use managed identities when possible
- Rotate API keys regularly
- Implement proper authentication in applications
- Use Azure Key Vault for storing secrets

### Performance
- Start with lower TPM limits and scale gradually
- Implement retry logic with exponential backoff
- Monitor usage and costs
- Cache responses when appropriate

### Cost Optimization
- Use GPT-4 Turbo for most tasks (cheaper and faster)
- Optimize prompt length
- Implement conversation trimming for long chats
- Monitor token usage

## Monitoring and Logging

### Azure Monitor
- Enable diagnostic settings
- Monitor API calls and errors
- Set up alerts for quota limits

### Application Insights
- Track application performance
- Monitor error rates
- Analyze usage patterns

## Troubleshooting

### Common Issues

1. **"Access Denied" Errors**
   - Ensure Azure OpenAI access is approved
   - Check resource permissions
   - Verify API key is correct

2. **"Model Not Found" Errors**
   - Verify deployment name matches exactly
   - Ensure model is deployed and active
   - Check regional availability

3. **Rate Limit Errors (429)**
   - Implement exponential backoff
   - Check TPM quota limits
   - Consider upgrading quota

4. **High Latency**
   - Choose nearest Azure region
   - Optimize prompt length
   - Consider using GPT-4 Turbo

### Support Resources
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Support Portal](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)
- [Azure OpenAI Community](https://techcommunity.microsoft.com/t5/azure-ai-services/ct-p/AzureAIServices)

## Next Steps

1. Test your deployment with the provided Python script
2. Implement proper error handling and retry logic
3. Set up monitoring and alerting
4. Scale your deployment based on usage patterns
5. Explore advanced features like function calling and fine-tuning