# Requirements Traceability Matrix

Every finding traces to a requirement, stories, test cases and a KPI, so nothing is built without evidence and nothing found is left without an owner.

| Finding | Business req. | Functional req. | User stories | UAT test cases | KPI that proves it |
|---|---|---|---|---|---|
| F1, F2 | BR-01 | FR-01, FR-02, FR-03, FR-04 | US-01, US-02, US-03 | TC-01 to TC-05 | KYC conversion; offline-KYC activation |
| F3 | BR-02 | FR-05, FR-06, FR-07, FR-08 | US-04, US-05, US-06 | TC-06 to TC-09 | Bank-verification conversion |
| F4, F9 | BR-03 | FR-09, FR-10, FR-11 | US-07, US-08, US-09 | TC-10 to TC-14 | KYC conversion; median hours to activate |
| F5 | BR-04 | FR-12, FR-13, FR-14 | US-10, US-11, US-12 | TC-15 to TC-17 | Selfie / IPV conversion |
| F6 | BR-05 | FR-15, FR-16 | US-13, US-14 | TC-18 to TC-20 | Segments step conversion |
| F7 | BR-06 | FR-17, FR-18 | US-15, US-16 | TC-21 to TC-23 | First-funding conversion; funded rate |
| F8 | BR-07 | FR-19, FR-20, FR-21 | US-17, US-18, US-19 | TC-24 to TC-26 | Share of drop-offs with no reason |
| All | NFR-01 to NFR-08 | n/a | n/a | TC-27 to TC-30 | Performance, privacy and security checks |

**Findings key**

| ID | Finding |
|---|---|
| F1 | KYC is the largest leak (5,385 users lost) |
| F2 | Aadhaar-not-linked users are stuck at KYC and e-Sign |
| F3 | Bank verification fails for some banks and when slow |
| F4 | Late-night starters do not come back |
| F5 | Selfie / IPV fails on weaker devices |
| F6 | F&O seekers drop at income proof |
| F7 | First funding is the second-biggest leak (2,502 users lost) |
| F8 | A third of drop-offs have no recorded reason |
| F9 | Activation is slow |