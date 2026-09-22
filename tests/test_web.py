import json, threading, unittest, urllib.error, urllib.request
from http.server import ThreadingHTTPServer

from flavoretro.web import Handler


class WebTeachingEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path):
        try:
            with urllib.request.urlopen(self.base + path) as response:
                return (
                    response.status,
                    dict(response.headers),
                    json.loads(response.read()),
                )
        except urllib.error.HTTPError as exc:
            return exc.code, dict(exc.headers), json.loads(exc.read())

    def test_teaching_returns_classifications_with_evidence_boundary(self):
        status, headers, body = self.get("/api/teaching")
        self.assertEqual(status, 200)
        self.assertTrue(headers.get("Content-Type", "").startswith("application/json"))
        self.assertEqual(headers.get("Cache-Control"), "no-store")
        self.assertIsInstance(body, dict)
        classifications = body.get("classifications")
        self.assertIsInstance(classifications, dict)
        self.assertGreater(len(classifications), 0)
        for key, entry in classifications.items():
            self.assertIn("evidence_boundary_zh", entry, key)
        self.assertIn("evidence_boundary_zh", body.get("default", {}))

    def test_literature_teaching_returns_cards_with_claim_status(self):
        status, headers, body = self.get("/api/literature-teaching")
        self.assertEqual(status, 200)
        self.assertTrue(headers.get("Content-Type", "").startswith("application/json"))
        self.assertEqual(headers.get("Cache-Control"), "no-store")
        self.assertIsInstance(body, dict)
        cards = body.get("paper_cards")
        self.assertIsInstance(cards, list)
        self.assertGreater(len(cards), 0)
        for card in cards:
            self.assertIn("claim_status", card)

    def test_unknown_path_is_404_not_found(self):
        status, headers, body = self.get("/api/definitely-not-a-route")
        self.assertEqual(status, 404)
        self.assertEqual(body, {"error": "not_found"})
        self.assertEqual(headers.get("Cache-Control"), "no-store")


if __name__ == "__main__":
    unittest.main()
