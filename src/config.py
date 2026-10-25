"""Shared configuration for the onboarding drop-off case study."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
CHART_DIR = ROOT / "dashboard" / "charts"
DOCS_DIR = ROOT / "docs"
SQL_DIR = ROOT / "sql"

DB_NAME = "broker_onboarding"
DB_URL = os.getenv("DB_URL", f"mysql+pymysql://root:@localhost:3306/{DB_NAME}")

# --- Funnel definition ------------------------------------------------------------------------------
# (order, full name, short name used in charts)
STAGES = [
    (1, "Registration & OTP verification", "Registration"),
    (2, "PAN & Aadhaar KYC", "KYC"),
    (3, "Bank account verification", "Bank"),
    (4, "Personal details & nominee", "Details"),
    (5, "Segment selection & income proof", "Segments"),
    (6, "Selfie / IPV verification", "Selfie/IPV"),
    (7, "e-Sign", "e-Sign"),
    (8, "Account approval", "Approval"),
    (9, "First funding", "Funding"),
    (10, "First trade", "First trade"),
]
STAGE_NAME = {o: n for o, n, _ in STAGES}
STAGE_SHORT = {o: s for o, _, s in STAGES}
ACTIVATION_STAGE = 8   # an account counts as "activated" once stage 8 is completed

# Reason codes grouped into business categories (used for the drop-off Pareto)
REASON_CATEGORY = {
    "OTP_NOT_RECEIVED": "Technical / system",
    "EMAIL_VERIFICATION_ISSUE": "Technical / system",
    "DIGILOCKER_ERROR": "Technical / system",
    "DIGILOCKER_TIMEOUT": "Technical / system",
    "VERIFICATION_TIMEOUT": "Technical / system",
    "PENNY_DROP_FAILED": "Bank verification",
    "BANK_NOT_SUPPORTED": "Bank verification",
    "BANK_NAME_MISMATCH": "Bank verification",
    "AADHAAR_MOBILE_NOT_LINKED": "KYC eligibility / documents",
    "PAN_AADHAAR_NAME_MISMATCH": "KYC eligibility / documents",
    "PAN_NOT_AVAILABLE": "KYC eligibility / documents",
    "INCOME_PROOF_UNAVAILABLE": "KYC eligibility / documents",
    "NOMINEE_DETAILS_UNAVAILABLE": "KYC eligibility / documents",
    "PHYSICAL_SIGNATURE_COURIER_PENDING": "KYC eligibility / documents",
    "KYC_REJECTED_NAME_MISMATCH": "KYC eligibility / documents",
    "KYC_REJECTED_POOR_DOCUMENT": "KYC eligibility / documents",
    "REJECTED_OTHER": "KYC eligibility / documents",
    "SELFIE_FAILED_LIGHTING": "Device / UX friction",
    "LIVENESS_CHECK_FAILED": "Device / UX friction",
    "CAMERA_PERMISSION_DENIED": "Device / UX friction",
    "ESIGN_OTP_FAILED": "Device / UX friction",
    "TOO_MANY_FIELDS": "Device / UX friction",
    "SEGMENT_CONFUSION": "Device / UX friction",
    "PLATFORM_COMPLEXITY": "Device / UX friction",
    "UPI_PAYMENT_FAILED": "Payment",
    "DEFERRED_NEVER_RETURNED": "Left intending to return",
    "NO_FUNDS_TO_ADD": "Intent / affordability",
    "WAITING_FOR_MARKET_DIP": "Intent / affordability",
    "NO_TRADING_IDEA": "Intent / affordability",
    "BROKERAGE_CHARGES_CONCERN": "Intent / affordability",
    "ABANDONED_NO_REASON": "Unknown (no reason captured)",
}
