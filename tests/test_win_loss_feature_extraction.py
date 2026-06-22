import unittest

from fetch_lost_deals import _extract_features_from_notes


def feature_names(note, outcome="LOST"):
    return {item["feature"] for item in _extract_features_from_notes(note, outcome)}


class WinLossFeatureExtractionTests(unittest.TestCase):
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
