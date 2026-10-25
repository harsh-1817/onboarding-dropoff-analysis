# UAT Test Plan

**Scope:** acceptance tests for the stories in [`02_user_stories.md`](02_user_stories.md) and the non-functional requirements in the [BRD](01_BRD.md).
**Environment:** staging with test KYC and bank sandboxes; time-shifting available for reminder tests.
**Entry criteria:** build deployed to staging, test data ready, Compliance has approved the alternative-path content.
**Exit criteria:** all High tests pass, no open Severity 1 or 2 defects, Medium and Low tests pass or have an agreed workaround, business sign-off recorded.

| ID | Story / NFR | Scenario | Precondition | Steps | Expected result | Priority |
|---|---|---|---|---|---|---|
| TC-01 | US-01 | User with unlinked Aadhaar sees alternative path | Test user whose Aadhaar is not linked to the mobile | Start KYC and enter PAN | Alternative-path options with expected time are shown; no blocking error | High |
| TC-02 | US-01 | Linked user does not see the alternative screen | Test user with linked Aadhaar | Start KYC | Normal DigiLocker flow is shown | High |
| TC-03 | US-02 | Alternative documents accepted | User on alternative path | Upload approved documents | Submission accepted; tracker shows 'submitted' | High |
| TC-04 | US-02 | Rejected document gives specific reason | Submitted case | Reviewer rejects one document | User sees the exact reason and can resubmit only that item | High |
| TC-05 | US-03 | Alternative signature completes | User who cannot use Aadhaar OTP | Choose an approved signature option and complete it | Application moves to approval; expected time shown | Medium |
| TC-06 | US-04 | Timeout triggers UPI fallback | Penny-drop simulated to take 70 s | Wait on the bank screen | At 60 s the app offers UPI verification and keeps the account number | High |
| TC-07 | US-04 | UPI verification succeeds | Fallback offered | Pay via UPI | Bank marked verified; next step opens | High |
| TC-08 | US-05 | Cheque upload verifies automatically | Cheque with name matching PAN | Upload cheque | Fields extracted; bank verified without manual review | High |
| TC-09 | US-05 | Name mismatch goes to review | Cheque with different name | Upload cheque | Case enters review queue; user told the expected time | High |
| TC-10 | US-07 | Resume after closing the app | User stopped after bank step | Close and reopen the app | User lands on the next incomplete step with data pre-filled | High |
| TC-11 | US-07 | Resume on a different device | User stopped on phone A | Log in with OTP on phone B | Progress is available and resumes at the right step | High |
| TC-12 | US-08 | Reminder sent only with consent | Consenting and non-consenting users abandon | Wait 30 min, 24 h, 72 h (time-shifted) | Only the consenting user receives reminders; max one per point | High |
| TC-13 | US-08 | Reminder cancelled after progress | Reminder queued | User completes the next step | Queued reminder is cancelled | Medium |
| TC-14 | US-09 | Continue-tomorrow scheduling | Sign-up at 23:30 | Reach KYC and choose 9:00 tomorrow | One reminder with deep link arrives at 9:00 | Low |
| TC-15 | US-10 | Low-light guidance and auto-capture | Low-end Android device in a dark room | Open selfie step, then move to light | Prompt appears in the dark; auto-capture when light is good | High |
| TC-16 | US-11 | Fallback after two failures | Two failed attempts | Attempt a third time | Retry-later link or assisted video is offered | Medium |
| TC-17 | US-12 | Web to mobile hand-off | Web user at selfie step | Choose 'use my phone' and scan the QR | App opens at the selfie step with the same session | Low |
| TC-18 | US-13 | Cash segments without income proof | User selects F&O and skips proof | Submit | Account created with cash and delivery only | High |
| TC-19 | US-13 | F&O requested later needs proof | Account without F&O | Request F&O | Income proof requested; segment enabled only after approval | High |
| TC-20 | US-14 | Multiple proof types accepted | F&O request open | Upload each accepted proof type | Each valid type is accepted; invalid shows a reason | Medium |
| TC-21 | US-15 | One-tap UPI funding | Activated account | Open funding screen and tap pay | Suggested amount pre-filled; UPI app opens | High |
| TC-22 | US-15 | Failed UPI payment recovery | Payment fails | Return to the app | Reason shown; retry or other method in one tap | High |
| TC-23 | US-16 | Nudge frequency cap | Activated, unfunded user | Advance 10 days | At most 3 nudges (day 1, 3, 7); none after funding | Medium |
| TC-24 | US-17 | Event completeness | Run 100 test onboardings | Check the event stream | Every stage has an event with all required fields; 99% within 5 minutes | High |
| TC-25 | US-18 | Exit prompt shown and skippable | User presses back on KYC | View prompt, then skip | Prompt shown with 5 options and 'Other'; skipping does not block | Medium |
| TC-26 | US-19 | Alert on conversion drop | Inject a 4-point KYC drop in test data | Run the daily check | Alert is sent to the product channel | Medium |
| TC-27 | NFR-01 | Response time | Load test at expected peak | Measure screen response | p95 below 2 seconds; external calls time out at 60 seconds | High |
| TC-28 | NFR-03 | PII masked in logs | Completed onboarding | Inspect application logs | PAN, Aadhaar and bank numbers are masked | High |
| TC-29 | NFR-05 | Opt-out honoured | User opts out of reminders | Abandon onboarding | No reminders within 24 hours of opt-out and after | High |
| TC-30 | NFR-06 | Low-end device usability | Low-RAM Android device | Complete onboarding end to end | All steps usable; no crash or freeze | High |

**Total:** 30 test cases (21 High, 7 Medium, 2 Low).

## Defect severity
| Severity | Definition |
|---|---|
| 1 | Blocks onboarding or breaks compliance; release stopped |
| 2 | Major step fails for a segment; fix before release |
| 3 | Minor issue with a workaround | 
| 4 | Cosmetic |