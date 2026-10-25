# User Stories and Acceptance Criteria

Stories are grouped by epic and linked to the business requirements (BR), functional requirements (FR) and findings (F) in the [BRD](01_BRD.md). Points are relative estimates (Fibonacci). Release is R1, R2 or R3 as in the BRD release plan.

| Story | Title | Priority | Points | Release | Requirements | Finding |
|---|---|---|---|---|---|---|
| US-01 | Alternative path at KYC start | Must | 5 | R3 | BR-01; FR-01 | F2 |
| US-02 | Alternative KYC verification with status tracking | Must | 13 | R3 | BR-01; FR-02, FR-03 | F2 |
| US-03 | Signature without Aadhaar OTP | Should | 8 | R3 | BR-01; FR-04 | F2 |
| US-04 | Timeout and UPI fallback for bank verification | Must | 5 | R1 | BR-02; FR-05, FR-07 | F3 |
| US-05 | Cancelled cheque or statement upload | Must | 8 | R1 | BR-02; FR-06 | F3 |
| US-06 | Bank health monitoring | Should | 5 | R1 | BR-02, BR-07; FR-08 | F3 |
| US-07 | Save and resume onboarding | Must | 8 | R1 | BR-03; FR-09 | F4, F9 |
| US-08 | Resume reminders | Must | 8 | R1 | BR-03; FR-10 | F4, F9 |
| US-09 | Continue tomorrow for late-night users | Could | 3 | R1 | BR-03; FR-11 | F4 |
| US-10 | Live camera guidance | Should | 8 | R2 | BR-04; FR-12 | F5 |
| US-11 | Fallback after repeated IPV failures | Should | 5 | R2 | BR-04; FR-13 | F5 |
| US-12 | Move from web to mobile for the selfie | Could | 3 | R2 | BR-04; FR-14 | F5 |
| US-13 | Activate cash segments first | Must | 5 | R2 | BR-05; FR-15 | F6 |
| US-14 | Flexible income-proof options | Should | 5 | R2 | BR-05; FR-16 | F6 |
| US-15 | One-tap UPI funding | Must | 5 | R2 | BR-06; FR-17 | F7 |
| US-16 | Funding nudges | Should | 5 | R2 | BR-06; FR-18 | F7 |
| US-17 | Standard funnel events | Must | 8 | R1 | BR-07; FR-19 | F8 |
| US-18 | Exit reason capture | Must | 3 | R1 | BR-07; FR-20 | F8 |
| US-19 | Daily funnel dashboard and alerts | Must | 5 | R1 | BR-07; FR-21 | F8 |

## Epic E1: Inclusive KYC (BR-01)

### US-01 Alternative path at KYC start
**As an** user whose Aadhaar is not linked to my mobile number, **I want** to be offered another way to verify my identity, **so that** I am not blocked by a dead-end error.

*Priority:* Must | *Points:* 5 | *Release:* R3 | *Requirements:* BR-01; FR-01 | *Finding:* F2

**Acceptance criteria**
1. Given I start KYC and the system detects an Aadhaar-mobile mismatch, When the check completes, Then I see the available alternative paths with expected time for each and no error message that blocks me.
2. Given I choose an alternative path, When I confirm, Then the app records the chosen path and moves me to the matching steps without re-entering my PAN.
3. Given my Aadhaar is linked, When I start KYC, Then I do not see the alternative-path screen.

### US-02 Alternative KYC verification with status tracking
**As an** user on the alternative KYC path, **I want** to submit my documents or complete a video-assisted check and see the status, **so that** I know when my account will be ready.

*Priority:* Must | *Points:* 13 | *Release:* R3 | *Requirements:* BR-01; FR-02, FR-03 | *Finding:* F2

**Acceptance criteria**
1. Given I am on the alternative path, When I upload my documents or join the assisted check, Then my submission is accepted in a format Compliance has approved.
2. Given I have submitted, When I open the app, Then I see a status tracker (submitted, under review, approved or action needed) with the expected turnaround.
3. Given my documents are rejected, When the reviewer marks them, Then I see the exact reason and can resubmit only the failed item.

### US-03 Signature without Aadhaar OTP
**As an** user who cannot use Aadhaar OTP e-Sign, **I want** to sign my account-opening form using an approved alternative, **so that** I do not have to print and courier documents.

*Priority:* Should | *Points:* 8 | *Release:* R3 | *Requirements:* BR-01; FR-04 | *Finding:* F2

**Acceptance criteria**
1. Given I cannot receive the Aadhaar OTP, When I reach the signature step, Then I see the signature options approved by Compliance.
2. Given I complete the alternative signature, When it is validated, Then my application moves to approval and I see the expected approval time.
3. Given I choose a courier-based option, When I place the request, Then I can track the document and the app reminds me if it has not been received after 5 days.

## Epic E2: Resilient bank verification (BR-02)

### US-04 Timeout and UPI fallback for bank verification
**As an** user adding my bank account, **I want** to be offered UPI-based verification if the check takes too long or fails, **so that** a slow bank does not stop me.

*Priority:* Must | *Points:* 5 | *Release:* R1 | *Requirements:* BR-02; FR-05, FR-07 | *Finding:* F3

**Acceptance criteria**
1. Given the bank verification has not returned within 60 seconds, When the timer expires, Then I am offered UPI-based verification and can continue without re-entering my account number.
2. Given I complete UPI verification, When the payment is confirmed, Then my bank is marked verified and I move to the next step.
3. Given verification takes longer than usual, When I am waiting, Then I see an expected-time message instead of a spinner with no information.

### US-05 Cancelled cheque or statement upload
**As an** user whose bank cannot be verified instantly, **I want** to upload a cancelled cheque or bank statement, **so that** I can still link my account.

*Priority:* Must | *Points:* 8 | *Release:* R1 | *Requirements:* BR-02; FR-06 | *Finding:* F3

**Acceptance criteria**
1. Given I upload a cancelled cheque, When the name, account number and IFSC are extracted and the name matches my PAN name, Then my bank is verified automatically.
2. Given the extracted name does not match, When the check completes, Then my case goes to the manual review queue and I see that review takes up to a stated time.
3. Given the image is unreadable, When the upload is processed, Then I get a specific tip (for example 'avoid glare') and can retake it.

### US-06 Bank health monitoring
**As an** operations analyst, **I want** to see penny-drop success rate and latency by bank and get alerts, **so that** I can react when a bank degrades.

*Priority:* Should | *Points:* 5 | *Release:* R1 | *Requirements:* BR-02, BR-07; FR-08 | *Finding:* F3

**Acceptance criteria**
1. Given a bank's success rate falls 10 points below its 7-day average, When the hourly check runs, Then an alert is sent to the operations channel.
2. Given I open the monitoring view, When I filter by bank, Then I see volume, success rate and p50 / p95 latency for the last 24 hours and 7 days.

## Epic E3: Save, resume and re-engage (BR-03)

### US-07 Save and resume onboarding
**As an** user who leaves in the middle of onboarding, **I want** to come back later and continue from where I stopped, **so that** I do not have to start again.

*Priority:* Must | *Points:* 8 | *Release:* R1 | *Requirements:* BR-03; FR-09 | *Finding:* F4, F9

**Acceptance criteria**
1. Given I complete a step, When I close the app, Then my entered data is saved on the server.
2. Given I return and log in with OTP on any device, When I open onboarding, Then I land on the first incomplete step with earlier data pre-filled.
3. Given my KYC data has expired or changed, When I resume, Then only the affected step is re-requested.

### US-08 Resume reminders
**As an** user who stopped onboarding, **I want** to get a timely reminder with a link back, **so that** I finish my account.

*Priority:* Must | *Points:* 8 | *Release:* R1 | *Requirements:* BR-03; FR-10 | *Finding:* F4, F9

**Acceptance criteria**
1. Given I have consented to messages and have not progressed, When 30 minutes, 24 hours and 72 hours pass, Then I receive at most one reminder at each point with a deep link to my next step.
2. Given I complete the next step, When a reminder is queued, Then it is cancelled.
3. Given I opted out, When I abandon onboarding, Then I receive no reminders on that channel.

### US-09 Continue tomorrow for late-night users
**As an** user starting KYC late at night, **I want** to schedule a reminder for the next morning, **so that** I finish when I am ready.

*Priority:* Could | *Points:* 3 | *Release:* R1 | *Requirements:* BR-03; FR-11 | *Finding:* F4

**Acceptance criteria**
1. Given I start KYC between 22:00 and 05:59, When I reach the KYC screen, Then I am offered 'Continue tomorrow' with a time I can choose.
2. Given I schedule a time, When that time arrives, Then I receive one reminder with a deep link to KYC.

## Epic E4: Assisted selfie / IPV (BR-04)

### US-10 Live camera guidance
**As an** user taking my selfie, **I want** to get instant guidance on light and position, **so that** my first attempt succeeds.

*Priority:* Should | *Points:* 8 | *Release:* R2 | *Requirements:* BR-04; FR-12 | *Finding:* F5

**Acceptance criteria**
1. Given the lighting is too low, When the camera opens, Then I see a clear prompt to move to better light before capture.
2. Given my face is centred and well lit, When the conditions are met, Then the app captures automatically.
3. Given I use a low-end device, When the camera opens, Then the guidance still responds within 1 second.

### US-11 Fallback after repeated IPV failures
**As an** user whose selfie check keeps failing, **I want** to be offered another option after two failures, **so that** I am not stuck in a loop.

*Priority:* Should | *Points:* 5 | *Release:* R2 | *Requirements:* BR-04; FR-13 | *Finding:* F5

**Acceptance criteria**
1. Given two attempts have failed, When I try a third time, Then I am offered 'retry later' with a reminder link or an assisted video session.
2. Given I choose 'retry later', When I return through the link, Then I resume at the selfie step.

### US-12 Move from web to mobile for the selfie
**As a** web user without a usable camera, **I want** to continue on my phone by scanning a QR code, **so that** I can complete the selfie step.

*Priority:* Could | *Points:* 3 | *Release:* R2 | *Requirements:* BR-04; FR-14 | *Finding:* F5

**Acceptance criteria**
1. Given I reach the selfie step on web, When I choose 'use my phone', Then a QR code opens the app at the selfie step with my session.
2. Given I finish on my phone, When I return to web, Then the web page shows the next step.

## Epic E5: Income proof without blocking (BR-05)

### US-13 Activate cash segments first
**As an** user who wants F&O but has no income proof yet, **I want** to open my account for cash and delivery trading and add income proof later, **so that** I can start now.

*Priority:* Must | *Points:* 5 | *Release:* R2 | *Requirements:* BR-05; FR-15 | *Finding:* F6

**Acceptance criteria**
1. Given I select F&O and skip income proof, When I submit, Then my account is created with cash and delivery segments only.
2. Given I later request F&O, When I open the request, Then I am asked for income proof and the segment is enabled only after approval.

### US-14 Flexible income-proof options
**As an** user adding income proof, **I want** to choose from several proof types, **so that** I can use what I have.

*Priority:* Should | *Points:* 5 | *Release:* R2 | *Requirements:* BR-05; FR-16 | *Finding:* F6

**Acceptance criteria**
1. Given I open income proof, When I view the options, Then I see all accepted types with a one-line explanation of each.
2. Given I upload a document, When it is checked, Then I see accepted or the exact reason it was rejected.

## Epic E6: First funding (BR-06)

### US-15 One-tap UPI funding
**As a** newly activated user, **I want** to add money with one tap using a pre-filled amount, **so that** I can start trading.

*Priority:* Must | *Points:* 5 | *Release:* R2 | *Requirements:* BR-06; FR-17 | *Finding:* F7

**Acceptance criteria**
1. Given my account is activated, When I open the funding screen, Then I see a suggested amount and a button that opens my UPI app.
2. Given my UPI payment fails, When I return, Then I see the reason and can retry or choose another method in one tap.
3. Given the payment succeeds, When I return, Then my balance updates within 1 minute.

### US-16 Funding nudges
**As an** activated user who has not funded, **I want** to get a helpful reminder, **so that** I remember to fund.

*Priority:* Should | *Points:* 5 | *Release:* R2 | *Requirements:* BR-06; FR-18 | *Finding:* F7

**Acceptance criteria**
1. Given I am activated and unfunded, When 1, 3 and 7 days pass, Then I receive at most one nudge per point.
2. Given I fund my account, When a nudge is queued, Then it is cancelled.
3. Given I have received 3 nudges, When more days pass, Then I receive no more.

## Epic E7: Measurement (BR-07)

### US-17 Standard funnel events
**As a** data analyst, **I want** to receive a consistent event for every stage, **so that** I can measure conversion, latency and failures.

*Priority:* Must | *Points:* 8 | *Release:* R1 | *Requirements:* BR-07; FR-19 | *Finding:* F8

**Acceptance criteria**
1. Given a user enters, completes or fails a stage, When the action happens, Then an event is emitted with user id, stage, timestamp, attempt number, latency and reason code if failed.
2. Given events are delivered, When I check completeness, Then at least 99% arrive within 5 minutes.

### US-18 Exit reason capture
**As a** product manager, **I want** to know why users abandon, **so that** I can fix the right problem.

*Priority:* Must | *Points:* 3 | *Release:* R1 | *Requirements:* BR-07; FR-20 | *Finding:* F8

**Acceptance criteria**
1. Given a user leaves a key step, When they return or press back, Then they see a one-question prompt with 5 options and 'Other'.
2. Given the user skips the prompt, When they continue, Then the flow is not blocked.

### US-19 Daily funnel dashboard and alerts
**As a** head of digital products, **I want** to see funnel health every day and get alerts, **so that** problems are fixed in days, not months.

*Priority:* Must | *Points:* 5 | *Release:* R1 | *Requirements:* BR-07; FR-21 | *Finding:* F8

**Acceptance criteria**
1. Given yesterday's data, When the dashboard refreshes, Then I see step conversion by channel, device, city tier and KYC path.
2. Given a step conversion falls more than 3 points below its 4-week average, When the daily check runs, Then an alert is sent to the product channel.

---
**Total:** 19 stories, 115 points.