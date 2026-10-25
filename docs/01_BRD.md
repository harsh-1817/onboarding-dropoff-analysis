# Business Requirements Document: Digital Account Opening Improvement

| | |
|---|---|
| **Document** | Business Requirements Document (BRD) |
| **Version / status** | 1.0 / Draft for stakeholder review |
| **Author** | Harsh Trivedi, Business Analyst |
| **Date** | 22 October 2026 |
| **Data note** | All figures come from a **synthetic** dataset built for this case study (see `src/generate_dataset.py`). The company, volumes and revenue figures are illustrative. |

---

## 1. Executive summary
Between 1 April and 31 August 2026, **20,000 people started opening a trading account** on the (fictional) broker's app and website. Only **5,964 (29.8%)** ended with an approved account, **3,462 (17.3%)** deposited money and **2,428 (12.1%)** placed a first trade.

Three steps explain most of the loss: **KYC (5,385 users lost), bank verification (2,515) and first funding (2,502)**. Together they account for **59.2%** of all 17,572 drop-offs. The causes are concentrated, not random:
- users whose Aadhaar is not linked to their mobile convert at **33.3%** at KYC against **75.2%** for everyone else,
- bank verification completes for only **56.7%** of users when the bank response takes over five minutes (against **86.3%** when it takes under 30 seconds),
- **36.8%** of all drop-offs have no recorded reason, so the business is partly blind.

This BRD proposes seven improvements, prioritised with a transparent model (`excel/Onboarding_Impact_Model.xlsx`). In the **base scenario** they add about **77 funded accounts per month (+11.1%)**, worth about **Rs 18.5 lakh** in first-year revenue using a placeholder revenue-per-account assumption. The conservative and optimistic scenarios give +5.6% and +16.7%.

## 2. Business problem and objectives
**Problem:** most people who start opening an account never fund or trade, so acquisition spend is wasted and revenue is lost.

| # | Objective (SMART) | Baseline | Target |
|---|---|---|---|
| O1 | Raise the share of sign-ups that become **funded** accounts within two quarters of release | 17.3% | 19.3% |
| O2 | Raise sign-up to **activation** | 29.8% | 32.7% |
| O3 | Capture a reason for drop-offs, so decisions rest on evidence | 36.8% unknown | under 15% unknown |
| O4 | Shorten the time to activate | median 40 h | 30 h or less |
| O5 | Close the gap for offline-KYC users | 12.4% activation | 20% or more |

## 3. Scope
| In scope | Out of scope |
|---|---|
| Mobile app and web account-opening flow (registration to first funding) | Trading-platform features after the first trade |
| Alternative KYC and signature paths for users who cannot use Aadhaar OTP | Brokerage pricing and offers (other than a funding nudge) |
| Bank-account verification, selfie / IPV, income-proof capture | Replacing the KRA or back-office KYC systems |
| Save-and-resume and re-engagement journeys | Changing the acquisition channel mix or ad spend |
| Funnel instrumentation, exit-reason capture and monitoring | Changes to regulation or exchange rules |

## 4. Stakeholders (RACI)
R = responsible, A = accountable, C = consulted, I = informed.

| Stakeholder | Role in this initiative | Requirements | Design | Build | Compliance sign-off | Launch |
|---|---|---|---|---|---|---|
| Head of Digital Products | Sponsor, owns funnel KPIs | A | A | I | I | A |
| Business Analyst (author) | Requirements, analysis, UAT coordination | R | C | C | C | R |
| Product Manager, Onboarding | Roadmap and backlog | R | R | C | I | R |
| Compliance / KYC officer | Approves every KYC variant | C | C | I | A / R | C |
| Back-office KYC operations | Reviews documents, handles rejections | C | C | I | C | C |
| Engineering lead | Estimates and delivers | C | C | A / R | I | C |
| UX designer | Flows and screens | C | R | I | I | I |
| Marketing / acquisition | Channel quality, nudge content | C | I | I | I | C |
| Customer support | Assisted onboarding, feedback | C | C | I | I | C |
| Data and analytics | Events, dashboard, A/B analysis | C | I | R | I | C |

## 5. Current state and evidence
The current flow has ten stages; the full as-is and to-be diagrams are in [`03_process_flows.md`](03_process_flows.md). The evidence below comes from the funnel analysis (`docs/key_findings.md`, `sql/analysis_queries.sql`).

| ID | Finding | Evidence |
|---|---|---|
| F1 | **KYC is the largest leak** | 5,385 users lost (26.9% of all sign-ups); step conversion 70.1% |
| F2 | **Users whose Aadhaar is not linked to their mobile are stuck** | KYC conversion 33.3% vs 75.2%; they are 12.0% of sign-ups (2,410 users) and activate at 12.4% vs 32.2%; they also fail more at e-Sign (76.7% vs 90.5%) and take a median 71 h to activate vs 39 h |
| F3 | **Bank verification fails for some banks and when it is slow** | Co-operative / other banks 63.6% and PNB 68.5% vs HDFC Bank 88.0%; completion 56.7% when the bank response takes over 5 minutes (1,052 users) vs 86.3% under 30 seconds |
| F4 | **Late-night starters do not come back** | KYC conversion 61.9% for sign-ups between 22:00 and 05:59 vs 71.7% in the morning |
| F5 | **Selfie / IPV fails on weaker devices** | Completion 79.6% on low-end Android and 83.9% on web vs 91.4% on iOS |
| F6 | **F&O seekers drop at income proof** | 83.1% step conversion vs 93.6% for cash-only users |
| F7 | **First funding is the second-biggest leak** | 2,502 users lost; step conversion 58.0%; referral users fund at 67.7% vs 50.1% for influencer-sourced users |
| F8 | **The business cannot explain a third of its drop-offs** | 36.8% of drop-offs carry no reason |
| F9 | **Activation is slow** | Median 40 h from sign-up to activation; only 27.6% activate within 24 h |

*Analytical caution:* conversion at later stages is affected by survivorship. For example, 55+ users who reach bank verification convert better than average because the weaker ones have already dropped at KYC. Segment decisions therefore use the stage where the problem arises, and sizing compares like-for-like benchmarks.

## 6. Proposed solution and prioritisation
| Lever | Opportunity | Stage | Excess users lost vs benchmark | Base-case extra funded accounts / month | Effort (person-weeks, estimate) | Confidence (estimate) | Rank |
|---|---|---|---|---|---|---|---|
| L1a | Alternative KYC path for users whose Aadhaar is not linked to their mobile (KYC stage) | KYC | 920 | 25.2 | 12 | 70% | 4 |
| L1b | Offline-KYC users blocked at e-Sign (signature step) | e-Sign | 62 | 3.3 | 4 | 60% | 7 |
| L2 | Bank-verification fallback (UPI / cancelled-cheque upload) for problem banks | Bank | 733 | 25.0 | 6 | 70% | 1 |
| L3 | Save-and-resume with reminders for late-night KYC starters | KYC | 150 | 4.1 | 3 | 50% | 6 |
| L4 | Assisted selfie / IPV capture for low-end Android, web and 55+ users | Selfie/IPV | 230 | 11.1 | 5 | 60% | 5 |
| L5 | First-funding nudges (one-tap UPI, starter offer) for paid-social/influencer users | Funding | 157 | 15.7 | 3 | 40% | 2 |
| L6 | Simplified income-proof upload for F&O seekers | Segments | 286 | 11.8 | 4 | 60% | 3 |

*Excess users lost* = segment users x (benchmark conversion - segment conversion). The base case assumes the fix closes **half** of that gap, and recovered users must still pass the remaining stages before they fund. Effort, confidence and revenue per account are **placeholders** to be replaced with engineering and finance estimates; the ranking can change when they do.

**Reading the ranking.** L1a has by far the biggest conversion gap (42 points) but ranks below L2 because it needs more effort and its recovered users still face e-Sign, approval and funding. This is why the roadmap uses a score, not the size of the gap alone.

## 7. Requirements

### 7.1 Business requirements
| ID | Requirement | Finding |
|---|---|---|
| BR-01 | Provide a compliant alternative identity-verification and signature path for users whose Aadhaar is not linked to their mobile number | F2 |
| BR-02 | Make bank verification resilient to slow or failed responses and unsupported banks | F3 |
| BR-03 | Let users pause and resume onboarding without losing data, and re-engage those who stop | F4, F9 |
| BR-04 | Reduce selfie / IPV failures on low-end devices and web | F5 |
| BR-05 | Let F&O seekers start in cash segments before income proof is complete | F6 |
| BR-06 | Convert activated users to first funding with a low-friction payment flow and timely nudges | F7 |
| BR-07 | Capture the reason for every drop-off and monitor funnel health daily | F8 |

### 7.2 Functional requirements
| ID | Requirement | BR |
|---|---|---|
| FR-01 | At KYC start, detect an Aadhaar-mobile mismatch and show the alternative-path options instead of a dead-end error | BR-01 |
| FR-02 | Support the alternative KYC method(s) approved by Compliance (for example offline paperless KYC file upload or video-assisted verification) | BR-01 |
| FR-03 | Show users on the alternative path a status tracker with the expected turnaround | BR-01 |
| FR-04 | Offer a signature method for users who cannot use Aadhaar OTP e-Sign, as approved by Compliance, with a turnaround target (replacing courier-only where permitted) | BR-01 |
| FR-05 | Time out the bank penny-drop check after 60 seconds and offer UPI-based verification | BR-02 |
| FR-06 | Allow cancelled-cheque or bank-statement upload with automatic extraction of name, account number and IFSC, and a manual review queue for mismatches | BR-02 |
| FR-07 | Show the expected verification time and bank-specific guidance on the bank screen | BR-02 |
| FR-08 | Track penny-drop latency and success rate by bank and alert operations when a bank breaches its threshold | BR-02, BR-07 |
| FR-09 | Save data on the server after every step and let users resume from the last completed step on any device after OTP login | BR-03 |
| FR-10 | Send resume reminders by push, SMS or WhatsApp (only with consent) at about 30 minutes, 24 hours and 72 hours after abandonment, with a deep link | BR-03 |
| FR-11 | When a user starts KYC between 22:00 and 05:59, offer "Continue tomorrow" with a scheduled reminder | BR-03 |
| FR-12 | Give live camera guidance (light, face position) and auto-capture when conditions are good | BR-04 |
| FR-13 | After two failed IPV attempts, offer a retry-later link or assisted video instead of looping | BR-04 |
| FR-14 | For web users, offer a QR hand-off to the mobile app for the selfie step | BR-04 |
| FR-15 | Allow activation of cash and delivery segments without income proof, and request proof when F&O is enabled | BR-05 |
| FR-16 | Accept multiple income-proof types and let users add them later from the app | BR-05 |
| FR-17 | On the funding screen, offer one-tap UPI with a pre-filled amount and a clear retry path for UPI failures | BR-06 |
| FR-18 | Run a frequency-capped nudge journey (day 1, 3 and 7) for activated, unfunded users | BR-06 |
| FR-19 | Emit standard funnel events: stage entered, stage completed, stage failed with reason code, latency and attempt number | BR-07 |
| FR-20 | Show a one-question "What stopped you?" prompt on abandonment from key steps | BR-07 |
| FR-21 | Provide a daily funnel dashboard and alert when any step conversion falls more than 3 points below its 4-week average | BR-07 |

### 7.3 Non-functional requirements
| ID | Requirement |
|---|---|
| NFR-01 | Performance: screen response p95 under 2 seconds; every external verification call has a hard timeout of 60 seconds |
| NFR-02 | Availability: onboarding APIs available at least 99.5% during market hours (assumption to confirm with engineering) |
| NFR-03 | Security: personal data encrypted in transit and at rest, masked in logs, role-based access |
| NFR-04 | Compliance: every KYC and signature variant approved by Compliance before release; audit trail retained as the regulations require |
| NFR-05 | Privacy and consent: reminders only with consent, opt-out honoured within 24 hours, in line with applicable data-protection law |
| NFR-06 | Device support: works on low-RAM Android devices and the main browsers; key screens available in Hindi and English (assumption) |
| NFR-07 | Observability: funnel events arrive within 5 minutes and at least 99% are complete |
| NFR-08 | Usability: at least 90% of test participants complete each redesigned step without help |

## 8. Success metrics
Targets are the **base scenario** (each fix closes half of its conversion gap, less a 20% overlap haircut because the levers reach overlapping users) and must be validated through the A/B tests in [`06_ab_test_plan.md`](06_ab_test_plan.md).

| KPI | Baseline | Target | Source |
|---|---|---|---|
| Sign-up to account activation | 29.8% | 32.7% | Funnel dashboard |
| Sign-up to first funding | 17.3% | 19.3% | Funnel dashboard |
| KYC step conversion | 70.1% | 72.5% | Stage events |
| Bank-verification step conversion | 80.1% | 82.4% | Stage events |
| Segments / income-proof step conversion | 90.5% | 91.7% | Stage events |
| Selfie / IPV step conversion | 85.4% | 86.5% | Stage events |
| e-Sign step conversion | 89.6% | 90.0% | Stage events |
| First-funding step conversion | 58.0% | 59.1% | Stage events |
| Share of drop-offs with no reason captured | 36.8% | under 15% | Exit-reason events |
| Median hours from sign-up to activation | 40 h | 30 h or less | Stage timestamps |
| Activation rate of offline-KYC users | 12.4% | 20% or more | Funnel dashboard, segment view |

## 9. Assumptions, constraints and dependencies
**Assumptions**
- Fixes recover users in proportion to the conversion gap (base case 50%, range 25% to 75%).
- Recovered users behave like current users at later stages.
- Revenue per funded account is a placeholder (Rs 2,000 a year) and must come from Finance.
- Users have given consent for communication where reminders are used.

**Constraints**
- No change to regulatory requirements; all variants need Compliance approval.
- Third-party services (DigiLocker, bank verification, e-Sign provider) are outside our control.

**Dependencies**
- Compliance decision on permitted alternative KYC and signature methods (blocks BR-01).
- Bank-verification provider support for UPI-based verification (BR-02).
- Messaging-channel approvals and templates for reminders (BR-03).
- Data and analytics capacity for the event schema and dashboard (BR-07).

## 10. Risks
| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Compliance does not approve the alternative KYC or signature path | Medium | High | Involve Compliance from week 1; prepare two options; deliver the other levers first |
| 2 | Relaxed flows increase fraud or mismatched accounts | Low | High | Keep verification checks; manual review queue; monitor rejection rate as a guardrail metric |
| 3 | Reminders feel like spam or breach consent | Medium | Medium | Consent-based, frequency caps, easy opt-out, monitor complaints |
| 4 | Bank API behaviour changes or a bank is down | Medium | Medium | Timeout and fallback (FR-05, FR-06), per-bank monitoring (FR-08) |
| 5 | Uplift is lower than the base case | Medium | Medium | A/B test each lever, release in stages, re-forecast with measured results |
| 6 | Engineering capacity delays delivery | Medium | Medium | Release in three phases; quick wins first |
| 7 | Segments overlap so benefits are not additive | High | Low | 20% overlap haircut in the model; measure combined effect after each release |

## 11. Release plan
| Release | Contents | Why first | MoSCoW |
|---|---|---|---|
| **R1: Measure and quick wins** (about 6 weeks) | FR-19 to FR-21 (events, exit reason, dashboard); FR-05 to FR-08 (bank fallback); FR-09 to FR-11 (save and resume, reminders) | Low effort, no regulatory change, and the measurement makes every later decision better | Must |
| **R2: Friction removal** (about 8 weeks) | FR-12 to FR-14 (IPV assist); FR-15, FR-16 (income-proof deferral); FR-17, FR-18 (funding) | Medium effort, each has a clear measurable gap | Should |
| **R3: Inclusive KYC** (about 12 weeks, needs Compliance) | FR-01 to FR-04 (alternative KYC and signature) | Largest conversion gap but longest lead time and regulatory dependency | Must (start approvals now) |

## 12. Open questions
1. Which alternative KYC and signature methods does Compliance permit, and with what turnaround?
2. What is the actual revenue per funded account, by channel?
3. Which messaging channels and templates are approved for reminders?
4. Does the bank-verification provider support UPI-based verification for all banks in scope?
5. Can the exit-reason prompt be shown without hurting completion?

## 13. Approvals
| Name | Role | Decision | Date |
|---|---|---|---|
| | Head of Digital Products | | |
| | Compliance officer | | |
| | Engineering lead | | |

## Appendix: glossary
| Term | Meaning |
|---|---|
| KYC | Know Your Customer: identity and address verification |
| KRA | KYC Registration Agency that stores verified KYC records |
| DigiLocker | Government digital document service used to fetch Aadhaar and PAN data |
| IPV | In-person verification, done in apps by a selfie or video liveness check |
| e-Sign | Aadhaar OTP-based electronic signature of the account-opening form |
| Penny drop | A small test credit to a bank account to verify it belongs to the user |
| UPI | Unified Payments Interface, the instant payment system |
| F&O | Futures and options trading, which needs proof of income in this flow |
| Activation | Account approved by back-office (stage 8 completed) |
| MoSCoW | Must, Should, Could, Won't prioritisation |
