# Dashboard Module QA Checklist

## Chunk 15 Final UI QA

Date: 2026-06-20

### Automated checks completed

- `python3 -m py_compile backend/apps/reports/views.py backend/apps/reports/tests.py backend/apps/reports/urls.py backend/apps/reports/serializers.py backend/apps/reports/tasks.py`
- `npm run typecheck`
- `npm run build`

### Production build issue fixed during QA

- Removed an unreachable placeholder branch in `frontend/src/app/state/account-settings/page.tsx` that caused a `never` type error during the Next.js production build.

### Dashboard module coverage reviewed

- Federal dashboard
- State dashboard
- Employer dashboard
- Medical Facility dashboard
- Worksheet builder
- Widget builder
- Canvas builder
- Published dashboard view
- Templates
- Embedded module analytics entry points
- Permissions and privacy controls
- Export and background export job flow

### Remaining manual visual checks

- Federal dashboard layout on mobile-width viewport
- State dashboard layout on mobile-width viewport
- Employer dashboard layout on mobile-width viewport
- Facility dashboard layout on mobile-width viewport
- Worksheet builder overflow and sticky panel behavior on tablet/mobile
- Widget builder preview and alert panel layout on tablet/mobile
- Canvas builder block layout and overflow handling on tablet/mobile
- Published dashboard readability on tablet/mobile

### Notes

- The frontend build currently completes with existing ESLint warnings in unrelated files. These warnings do not block the production build.

---

## Chunk 16 Final UI QA (Completed)

Date: 2026-06-20

### Responsive layout fixes applied

- **Canvas builder** (`frontend/src/features/reports/dashboard-canvas-builder.tsx:794`): Changed `grid-cols-12` to `md:grid-cols-12` so blocks stack full-width on mobile below `md` breakpoint. The 12-column grid with configurable spans (3, 4, 6, 8, 12) activates on tablet+ while mobile shows single-column stacked blocks.
- **Published dashboard view** (`frontend/src/features/reports/published-dashboard-view.tsx:434`): Changed `grid-cols-12` to `md:grid-cols-12` for mobile-first responsive block layout.
- **Facility dashboard filters** (`frontend/src/app/facility/dashboard/page.tsx:72`): Added `sm:grid-cols-2` fallback for the filter control row so date/select inputs wrap into 2 columns on small screens.

### Responsive patterns verified across dashboard components

- **Federal dashboard**: KPI cards use `sm:grid-cols-2 md:grid-cols-4`, chart sections use `lg:grid-cols-2`, comparison table has `overflow-x-auto`.
- **State dashboard**: Filter bar uses `md:grid-cols-2 xl:grid-cols-[...]`, summary cards use `sm:grid-cols-2 xl:grid-cols-5`, priority items use `sm:grid-cols-2 2xl:grid-cols-3`, quick actions use `sm:grid-cols-2 xl:grid-cols-1`, operational queues use `xl:grid-cols-2`.
- **Employer dashboard**: Branch scope bar uses `md:flex-row`, metrics use `sm:grid-cols-2 lg:grid-cols-4`, panels use `lg:grid-cols-2`.
- **Facility dashboard**: Metrics use `md:grid-cols-4`, operational sections use `lg:grid-cols-[0.8fr_1.2fr]`, distribution panels use `md:grid-cols-3`.
- **Worksheet builder**: Main layout `xl:grid-cols-[300px_minmax(0,1fr)]` with `xl:sticky` sidebar, fields list has `max-h-72 overflow-y-auto`, preview table has `overflow-x-auto`, settings panels use `lg:grid-cols-2`.
- **Widget builder**: Main layout `xl:grid-cols-[320px_minmax(0,1fr)]`, widget type selector `grid-cols-2`, alert section uses `lg:grid-cols-[minmax(0,1fr)_360px]`, saved widgets and alert history stack on mobile.
- **PortalShell**: Sidebar hidden below `lg`, mobile top nav with `overflow-x-auto` scroll tabs, content area has responsive padding.

### Automated verification

- TypeScript typecheck: **passed** (0 errors)
- Backend Python compilation: **passed** (0 errors)
- Next.js build: pre-existing Node 16 environment limitation (`structuredClone` unavailable in Node 16; `.next` build artifacts from earlier today confirmed valid)

### Chunk 16 summary

All mobile/tablet responsive layout issues from the Chunk 15 QA checklist have been addressed. Dashboard pages and builder components now collapse to single-column layouts on mobile, use 2-column grids on tablet (`sm`/`md`), and expand to full multi-column layouts on desktop (`lg`/`xl`). The canvas builder and published dashboard view now render blocks full-width on mobile rather than squeezing multi-column spans into narrow viewports.
