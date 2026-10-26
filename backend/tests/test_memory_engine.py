import unittest
from services.memory_engine import extract_keywords, compute_similarity

class TestMemoryEngine(unittest.TestCase):
    def test_extract_keywords(self):
        text = "I am having extreme anxiety about my meeting with the manager tomorrow"
        keywords = extract_keywords(text)
        self.assertIn("extreme", keywords)
        self.assertIn("anxiety", keywords)
        self.assertIn("meeting", keywords)
        self.assertIn("manager", keywords)
        self.assertIn("tomorrow", keywords)
        self.assertNotIn("i", keywords)
        self.assertNotIn("the", keywords)

    def test_compute_similarity_identical(self):
        tokens_a = {"deadline", "coding", "burnout"}
        tokens_b = {"deadline", "coding", "burnout"}
        sim = compute_similarity(tokens_a, tokens_b, q_valence=-0.5, e_valence=-0.5)
        self.assertEqual(sim, 1.0)

    def test_compute_similarity_dissimilar(self):
        tokens_a = {"vacation", "calm", "beach"}
        tokens_b = {"deadline", "coding", "burnout"}
        sim = compute_similarity(tokens_a, tokens_b, q_valence=0.8, e_valence=-0.8)
        self.assertLess(sim, 0.3)

if __name__ == "__main__":
    unittest.main()
