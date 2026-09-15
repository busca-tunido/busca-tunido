# Task: Landlord Interactive Map Location Picker & WebP Pre-Optimization (`web/tasks/landlord-interactive-map-picker-webp-upload.md`)

## Execution Profile
- **Wave / Batch**: Wave 1
- **Execution Mode**: `PARALLEL`
- **Assigned Role**: `Worker Agent`
- **Dependencies (`depends_on`)**: None
- **Collision Risk**: `LOW (Isolated files)`

## Target Files
- **Exclusive**:
  - `src/components/location-map-picker.tsx`
  - `src/lib/image-processor.ts`
- **Shared / Integration Points**:
  - `src/components/pension-form.tsx` (Requiere Merge Gate si hay formularios concurrentes)

## Objective

Enhance the landlord pension creation and editing interface:
1. Completely abstract coordinates: The landlord places a pin on an interactive map or searches an address, and the frontend automatically derives `latitude` and `longitude` without manual numeric inputs.
2. Add client-side image compression and WebP conversion before uploading photos to the backend pipeline.

---

## Technical Specifications

### 1. Interactive Map Location Picker (`src/components/location-map-picker.tsx`)
- Render an interactive Leaflet map centered on the selected city or current location.
- Provide a draggable marker:
  - On drag end: Update internal state with precise `latitude` and `longitude`.
  - Perform reverse geocoding to suggest the street name and neighborhood automatically.
- Ensure form inputs for latitude/longitude are completely hidden from the user.

### 2. Client-Side Image Pre-Optimization (`src/lib/image-processor.ts`)
- Accept image uploads (PNG, JPEG, HEIC, WebP).
- Convert image in browser via HTML5 Canvas / OffscreenCanvas to WebP format before network transmission.
- Reduces upload bandwidth and speeds up the server-side Sharp processing pipeline.

---

## Checklist

- [ ] Implement `src/components/location-map-picker.tsx` with Leaflet draggable marker.
- [ ] Connect map coordinates seamlessly to pension creation form state.
- [ ] Implement `src/lib/image-processor.ts` for client-side WebP conversion.
- [ ] Ensure landlord form has zero manual number inputs for coordinates.
- [ ] Validate code quality with Biome (`pnpm run check && pnpm run review`).
- [ ] Verify build with `pnpm run build`.

---

## Verification

- Code Quality (Biome): `pnpm run check && pnpm run review`
- Build & Typecheck: `pnpm build`
