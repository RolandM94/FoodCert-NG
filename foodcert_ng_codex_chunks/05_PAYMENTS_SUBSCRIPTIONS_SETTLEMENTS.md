# Chunk 05 — Payments, Employer Subscriptions, and Facility Settlements

## Goal

Implement platform payments for:
1. Food handler assessment fees.
2. Employer subscription fees.
3. Settlement payouts to medical facilities.
4. State and platform fee reporting.

## Payment Provider Abstraction

Implement a provider interface that supports mock payment first, then Paystack/Flutterwave/Remita.

```python
class PaymentProvider:
    def initialize_payment(self, amount, email, reference, metadata): ...
    def verify_payment(self, reference): ...
    def refund_payment(self, reference, amount=None): ...
```

## Assessment Payment Flow

1. Food handler selects approved facility.
2. System gets active AssessmentFee for the state/facility type.
3. Food handler pays through platform.
4. Payment provider confirms payment.
5. Appointment/assessment is activated.
6. Receipt is generated.
7. Payment is linked to assessment.
8. After completed assessment and State validation, facility settlement becomes eligible.

## Assessment Fee Model

```python
class AssessmentFee(models.Model):
    id = UUIDField(primary_key=True)
    state = ForeignKey(State)
    facility_type = CharField()
    amount = DecimalField()
    currency = CharField(default="NGN")
    state_fee = DecimalField(default=0)
    facility_fee = DecimalField(default=0)
    platform_fee = DecimalField(default=0)
    effective_from = DateField()
    effective_to = DateField(null=True, blank=True)
    status = CharField(choices=["active", "inactive"])
    created_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## PaymentTransaction Model

```python
class PaymentTransaction(models.Model):
    id = UUIDField(primary_key=True)
    payer_user = ForeignKey(User)
    payer_type = CharField()
    related_entity_type = CharField()
    related_entity_id = UUIDField()
    amount = DecimalField()
    currency = CharField(default="NGN")
    payment_provider = CharField()
    provider_reference = CharField()
    internal_reference = CharField(unique=True)
    status = CharField()
    paid_at = DateTimeField(null=True)
    metadata = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Employer Subscription

Plans:
- Basic
- Standard
- Enterprise

Subscription may be based on:
- Maximum food handlers
- Number of locations
- Advanced reporting access
- API access
- Dedicated support

## Subscription Models

```python
class EmployerSubscriptionPlan(models.Model):
    id = UUIDField(primary_key=True)
    name = CharField()
    description = TextField()
    max_food_handlers = IntegerField()
    max_locations = IntegerField()
    price_monthly = DecimalField()
    price_yearly = DecimalField()
    features = JSONField(default=dict)
    status = CharField(choices=["active", "inactive"])
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

```python
class EmployerSubscription(models.Model):
    id = UUIDField(primary_key=True)
    employer = ForeignKey(Employer)
    plan = ForeignKey(EmployerSubscriptionPlan)
    billing_cycle = CharField(choices=["monthly", "yearly"])
    status = CharField()
    starts_at = DateTimeField()
    expires_at = DateTimeField()
    cancelled_at = DateTimeField(null=True, blank=True)
    last_payment_transaction = ForeignKey(PaymentTransaction, null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Employer Subscription Rules

If subscription is expired:
- Employer can view existing records.
- Employer cannot add new food handlers above free/basic limit.
- Employer cannot generate premium reports.
- Regulatory notices remain visible.
- Regulators can still inspect employer records.

## Facility Settlement

Settlement should be eligible only after:
- Payment is successful.
- Assessment is completed.
- Doctor decision is submitted.
- State validation is completed.
- Certificate or not-fit report is issued.

## Settlement Model

```python
class Settlement(models.Model):
    id = UUIDField(primary_key=True)
    facility = ForeignKey(MedicalFacility)
    state = ForeignKey(State)
    payment_transaction = ForeignKey(PaymentTransaction)
    assessment = ForeignKey(MedicalAssessment)
    gross_amount = DecimalField()
    facility_amount = DecimalField()
    state_amount = DecimalField()
    platform_amount = DecimalField()
    settlement_status = CharField()
    settlement_reference = CharField(blank=True)
    settled_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## API Endpoints

```txt
POST /api/payments/assessment/initiate
POST /api/payments/subscription/initiate
GET  /api/payments/verify/:reference
POST /api/payments/webhook

GET  /api/assessment-fees
POST /api/assessment-fees
PATCH /api/assessment-fees/:id

GET  /api/subscription-plans
POST /api/subscription-plans
POST /api/employers/:id/subscribe
GET  /api/employers/:id/subscription

GET  /api/settlements
POST /api/settlements/:id/process
GET  /api/facilities/:id/settlements
```

## Acceptance Criteria

- Food handler must pay before assessment activation.
- Failed payment blocks assessment.
- Employer can subscribe to a plan.
- Expired employer subscription restricts premium actions.
- Facility settlement is created after valid completed assessment.
- All payments and settlements are auditable.
