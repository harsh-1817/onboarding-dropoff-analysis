# Process Flows

Diagrams use Mermaid and render on GitHub. Loss percentages are the share of **all sign-ups** lost at that step.

## 1. As-is onboarding flow
```mermaid
flowchart TD
    S([User opens app or website]) --> R1["1. Mobile + email OTP<br/>9.8% of sign-ups lost"]
    R1 --> K{"Aadhaar linked<br/>to mobile?"}
    K -- Yes --> K1["2. PAN + Aadhaar via DigiLocker<br/>26.9% lost: the largest leak"]
    K -- No --> K2["2. Offline / manual KYC<br/>only 33.3% convert"]
    K1 --> B["3. Bank verification (penny drop)<br/>12.6% lost"]
    K2 --> B
    B --> P["4. Personal details + nominee"]
    P --> G["5. Segments + income proof for F&O"]
    G --> I["6. Selfie / IPV"]
    I --> E{"Aadhaar OTP<br/>e-Sign possible?"}
    E -- Yes --> E1["7. e-Sign"]
    E -- No --> E2["7. Print, sign and courier"]
    E1 --> A["8. Back-office approval<br/>median wait about a day"]
    E2 --> A
    A --> F["9. First funding (UPI)<br/>12.5% lost: second-biggest leak"]
    F --> T(["10. First trade"])
    classDef leak fill:#fde2e1,stroke:#c0392b,color:#000;
    class K1,K2,B,F leak;
```

**Pain points**
| Step | Pain point | Evidence |
|---|---|---|
| KYC | Aadhaar-mobile mismatch ends the journey; late-night starters leave and do not return | F1, F2, F4 |
| Bank | Slow penny-drop responses and unsupported co-operative banks | F3 |
| Selfie / IPV | Failures on low-end devices and web | F5 |
| Signature | Offline users must print, sign and courier | F2 |
| Funding | No guided path from approval to first deposit | F7 |
| All | Reasons for drop-off are unknown for 36.8% of cases | F8 |

## 2. To-be onboarding flow
```mermaid
flowchart TD
    S([User opens app or website]) --> R1["1. Mobile + email OTP"]
    R1 --> K{"Aadhaar linked<br/>to mobile?"}
    K -- Yes --> K1["2. DigiLocker KYC"]
    K -- No --> K2["2. Alternative KYC path<br/>(Compliance-approved) with status tracker"]
    K1 --> B{"3. Bank verified<br/>within 60 s?"}
    K2 --> B
    B -- Yes --> P["4. Personal details + nominee"]
    B -- No --> B2["Fallback: UPI verification<br/>or cancelled cheque upload"]
    B2 --> P
    P --> G{"5. Wants F&O<br/>and has income proof?"}
    G -- Yes --> G1["All segments"]
    G -- No --> G2["Cash segments now,<br/>F&O proof added later"]
    G1 --> I["6. Selfie / IPV with live guidance"]
    G2 --> I
    I --> I2{"Failed twice?"}
    I2 -- Yes --> I3["Retry later link<br/>or assisted video"]
    I2 -- No --> E["7. e-Sign or approved alternative"]
    I3 --> E
    E --> A["8. Approval with tracked status"]
    A --> F["9. One-tap UPI funding<br/>+ day 1, 3, 7 nudges"]
    F --> T(["10. First trade"])
    SAVE["Progress saved after every step<br/>Resume on any device"] -.-> K
    REM["Consent-based reminders at 30 min, 24 h, 72 h<br/>'Continue tomorrow' for late-night starters"] -.-> SAVE
    EV["Every step emits events + exit-reason prompt"] -.-> A
    classDef fresh fill:#e3f4e8,stroke:#2e8b57,color:#000;
    class K2,B2,G2,I3,SAVE,REM,EV fresh;
```
Green boxes are new or changed. Sign-off from Compliance is required for the alternative KYC and signature steps.

## 3. Application status model
```mermaid
stateDiagram-v2
    [*] --> Registered
    Registered --> KYC_in_progress
    KYC_in_progress --> Paused: user leaves
    Paused --> KYC_in_progress: resume link or reminder
    Paused --> Abandoned: no activity for 30 days
    KYC_in_progress --> KYC_verified
    KYC_verified --> Bank_verified
    Bank_verified --> Details_complete
    Details_complete --> IPV_done
    IPV_done --> Signed
    Signed --> Under_review
    Under_review --> Activated: approved
    Under_review --> Action_needed: documents rejected
    Action_needed --> Under_review: resubmitted
    Activated --> Funded: first deposit
    Funded --> Trading: first trade
    Abandoned --> [*]
    Trading --> [*]
```

## 4. Bank verification with fallback (sequence)
```mermaid
sequenceDiagram
    participant U as User
    participant A as App
    participant V as Verification service
    participant O as Ops queue
    U->>A: Enter account number and IFSC
    A->>V: Penny-drop request (60 s timeout)
    alt Verified in time
        V-->>A: Success
        A-->>U: Bank verified
    else Timeout or failure
        A-->>U: Offer UPI verification or cheque upload
        alt UPI chosen
            U->>A: Pay via UPI
            A->>V: Confirm payment and name
            V-->>A: Success
            A-->>U: Bank verified
        else Cheque chosen
            U->>A: Upload cancelled cheque
            A->>A: Extract name, account, IFSC
            alt Name matches PAN
                A-->>U: Bank verified
            else Mismatch
                A->>O: Create review task
                O-->>A: Decision
                A-->>U: Verified or action needed
            end
        end
    end
```
