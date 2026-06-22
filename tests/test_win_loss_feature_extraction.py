import unittest

from fetch_lost_deals import (
    PRODUCT_FEEDBACK_OPTIONS,
    UNCLASSIFIED_PRODUCT_LIMITATION_FEATURE,
    _FEATURE_KEYWORD_MAP,
    _FEATURE_REGEX_RULES,
    _canonical_feature_name,
    _extract_features_from_notes,
    _feature_category,
    build_feature_impact_rows,
)


def feature_names(note, outcome="LOST"):
    return {item["feature"] for item in _extract_features_from_notes(note, outcome)}


class WinLossFeatureExtractionTests(unittest.TestCase):
    def test_every_emittable_feature_has_a_product_category(self):
        labels = set(PRODUCT_FEEDBACK_OPTIONS)
        labels.update(_FEATURE_KEYWORD_MAP.values())
        labels.update(category for _, category in _FEATURE_REGEX_RULES)

        uncategorized = sorted(
            label for label in labels if _feature_category(label) == "NEEDS_REVIEW"
        )
        self.assertEqual([], uncategorized)

    def test_language_alias_does_not_split_the_same_gap(self):
        self.assertEqual(
            "Multi-language Support",
            _canonical_feature_name("Localization / Multi-language Support"),
        )
        names = feature_names("The language functionality is not feasible for us.")
        self.assertEqual({"Multi-language Support"}, names)

    def test_unclassified_product_limitation_is_not_forced(self):
        self.assertEqual(
            "NEEDS_REVIEW",
            _feature_category(UNCLASSIFIED_PRODUCT_LIMITATION_FEATURE),
        )

    def test_feature_impact_rows_expose_the_parent_category(self):
        rows = build_feature_impact_rows([{
            "id": "deal-1",
            "outcome": "LOST",
            "amount": 6000,
            "amount_estimated": True,
            "features_mentioned": [{"feature": "Question Bank", "quote": "No question pool"}],
            "competitors_mentioned": [],
        }])
        self.assertEqual("Assessments & Quizzes", rows[0]["category"])

    def test_compliance_word_does_not_imply_attendance_reporting(self):
        names = feature_names(
            "No question bank or randomization. Course compliance is all or "
            "nothing and cannot support pass-one-of-three logic."
        )
        self.assertNotIn("Attendance Reporting (Compliance Use Case)", names)
        self.assertIn("Question Bank", names)
        self.assertIn("Quiz / Assessment Builder", names)

    def test_cross_course_compliance_is_completion_gating(self):
        names = feature_names(
            "Cross-course learning paths: no way to require Course A completion "
            "before unlocking Course B. Within one course compliance is supported."
        )
        self.assertNotIn("Attendance Reporting (Compliance Use Case)", names)
        self.assertIn("Course Sequencing / Completion Gating", names)
        self.assertNotIn("Learning Paths", names)

    def test_security_compliance_keeps_specific_meaning(self):
        hipaa = feature_names(
            "HIPAA compliance would require Teachable to sign a Business Associate Agreement."
        )
        pci = feature_names(
            "PCI compliance documentation was a hard requirement.", outcome="WON"
        )
        self.assertEqual({"HIPAA / BAA Compliance"}, hipaa)
        self.assertEqual({"PCI Compliance Documentation"}, pci)

    def test_hybrid_business_model_is_not_hybrid_scheduling(self):
        names = feature_names(
            "Their use case was a hybrid B2C subscription plus B2B seat-based "
            "organizational structure. Assessment depth was also important."
        )
        self.assertNotIn("Hybrid Scheduling", names)
        self.assertIn("Organizations / Multi-tenancy", names)
        self.assertIn("Quiz / Assessment Builder", names)

    def test_certificate_eligibility_is_submission_tracking(self):
        names = feature_names(
            "Tracking student submissions for certificate eligibility is required. "
            "Certificate issuance depends on that tracking."
        )
        self.assertNotIn("Certificate Issuance", names)
        self.assertIn("File Upload & Grading", names)

    def test_attendance_requires_attendance_context(self):
        names = feature_names(
            "There is no built-in attendance for a mixed in-person and remote audience."
        )
        self.assertIn("Attendance Reporting (Compliance Use Case)", names)
        self.assertIn("Hybrid Scheduling", names)

    def test_workaround_does_not_become_the_primary_gap(self):
        names = feature_names(
            "Per-country content branching is missing. We could use learning paths "
            "once those are available as a workaround."
        )
        self.assertIn("Conditional Content Visibility (Per User)", names)
        self.assertNotIn("Learning Paths", names)


if __name__ == "__main__":
    unittest.main()
