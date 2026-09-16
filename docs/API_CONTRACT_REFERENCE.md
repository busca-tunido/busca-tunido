# BuscaTuNido API Contract Reference

This document serves as the canonical contract reference for AI agents, workers, and orchestrators developing across the `api` (NestJS) and `web` (Next.js) workspaces.

---

## 1. Global Response Envelope

All API endpoints wrap payloads in the standard response envelope produced by the NestJS `TransformInterceptor`:

```typescript
export type ApiResponseEnvelope<T> = {
  success: boolean;
  statusCode: number;
  timestamp: string;
  data: T;
};
```

When an error occurs, the global exception filter produces:
```typescript
export type ApiErrorResponse = {
  success: false;
  statusCode: number;
  timestamp: string;
  message: string;
  error?: string;
  errors?: Record<string, string[]>;
};
```

---

## 2. Pensions Endpoints

### `GET /pensions`
Retrieves a paginated list of active pensions.

- **Query Parameters**:
  - `page?: number` (default: 1)
  - `limit?: number` (default: 12, max: 50)
  - `city?: string`
  - `search?: string`
  - `minPrice?: number`
  - `maxPrice?: number`
  - `roomType?: 'SINGLE' | 'SHARED'`
  - `genderPreference?: 'ANY' | 'FEMALE_ONLY' | 'MALE_ONLY'`
  - `sortBy?: 'relevance' | 'distance' | 'price_asc' | 'price_desc' | 'rating'`
  - `latitude?: number`
  - `longitude?: number`
  - `radiusKm?: number` (default: 30)
  - `minLat?: number`, `maxLat?: number`, `minLng?: number`, `maxLng?: number` (bounding box)

- **Response (`data`)**:
```typescript
type PaginatedPensions = {
  items: RawPensionSummary[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasMore: boolean;
  };
  nearbyCityCounts: Array<{
    city: string;
    count: number;
    distanceKm?: number;
  }>;
  total: number;
  page: number;
  limit: number;
  totalPages: number;
};
```

### `GET /pensions/:idOrSlug`
Retrieves complete pension details including rooms, amenities, landlord details, and nearby universities.

- **Response (`data`)**: `RawPensionDetail`
  - `id`: string (UUID)
  - `slug`: string
  - `title`: string
  - `description`: string
  - `address`: string
  - `neighborhood`: string
  - `city`: string
  - `latitude`: number
  - `longitude`: number
  - `baseMonthlyPrice`: Decimal / number
  - `deposit`: Decimal / number | null
  - `currency`: string (CLP)
  - `waterIncluded`: boolean
  - `electricityIncluded`: boolean
  - `gasIncluded`: boolean
  - `internetIncluded`: boolean
  - `curfewTime`: string | null
  - `guestsAllowed`: boolean
  - `smokingAllowed`: boolean
  - `petsAllowed`: boolean
  - `genderPreference`: 'ANY' | 'FEMALE_ONLY' | 'MALE_ONLY'
  - `quietHoursStart`: string | null
  - `quietHoursEnd`: string | null
  - `verificationStatus`: 'UNVERIFIED' | 'COMMUNITY_VERIFIED' | 'OFFICIALLY_VERIFIED'
  - `ratingAverage`: Decimal / number (e.g. 4.25 or 0)
  - `ratingCount`: number
  - `isActive`: boolean
  - `images`: Array<{ id: string; url: string; caption?: string | null; isFeatured: boolean; sortOrder: number }>
  - `rooms`: Array<{ id: string; roomNumber?: string; title: string; type: string; monthlyPrice: Decimal / number; deposit?: Decimal / number; isAvailable: boolean; images: string[] }>
  - `amenities`: Array<{ id: string; slug: string; name: string; category: string; iconKey?: string }>
  - `nearbyUniversities`: Array<{ distanceMeters: number; walkingMinutes?: number; university: RawUniversity }>
  - `landlord`: { id: string; firstName: string; lastName: string; phone?: string; avatarUrl?: string }

---

## 3. Reviews Endpoints

### `GET /pensions/:pensionId/reviews`
Retrieves reviews for a given pension with server-side pagination, rating filtering, and sorting.

- **Query Parameters**:
  - `page?: number` (default: 1)
  - `limit?: number` (default: 10, max: 50)
  - `rating?: number` (filter 1..5)
  - `sortBy?: 'newest' | 'oldest' | 'rating_desc' | 'rating_asc'` (default: `'newest'`)

- **Response (`data`)**:
```typescript
type PaginatedReviewsResponse = {
  items: RawReview[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasMore: boolean;
  };
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  hasMore: boolean;
};

type RawReview = {
  id: string;
  pensionId: string;
  userId: string;
  overallRating: number; // integer 1..5
  cleanlinessRating?: number | null; // integer 1..5
  landlordRating?: number | null; // integer 1..5
  quietnessRating?: number | null; // integer 1..5
  wifiRating?: number | null; // integer 1..5
  comment: string;
  images: string[]; // URLs stored in PostgreSQL array
  stayDurationCategory?: 'FEW_DAYS' | 'FEW_WEEKS' | 'ONE_SEMESTER' | 'ONE_YEAR' | 'MORE_THAN_A_YEAR' | null;
  stayStartDate?: string | null;
  stayEndDate?: string | null;
  exactStayDays?: number | null;
  isResidentVerified: boolean;
  isHidden: boolean;
  createdAt: string; // ISO 8601
  updatedAt: string;
  user: {
    id: string;
    firstName: string;
    lastName: string;
    avatarUrl?: string | null;
    university?: {
      shortName?: string | null;
      name?: string;
    } | null;
  };
};
```

### `POST /pensions/:pensionId/reviews`
Creates a review for a pension. Requires JWT Bearer token (student role).

- **Request Body**:
```typescript
type CreateReviewDto = {
  overallRating: number; // 1..5
  comment: string; // min 15 chars
  cleanlinessRating?: number;
  landlordRating?: number;
  quietnessRating?: number;
  wifiRating?: number;
  stayDurationCategory?: 'FEW_DAYS' | 'FEW_WEEKS' | 'ONE_SEMESTER' | 'ONE_YEAR' | 'MORE_THAN_A_YEAR';
  images?: string[]; // max 3 URLs
};
```

### `POST /reviews/:id/helpful`
Votes a review as helpful.

- **Response (`data`)**:
```typescript
type VoteHelpfulResponse = {
  helpfulCount: number;
  voted: boolean;
};
```

---

## 4. Frontend Types & Mapping Rules

### Pension DTO (`PensionItemDto`)
To guarantee compatibility between API responses and UI layers, `PensionItemDto` MUST provide both keys:
```typescript
export type PensionItemDto = {
  id: string;
  title: string;
  city: string;
  // Calificación promedio: soportar ambos nombres
  averageRating?: number;
  ratingAverage?: number;
  // Contador de reseñas: soportar ambos nombres
  reviewsCount?: number;
  ratingCount?: number;
  // ... otras propiedades
};
```

### Pension UI Item (`PensionItem`)
```typescript
export type PensionItem = {
  id: string;
  title: string;
  city: string;
  ratingAverage: number; // 0..5 siempre numérico
  reviewsCount: number; // >= 0
  // ...
};
```

### Review UI Item (`PensionReview`)
```typescript
export type PensionReview = {
  id: string;
  pensionId: string;
  overallRating: number;
  rating?: number;
  comment: string;
  images?: Array<string | { id?: string; url: string; caption?: string }>;
  createdAt: string;
  user: {
    id: string;
    firstName: string;
    lastName: string;
    avatarUrl?: string;
    university?: {
      name?: string;
      shortName?: string;
    };
  };
};
```
When rendering photos, always normalize:
```typescript
const photoUrl = typeof img === 'string' ? img : img?.url || '';
```
