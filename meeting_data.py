"""Sample meeting data for the compliance checker agent."""

organizations = [
    {
        "id": "org-001",
        "name": "Acme Digital Solutions",
        "industry": "Technology Services",
        "data_protection_officer": "Elena Korhonen",
    }
]

meeting_records = [
    {
        "id": "meeting-001",
        "title": "Customer Onboarding and Data Sharing Review",
        "date": "2026-05-14",
        "duration_minutes": 90,
        "participants": [
            "Mikko Lehtinen",
            "Sofia Virtanen",
            "Ari Koskinen",
            "Elena Korhonen",
        ],
        "organization_id": "org-001",
        "summary": "Review of the new onboarding flow, customer data collection, third-party sharing and legal review requirements.",
        "decision_ids": ["decision-001", "decision-002"],
        "action_item_ids": ["action-001", "action-002", "action-003"],
        "plan_id": "plan-001",
    }
]

transcripts = {
    "meeting-001": [
        {
            "speaker": "Mikko Lehtinen",
            "text": "We want to add a new onboarding screen that asks customers for their date of birth, address, and optionally health-related preferences so we can personalise services.",
        },
        {
            "speaker": "Sofia Virtanen",
            "text": "I think we should be very careful about sensitive personal data. GDPR requires that we justify why we collect these fields. If the new flow stores contact details and health preferences, we may need a DPIA.",
        },
        {
            "speaker": "Ari Koskinen",
            "text": "The plan is also to share the customer profile with our marketing partner and a payment gateway provider in Estonia. That is an international transfer, and we need to understand if it is lawful under GDPR.",
        },
        {
            "speaker": "Elena Korhonen",
            "text": "I recommend we involve legal counsel and the data protection officer before we launch this. We should not finalise the integration until the lawyer has reviewed the data-sharing agreement and the DPIA is completed.",
        },
        {
            "speaker": "Mikko Lehtinen",
            "text": "So the decisions are: update the onboarding flow with privacy by design principles, check the third-party sharing with our lawyer, and prepare a DPIA if we keep health and address information.",
        },
    ]
}

decisions = [
    {
        "id": "decision-001",
        "meeting_id": "meeting-001",
        "title": "Approve new onboarding fields with privacy safeguards",
        "context": "The team agreed to collect customer demographics, contact details, and optional health preferences only if the business case is clearly documented.",
        "category": "GDPR",
    },
    {
        "id": "decision-002",
        "meeting_id": "meeting-001",
        "title": "Require legal review before data sharing",
        "context": "All third-party sharing of customer data must be reviewed by legal counsel and DPO prior to integration.",
        "category": "Legal",
    },
]

action_items = [
    {
        "id": "action-001",
        "meeting_id": "meeting-001",
        "description": "Draft the onboarding data collection details and privacy justification for the new customer flow.",
        "owner": "Sofia Virtanen",
        "due_date": "2026-05-21",
        "related_decision_id": "decision-001",
    },
    {
        "id": "action-002",
        "meeting_id": "meeting-001",
        "description": "Schedule a meeting with the company lawyer to review third-party data sharing and GDPR compliance.",
        "owner": "Elena Korhonen",
        "due_date": "2026-05-19",
        "related_decision_id": "decision-002",
    },
    {
        "id": "action-003",
        "meeting_id": "meeting-001",
        "description": "Prepare a draft DPIA for the planned onboarding flow and submit it to the compliance board.",
        "owner": "Ari Koskinen",
        "due_date": "2026-05-24",
        "related_decision_id": "decision-001",
    },
]

execution_plan = {
    "id": "plan-001",
    "name": "Customer Onboarding Compliance Plan",
    "current_phase": "Review",
    "milestones": [
        {"milestone": "Define data fields", "status": "Completed"},
        {"milestone": "Legal and DPIA review", "status": "In Progress"},
        {"milestone": "Launch onboarding flow", "status": "Pending"},
    ],
    "related_meeting_ids": ["meeting-001"],
}

plan_versions = [
    {
        "plan_id": "plan-001",
        "version": 1,
        "timestamp": "2026-05-14T10:12:00Z",
        "changes": "Initial plan created after first compliance review meeting.",
    },
    {
        "plan_id": "plan-001",
        "version": 2,
        "timestamp": "2026-05-16T09:05:00Z",
        "changes": "Added DPIA preparation and legal review milestones.",
    },
]
