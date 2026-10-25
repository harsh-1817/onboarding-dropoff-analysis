# Key findings (auto-generated from the data)

> Synthetic dataset: patterns reflect the assumptions in `src/generate_dataset.py`, not any real company.

Period: **01 Apr 2026 to 31 Aug 2026** | Sign-ups: **20,000** | Activated: **5,964 (29.8%)** | Funded: **3,462 (17.3%)** | First trade: **2,428 (12.1%)**

## Funnel

|   stage_order | stage_name                       |   entered |   completed |   dropped |   step_conversion |   cumulative_conversion |   lost_pct_of_signups |
|--------------:|:---------------------------------|----------:|------------:|----------:|------------------:|------------------------:|----------------------:|
|             1 | Registration & OTP verification  |     20000 |       18035 |      1965 |              90.2 |                    90.2 |                   9.8 |
|             2 | PAN & Aadhaar KYC                |     18035 |       12650 |      5385 |              70.1 |                    63.2 |                  26.9 |
|             3 | Bank account verification        |     12650 |       10135 |      2515 |              80.1 |                    50.7 |                  12.6 |
|             4 | Personal details & nominee       |     10135 |        9308 |       827 |              91.8 |                    46.5 |                   4.1 |
|             5 | Segment selection & income proof |      9308 |        8424 |       884 |              90.5 |                    42.1 |                   4.4 |
|             6 | Selfie / IPV verification        |      8424 |        7194 |      1230 |              85.4 |                    36   |                   6.2 |
|             7 | e-Sign                           |      7194 |        6447 |       747 |              89.6 |                    32.2 |                   3.7 |
|             8 | Account approval                 |      6447 |        5964 |       483 |              92.5 |                    29.8 |                   2.4 |
|             9 | First funding                    |      5964 |        3462 |      2502 |              58   |                    17.3 |                  12.5 |
|            10 | First trade                      |      3462 |        2428 |      1034 |              70.1 |                    12.1 |                   5.2 |

## Opportunity sizing (excess users lost vs the rest of the base)

| lever_id   | segment_definition                          | stage_short   |   seg_entered |   seg_conv |   rest_conv |   gap_pp |   excess_lost_vs_rest |
|:-----------|:--------------------------------------------|:--------------|--------------:|-----------:|------------:|---------:|----------------------:|
| L1a        | Aadhaar not linked to mobile                | KYC           |          2196 |      0.333 |       0.752 |   41.911 |                   920 |
| L1b        | Aadhaar not linked to mobile                | e-Sign        |           446 |      0.767 |       0.905 |   13.79  |                    62 |
| L2         | PNB, Bank of Baroda, Co-operative / other   | Bank          |          3948 |      0.674 |       0.859 |   18.561 |                   733 |
| L3         | Signed up 22:00-05:59 (DigiLocker-eligible) | KYC           |          1677 |      0.673 |       0.762 |    8.927 |                   150 |
| L4         | Low-end Android, web or age 55+             | Selfie/IPV    |          3123 |      0.808 |       0.881 |    7.379 |                   230 |
| L5         | Influencer / YouTube and Meta / social ads  | Funding       |          1402 |      0.495 |       0.607 |   11.174 |                   157 |
| L6         | Wants F&O                                   | Segments      |          2725 |      0.831 |       0.936 |   10.492 |                   286 |

## Drop-off reason categories

| reason_category              |   users |   share |   cumulative_share |
|:-----------------------------|--------:|--------:|-------------------:|
| Unknown (no reason captured) |    6468 |   0.368 |              0.368 |
| KYC eligibility / documents  |    2991 |   0.17  |              0.538 |
| Technical / system           |    2956 |   0.168 |              0.707 |
| Device / UX friction         |    1761 |   0.1   |              0.807 |
| Intent / affordability       |    1533 |   0.087 |              0.894 |
| Bank verification            |    1300 |   0.074 |              0.968 |
| Payment                      |     361 |   0.021 |              0.989 |
| Left intending to return     |     202 |   0.011 |              1     |
