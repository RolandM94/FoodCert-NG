# Chunk 03 — Identity, Food Handlers, Employers, and NIN Verification

## Goal

Implement food handler profiles, employer profiles, and automatic NIN verification.

## Food Handler Profile

Required fields:

```txt
full_name
date_of_birth
gender
NIN
passport_photo
phone
email
nationality
home_address
state_of_domicile
LGA
ward
employer
work_location
food_handler_category
emergency_contact
system_identifier
current_status
```

## Food Handler Categories

- Kitchen staff
- Food preparers
- Serving and catering staff
- Food packers
- Bakery workers
- Food processing operators
- Bartenders
- Dishwashers
- Food delivery personnel
- Food stall and street food vendors
- Food storage handlers
- Concession stand workers
- Airline catering vendors
- Train catering vendors
- Cruise ship/sea vessel catering vendors
- Livestock farmers, butchers, meat cutters
- Emergency situation food workers

## Employer / Food Business Profile

Required fields:

```txt
business_name
business_registration_number
establishment_category
contact_person_name
contact_person_phone
contact_person_email
address
state
LGA
ward
number_of_food_handlers
compliance_status
subscription_status
```

## Establishment Categories

- Restaurants and cafes
- Bakeries and pastry shops
- Abattoirs, slaughter slabs, and butcher shops
- Grocery stores and supermarkets
- Food trucks and street vendors
- Catering services
- School cafeterias
- Hospital kitchens
- Bars and pubs
- Food processing plants
- Hotels and resorts
- Corporate dining facilities
- Food markets and stalls
- Airport and train station food outlets
- Farms and livestock feed processing plants
- Daycare centres

## NIN Verification Workflow

1. Food handler enters NIN.
2. System calls NIN provider abstraction.
3. System retrieves verified identity data.
4. System compares:
   - full name
   - date of birth
   - gender
   - photo, if available
5. If match is acceptable, mark NIN as verified.
6. If mismatch, mark as manual review required.
7. State Ministry Admin or authorized regulator can approve override.
8. Certificate issuance must be blocked until NIN is verified or override is approved.

## NIN Statuses

```txt
not_submitted
pending_verification
verified
failed
mismatch
manual_review_required
override_approved
```

## Privacy Requirements

- Store NIN securely.
- Never show full NIN publicly.
- Public verification should show no NIN or masked NIN.
- Employers should not see full NIN unless policy allows.

## Models

```python
class FoodHandlerProfile(models.Model):
    id = UUIDField(primary_key=True)
    user = OneToOneField(User)
    full_name = CharField()
    date_of_birth = DateField()
    gender = CharField()
    nin = CharField()
    passport_photo = FileField()
    nationality = CharField()
    phone = CharField()
    email = EmailField()
    home_address = TextField()
    state = ForeignKey(State)
    lga = ForeignKey(LGA)
    ward = CharField(blank=True)
    employer = ForeignKey(Employer, null=True, blank=True)
    food_handler_category = CharField()
    system_identifier = CharField(unique=True)
    current_status = CharField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

```python
class NINVerification(models.Model):
    id = UUIDField(primary_key=True)
    food_handler = ForeignKey(FoodHandlerProfile)
    nin = CharField()
    provider = CharField()
    provider_reference = CharField(blank=True)
    status = CharField()
    verified_full_name = CharField(blank=True)
    verified_date_of_birth = DateField(null=True)
    verified_gender = CharField(blank=True)
    verified_photo_url = URLField(blank=True)
    match_score = DecimalField()
    mismatch_fields = JSONField(default=dict)
    verified_at = DateTimeField(null=True)
    reviewed_by = ForeignKey(User, null=True, blank=True)
    review_notes = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## API Endpoints

```txt
POST /api/food-handlers
GET  /api/food-handlers
GET  /api/food-handlers/:id
PATCH /api/food-handlers/:id

POST /api/employers
GET  /api/employers
GET  /api/employers/:id
PATCH /api/employers/:id

POST /api/food-handlers/:id/verify-nin
GET  /api/food-handlers/:id/nin-verification
PATCH /api/nin-verifications/:id/approve-override
PATCH /api/nin-verifications/:id/reject-override
```

## Acceptance Criteria

- Food handler can create and update profile.
- Employer can create and update business profile.
- Employer can add or invite food handlers.
- NIN verification is required before certificate issuance.
- NIN mismatch blocks certificate issuance pending review.
- Public verification never exposes full NIN.
