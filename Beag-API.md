# Beag.io SaaS Client API Integration Guide

The SaaS Client API allows you to programmatically access your clients' subscription details. Use it to verify subscription status and control feature access in your server-side application.

## 📋 Overview

### How It Works

The SaaS Client API workflow:

1. **Server Authentication**: Your server makes authenticated requests using your private API key
2. **Client Lookup**: Look up client subscription information by email or client ID
3. **Subscription Data**: API returns detailed subscription information including status, plan, and billing dates
4. **Access Control**: Your application uses this data to control feature access based on subscription status and plan level

### Base URL

All API endpoints use this base URL:
```
https://my-saas-basic-api-d5e3hpgdf0gnh2em.eastus-01.azurewebsites.net/api/v1/saas
```

### Authentication

All requests require your API key in the `X-API-KEY` header:
```
X-API-KEY: YOUR_SAAS_API_KEY
```

⚠️ **Security Important**: Keep your API key confidential and only use it server-side, never in client-side code.

## 🔗 API Endpoints

### 1. Get Client by Email

Retrieve subscription details for a client using their email address.

**Endpoint:**
```
GET /clients/by-email/{email}
```

**Headers:**
```
X-API-KEY: YOUR_SAAS_API_KEY
```

**Example Request:**
```bash
curl -X GET "https://my-saas-basic-api-d5e3hpgdf0gnh2em.eastus-01.azurewebsites.net/api/v1/saas/clients/by-email/user%40example.com" \
     -H "X-API-KEY: YOUR_SAAS_API_KEY"
```

### 2. Get Client by ID

Retrieve subscription details for a client using their internal client ID.

**Endpoint:**
```
GET /clients/by-id/{client_id}
```

**Headers:**
```
X-API-KEY: YOUR_SAAS_API_KEY
```

**Example Request:**
```bash
curl -X GET "https://my-saas-basic-api-d5e3hpgdf0gnh2em.eastus-01.azurewebsites.net/api/v1/saas/clients/by-id/456" \
     -H "X-API-KEY: YOUR_SAAS_API_KEY"
```

## 📤 Response Format

### Success Response (200 OK)

```json
{
  "email": "client_email@example.com",
  "status": "PAID", 
  "plan_id": 123,
  "start_date": "2023-10-26T10:00:00Z",
  "end_date": "2024-10-26T10:00:00Z",
  "my_saas_app_id": "bgapp_61_2.kxkRXDR0UWs",
  "client_id": 456
}
```

### Subscription Status Values

| Status | Description |
|--------|-------------|
| `PAID` | Subscription is active and paid |
| `FAILED` | Payment has failed |
| `CANCELLED` | Subscription has been cancelled |
| `REFUNDED` | Payment was refunded |
| `PAUSED` | Subscription is temporarily paused |
| `RESUMED` | Subscription was resumed after being paused |

### Error Responses

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| 401 | - | Missing API key |
| 403 | `api_key_invalid` | Invalid or inactive API key |
| 404 | `client_not_found` | Client with specified email/ID not found |
| 404 | `subscription_not_found` | No active subscription for this client |
| 404 | `app_not_found` | Application ID not found |
| 500 | `server_error` | Unexpected server error occurred |
| - | `app_inactive` | SaaS application is inactive |

## 💻 Implementation Example

### Server-Side JavaScript

```javascript
/**
 * Check if a user has an active subscription
 * @param {string} email - User's email address
 * @returns {Object|null} Subscription data or null if not found
 */
async function checkUserSubscription(email) {
  try {
    // IMPORTANT: This code should run on your server, never on the client
    const response = await fetch(
      `https://my-saas-basic-api-d5e3hpgdf0gnh2em.eastus-01.azurewebsites.net/api/v1/saas/clients/by-email/${encodeURIComponent(email)}`,
      {
        method: 'GET',
        headers: {
          'X-API-KEY': process.env.BEAG_API_KEY // Use environment variable
        }
      }
    );
    
    if (response.ok) {
      const data = await response.json();
      
      // Log subscription details
      console.log('✅ Subscription found:', {
        status: data.status,
        plan: data.plan_id,
        expires: new Date(data.end_date).toLocaleDateString()
      });
      
      return data;
    } else {
      const error = await response.json();
      console.warn('⚠️ Subscription check failed:', error.message);
      return null;
    }
  } catch (error) {
    console.error('❌ API request failed:', error.message);
    return null;
  }
}

/**
 * Check if user has access to specific features based on plan
 * @param {Object} subscriptionData - Data from checkUserSubscription
 * @returns {Object} Feature access permissions
 */
function getFeatureAccess(subscriptionData) {
  if (!subscriptionData) {
    return { hasAccess: false, plan: 'free' };
  }

  const isActive = ['PAID', 'ACTIVE', 'TRIAL', 'RESUMED'].includes(
    subscriptionData.status.toUpperCase()
  );

  return {
    hasAccess: isActive,
    plan: subscriptionData.plan_id,
    status: subscriptionData.status,
    expiresAt: new Date(subscriptionData.end_date)
  };
}
```

### Usage Example

```javascript
// Example: Protecting an API endpoint
app.get('/api/premium-feature', async (req, res) => {
  const userEmail = req.user.email; // Get from your auth system
  
  const subscription = await checkUserSubscription(userEmail);
  const access = getFeatureAccess(subscription);
  
  if (!access.hasAccess) {
    return res.status(403).json({
      error: 'Premium subscription required',
      message: 'This feature requires an active subscription'
    });
  }
  
  // User has access, proceed with premium feature
  res.json({ data: 'Premium content here' });
});
```

## 🔧 Implementation Steps

### 1. Generate API Key
1. Log in to your Beag.io dashboard
2. Navigate to API settings
3. Generate a new API key for your application
4. Store the key securely in your environment variables

### 2. Implement Server-Side Validation
1. Create backend endpoints to check subscription status
2. Use the API key to authenticate requests to Beag.io
3. Cache subscription data briefly to reduce API calls

### 3. Control Feature Access
1. Use subscription status to enable/disable features
2. Check plan level for tiered feature access
3. Handle subscription expiration gracefully

## 🔒 Security Best Practices

### API Key Security
- ❌ **Never** expose your API key in client-side code
- ✅ Store API key in environment variables
- ✅ Use server-side validation only
- ✅ Rotate API keys periodically

### Error Handling
- ✅ Implement proper error handling for all API responses
- ✅ Log errors for monitoring and debugging
- ✅ Provide graceful fallbacks for API failures
- ✅ Handle network timeouts and retries

### Performance Optimization
- ✅ Cache subscription data for 5-15 minutes to reduce API calls
- ✅ Use asynchronous requests to avoid blocking
- ✅ Implement request timeout handling
- ✅ Monitor API usage and rate limits

### Data Privacy
- ✅ Only request necessary subscription data
- ✅ Don't store sensitive subscription details longer than needed
- ✅ Follow data protection regulations (GDPR, CCPA)
- ✅ Implement proper data retention policies

## 🐛 Troubleshooting

### Common Issues

**403 Forbidden Error**
- Check if your API key is correct
- Verify the API key is active in your Beag dashboard
- Ensure you're using the `X-API-KEY` header

**404 Not Found Error**
- Verify the email address is correct
- Check if the user has an active subscription
- Ensure the client exists in your Beag system

**Network/Timeout Errors**
- Implement retry logic with exponential backoff
- Check your server's network connectivity
- Verify the API endpoint URL is correct

**Rate Limiting**
- Cache subscription data to reduce API calls
- Implement proper request spacing
- Monitor your API usage in the Beag dashboard