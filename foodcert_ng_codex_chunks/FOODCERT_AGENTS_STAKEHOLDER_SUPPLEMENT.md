# FOODCERT_AGENTS_STAKEHOLDER_SUPPLEMENT.md

Add these rules to the root `AGENTS.md`, `backend/AGENTS.md`, and `frontend/AGENTS.md`.

## Multi-Actor Organization Rule

Organizations are not flat. Implement `OrganizationUnit` for directorates, departments, units, branches, LGA offices, lab departments, clinical departments, records departments, and other substructures.

## User Scoping Rule

A user belongs to an organization and may optionally belong to an organization unit. The user's effective access is based on:

```txt
Role + Organization + Unit + unit_restricted flag + explicit permissions
```

## Required Model Updates

- Add `OrganizationUnit`.
- Add `User.unit`.
- Add `User.unit_restricted`.
- Add `UserInvite`.
- Add `FoodHandlerProfile.business_branch`.
- Add `Inspection.branch`.

## Required UX Updates

- Add organization unit management pages.
- Add employer branch management page.
- Add medical facility department management page.
- Add state ministry unit management page.
- Add invite user modal with role and unit selection.
- Add branch/unit filters to dashboards.

## Privacy Reminder

Unit scoping must not weaken medical privacy. Employers and branch managers still must not see diagnosis, lab results, doctor notes, or declaration answers.
