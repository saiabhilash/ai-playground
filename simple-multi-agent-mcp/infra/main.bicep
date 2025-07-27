targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the resource group. Generated from environment name.')
param resourceGroupName string = ''

// Generate a unique token for resource naming
var resourceToken = uniqueString(subscription().id, location, environmentName)

// Construct resource group name
var finalResourceGroupName = !empty(resourceGroupName) ? resourceGroupName : 'rg-${environmentName}'

// Resource prefix (3 characters max)
var resourcePrefix = 'aif'

// Create resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: finalResourceGroupName
  location: location
  tags: {
    'azd-env-name': environmentName
    'project': 'simple-multi-agent-foundry'
  }
}

// Deploy main resources within the resource group
module resources 'modules/main-resources.bicep' = {
  name: 'main-resources'
  scope: rg
  params: {
    location: location
    environmentName: environmentName
    resourceToken: resourceToken
    resourcePrefix: resourcePrefix
  }
}

// Outputs required by AZD
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output RESOURCE_GROUP_ID string = rg.id
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = resources.outputs.AZURE_CONTAINER_REGISTRY_ENDPOINT
output AZURE_CONTAINER_REGISTRY_NAME string = resources.outputs.AZURE_CONTAINER_REGISTRY_NAME
output AZURE_CONTAINER_APP_ENVIRONMENT_ID string = resources.outputs.AZURE_CONTAINER_APP_ENVIRONMENT_ID
output AZURE_CONTAINER_APP_NAME string = resources.outputs.AZURE_CONTAINER_APP_NAME
output AZURE_AI_PROJECT_ENDPOINT string = resources.outputs.AZURE_AI_PROJECT_ENDPOINT
output AZURE_OPENAI_ENDPOINT string = resources.outputs.AZURE_OPENAI_ENDPOINT
output AZURE_OPENAI_DEPLOYMENT_NAME string = resources.outputs.AZURE_OPENAI_DEPLOYMENT_NAME
output AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING string = resources.outputs.AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING
