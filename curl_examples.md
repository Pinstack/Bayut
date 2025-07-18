# Bayut.sa Algolia API - cURL Examples

This file contains cURL examples for directly using the Algolia API that powers Bayut.sa.

## API Configuration

- **Endpoint**: `https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries`
- **Application ID**: `LL8IZ711CS`
- **API Key**: `5b970b39b22a4ff1b99e5167696eef3f`
- **Index**: `bayut-sa-production-ads-city-level-score-ar`

## Basic Search Example

```bash
curl -X POST "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" \
  -H "X-Algolia-Application-Id: LL8IZ711CS" \
  -H "X-Algolia-API-Key: 5b970b39b22a4ff1b99e5167696eef3f" \
  -H "X-Algolia-Agent: Algolia for JavaScript (3.35.1); Browser (lite)" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "indexName": "bayut-sa-production-ads-city-level-score-ar",
        "query": "",
        "params": "hitsPerPage=25&page=0&facets=*&attributesToRetrieve=state,type,agency,area,baths,category,additionalCategories,contactName,externalID,sourceID,id,location,objectID,phoneNumber,coverPhoto,photoCount,price,product,productLabel,purpose,geography,permitNumber,referenceNumber,rentFrequency,rooms,slug,slug_l1,title,title_l1,createdAt,updatedAt,ownerID,isVerified,propertyTour,verification,completionDetails,completionStatus,furnishingStatus,coverVideo,videoCount,description,description_l1,descriptionTranslated,descriptionTranslated_l1,floorPlanID,panoramaCount,hasMatchingFloorPlans,photoIDs,reactivatedAt,hidePrice,extraFields,projectNumber,locationPurposeTier,hasRedirectionLink,ownerAgent,hasEmail,plotArea,offplanDetails,paymentPlans,paymentPlanSummaries,project,availabilityStatus,userExternalID,units,unitCategories,downPayment,clips,contactMethodAvailability,agentAdStoriesCount,isProjectOwned,documents"
      }
    ]
  }'
```

## Search with Filters

### Apartments for Sale
```bash
curl -X POST "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" \
  -H "X-Algolia-Application-Id: LL8IZ711CS" \
  -H "X-Algolia-API-Key: 5b970b39b22a4ff1b99e5167696eef3f" \
  -H "X-Algolia-Agent: Algolia for JavaScript (3.35.1); Browser (lite)" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "indexName": "bayut-sa-production-ads-city-level-score-ar",
        "query": "",
        "params": "hitsPerPage=25&page=0&facets=*&filters=category:apartments AND purpose:for-sale&attributesToRetrieve=state,type,agency,area,baths,category,additionalCategories,contactName,externalID,sourceID,id,location,objectID,phoneNumber,coverPhoto,photoCount,price,product,productLabel,purpose,geography,permitNumber,referenceNumber,rentFrequency,rooms,slug,slug_l1,title,title_l1,createdAt,updatedAt,ownerID,isVerified,propertyTour,verification,completionDetails,completionStatus,furnishingStatus,coverVideo,videoCount,description,description_l1,descriptionTranslated,descriptionTranslated_l1,floorPlanID,panoramaCount,hasMatchingFloorPlans,photoIDs,reactivatedAt,hidePrice,extraFields,projectNumber,locationPurposeTier,hasRedirectionLink,ownerAgent,hasEmail,plotArea,offplanDetails,paymentPlans,paymentPlanSummaries,project,availabilityStatus,userExternalID,units,unitCategories,downPayment,clips,contactMethodAvailability,agentAdStoriesCount,isProjectOwned,documents"
      }
    ]
  }'
```

### Villas for Rent
```bash
curl -X POST "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" \
  -H "X-Algolia-Application-Id: LL8IZ711CS" \
  -H "X-Algolia-API-Key: 5b970b39b22a4ff1b99e5167696eef3f" \
  -H "X-Algolia-Agent: Algolia for JavaScript (3.35.1); Browser (lite)" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "indexName": "bayut-sa-production-ads-city-level-score-ar",
        "query": "",
        "params": "hitsPerPage=25&page=0&facets=*&filters=category:villas AND purpose:for-rent&attributesToRetrieve=state,type,agency,area,baths,category,additionalCategories,contactName,externalID,sourceID,id,location,objectID,phoneNumber,coverPhoto,photoCount,price,product,productLabel,purpose,geography,permitNumber,referenceNumber,rentFrequency,rooms,slug,slug_l1,title,title_l1,createdAt,updatedAt,ownerID,isVerified,propertyTour,verification,completionDetails,completionStatus,furnishingStatus,coverVideo,videoCount,description,description_l1,descriptionTranslated,descriptionTranslated_l1,floorPlanID,panoramaCount,hasMatchingFloorPlans,photoIDs,reactivatedAt,hidePrice,extraFields,projectNumber,locationPurposeTier,hasRedirectionLink,ownerAgent,hasEmail,plotArea,offplanDetails,paymentPlans,paymentPlanSummaries,project,availabilityStatus,userExternalID,units,unitCategories,downPayment,clips,contactMethodAvailability,agentAdStoriesCount,isProjectOwned,documents"
      }
    ]
  }'
```

## Advanced Filtering Examples

### Price Range Filter
```bash
curl -X POST "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" \
  -H "X-Algolia-Application-Id: LL8IZ711CS" \
  -H "X-Algolia-API-Key: 5b970b39b22a4ff1b99e5167696eef3f" \
  -H "X-Algolia-Agent: Algolia for JavaScript (3.35.1); Browser (lite)" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "indexName": "bayut-sa-production-ads-city-level-score-ar",
        "query": "",
        "params": "hitsPerPage=25&page=0&facets=*&filters=purpose:for-sale AND category:apartments AND price>=500000 AND price<=2000000&attributesToRetrieve=state,type,agency,area,baths,category,additionalCategories,contactName,externalID,sourceID,id,location,objectID,phoneNumber,coverPhoto,photoCount,price,product,productLabel,purpose,geography,permitNumber,referenceNumber,rentFrequency,rooms,slug,slug_l1,title,title_l1,createdAt,updatedAt,ownerID,isVerified,propertyTour,verification,completionDetails,completionStatus,furnishingStatus,coverVideo,videoCount,description,description_l1,descriptionTranslated,descriptionTranslated_l1,floorPlanID,panoramaCount,hasMatchingFloorPlans,photoIDs,reactivatedAt,hidePrice,extraFields,projectNumber,locationPurposeTier,hasRedirectionLink,ownerAgent,hasEmail,plotArea,offplanDetails,paymentPlans,paymentPlanSummaries,project,availabilityStatus,userExternalID,units,unitCategories,downPayment,clips,contactMethodAvailability,agentAdStoriesCount,isProjectOwned,documents"
      }
    ]
  }'
```

### Location and Room Filter
```bash
curl -X POST "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" \
  -H "X-Algolia-Application-Id: LL8IZ711CS" \
  -H "X-Algolia-API-Key: 5b970b39b22a4ff1b99e5167696eef3f" \
  -H "X-Algolia-Agent: Algolia for JavaScript (3.35.1); Browser (lite)" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "indexName": "bayut-sa-production-ads-city-level-score-ar",
        "query": "",
        "params": "hitsPerPage=25&page=0&facets=*&filters=purpose:for-sale AND category:apartments AND location:الرياض AND rooms>=2&attributesToRetrieve=state,type,agency,area,baths,category,additionalCategories,contactName,externalID,sourceID,id,location,objectID,phoneNumber,coverPhoto,photoCount,price,product,productLabel,purpose,geography,permitNumber,referenceNumber,rentFrequency,rooms,slug,slug_l1,title,title_l1,createdAt,updatedAt,ownerID,isVerified,propertyTour,verification,completionDetails,completionStatus,furnishingStatus,coverVideo,videoCount,description,description_l1,descriptionTranslated,descriptionTranslated_l1,floorPlanID,panoramaCount,hasMatchingFloorPlans,photoIDs,reactivatedAt,hidePrice,extraFields,projectNumber,locationPurposeTier,hasRedirectionLink,ownerAgent,hasEmail,plotArea,offplanDetails,paymentPlans,paymentPlanSummaries,project,availabilityStatus,userExternalID,units,unitCategories,downPayment,clips,contactMethodAvailability,agentAdStoriesCount,isProjectOwned,documents"
      }
    ]
  }'
```

### Verified Properties Only
```bash
curl -X POST "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" \
  -H "X-Algolia-Application-Id: LL8IZ711CS" \
  -H "X-Algolia-API-Key: 5b970b39b22a4ff1b99e5167696eef3f" \
  -H "X-Algolia-Agent: Algolia for JavaScript (3.35.1); Browser (lite)" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "indexName": "bayut-sa-production-ads-city-level-score-ar",
        "query": "",
        "params": "hitsPerPage=25&page=0&facets=*&filters=isVerified:true&attributesToRetrieve=state,type,agency,area,baths,category,additionalCategories,contactName,externalID,sourceID,id,location,objectID,phoneNumber,coverPhoto,photoCount,price,product,productLabel,purpose,geography,permitNumber,referenceNumber,rentFrequency,rooms,slug,slug_l1,title,title_l1,createdAt,updatedAt,ownerID,isVerified,propertyTour,verification,completionDetails,completionStatus,furnishingStatus,coverVideo,videoCount,description,description_l1,descriptionTranslated,descriptionTranslated_l1,floorPlanID,panoramaCount,hasMatchingFloorPlans,photoIDs,reactivatedAt,hidePrice,extraFields,projectNumber,locationPurposeTier,hasRedirectionLink,ownerAgent,hasEmail,plotArea,offplanDetails,paymentPlans,paymentPlanSummaries,project,availabilityStatus,userExternalID,units,unitCategories,downPayment,clips,contactMethodAvailability,agentAdStoriesCount,isProjectOwned,documents"
      }
    ]
  }'
```

## Pagination Example

### Page 2 (50-75 results)
```bash
curl -X POST "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" \
  -H "X-Algolia-Application-Id: LL8IZ711CS" \
  -H "X-Algolia-API-Key: 5b970b39b22a4ff1b99e5167696eef3f" \
  -H "X-Algolia-Agent: Algolia for JavaScript (3.35.1); Browser (lite)" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "indexName": "bayut-sa-production-ads-city-level-score-ar",
        "query": "",
        "params": "hitsPerPage=25&page=1&facets=*&filters=purpose:for-sale AND category:apartments&attributesToRetrieve=state,type,agency,area,baths,category,additionalCategories,contactName,externalID,sourceID,id,location,objectID,phoneNumber,coverPhoto,photoCount,price,product,productLabel,purpose,geography,permitNumber,referenceNumber,rentFrequency,rooms,slug,slug_l1,title,title_l1,createdAt,updatedAt,ownerID,isVerified,propertyTour,verification,completionDetails,completionStatus,furnishingStatus,coverVideo,videoCount,description,description_l1,descriptionTranslated,descriptionTranslated_l1,floorPlanID,panoramaCount,hasMatchingFloorPlans,photoIDs,reactivatedAt,hidePrice,extraFields,projectNumber,locationPurposeTier,hasRedirectionLink,ownerAgent,hasEmail,plotArea,offplanDetails,paymentPlans,paymentPlanSummaries,project,availabilityStatus,userExternalID,units,unitCategories,downPayment,clips,contactMethodAvailability,agentAdStoriesCount,isProjectOwned,documents"
      }
    ]
  }'
```

## Search with Text Query

### Search for specific location
```bash
curl -X POST "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" \
  -H "X-Algolia-Application-Id: LL8IZ711CS" \
  -H "X-Algolia-API-Key: 5b970b39b22a4ff1b99e5167696eef3f" \
  -H "X-Algolia-Agent: Algolia for JavaScript (3.35.1); Browser (lite)" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "indexName": "bayut-sa-production-ads-city-level-score-ar",
        "query": "الرياض",
        "params": "hitsPerPage=25&page=0&facets=*&attributesToRetrieve=state,type,agency,area,baths,category,additionalCategories,contactName,externalID,sourceID,id,location,objectID,phoneNumber,coverPhoto,photoCount,price,product,productLabel,purpose,geography,permitNumber,referenceNumber,rentFrequency,rooms,slug,slug_l1,title,title_l1,createdAt,updatedAt,ownerID,isVerified,propertyTour,verification,completionDetails,completionStatus,furnishingStatus,coverVideo,videoCount,description,description_l1,descriptionTranslated,descriptionTranslated_l1,floorPlanID,panoramaCount,hasMatchingFloorPlans,photoIDs,reactivatedAt,hidePrice,extraFields,projectNumber,locationPurposeTier,hasRedirectionLink,ownerAgent,hasEmail,plotArea,offplanDetails,paymentPlans,paymentPlanSummaries,project,availabilityStatus,userExternalID,units,unitCategories,downPayment,clips,contactMethodAvailability,agentAdStoriesCount,isProjectOwned,documents"
      }
    ]
  }'
```

## Response Format

The API returns JSON in this format:

```json
{
  "results": [
    {
      "hits": [
        {
          "objectID": "12345",
          "title": "شقة فاخرة للبيع في الرياض",
          "price": 1500000,
          "location": "الرياض",
          "area": 150.5,
          "rooms": 3,
          "baths": 2,
          "category": "apartments",
          "purpose": "for-sale",
          "coverPhoto": "https://images.bayut.sa/...",
          "photoCount": 15,
          "description": "شقة فاخرة...",
          "agency": "شركة عقارية",
          "contactName": "أحمد محمد",
          "phoneNumber": "+966501234567",
          "isVerified": true,
          "createdAt": "2024-01-10T08:00:00",
          "updatedAt": "2024-01-15T09:30:00",
          "slug": "شقة-فاخرة-للبيع-في-الرياض",
          "externalID": "EXT12345",
          "geography": {
            "lat": 24.7136,
            "lng": 46.6753
          }
        }
      ],
      "nbHits": 1250,
      "page": 0,
      "nbPages": 50,
      "hitsPerPage": 25,
      "exhaustiveNbHits": true,
      "exhaustiveTypo": true,
      "query": "",
      "params": "...",
      "processingTimeMS": 5
    }
  ]
}
```

## Notes

1. **Rate Limiting**: Be respectful and add delays between requests
2. **Pagination**: Use the `page` parameter (0-based) for pagination
3. **Filters**: Use Algolia filter syntax (e.g., `attribute:value`)
4. **Text Search**: Use the `query` parameter for text-based search
5. **Facets**: Use `facets=*` to get facet information for filtering

## Using with Python requests

```python
import requests
import json

url = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries"
headers = {
    "X-Algolia-Application-Id": "LL8IZ711CS",
    "X-Algolia-API-Key": "5b970b39b22a4ff1b99e5167696eef3f",
    "X-Algolia-Agent": "Algolia for JavaScript (3.35.1); Browser (lite)",
    "Content-Type": "application/json"
}

data = {
    "requests": [
        {
            "indexName": "bayut-sa-production-ads-city-level-score-ar",
            "query": "",
            "params": "hitsPerPage=25&page=0&facets=*&filters=purpose:for-sale AND category:apartments"
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
results = response.json()
print(json.dumps(results, indent=2))
``` 