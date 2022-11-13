import unittest
import requests


class MyTestCase(unittest.TestCase):
    def test_sorting(self):
        r = requests.post('http://127.0.0.1:5000/location',
                          json={'location': 'London', 'page': '1', 'sorting': 'Title'})
        page1 = r.json()

        r = requests.post('http://127.0.0.1:5000/location',
                          json={'location': 'London', 'page': '2', 'sorting': 'Title'})
        page2 = r.json()

        self.assertGreaterEqual(page1[-1]['Title'], page1[0]['Title'])
        self.assertGreaterEqual(page2[0]['Title'], page1[-1]['Title'])

    def test_pagination(self):
        r = requests.post('http://127.0.0.1:5000/location',
                          json={'location': 'London', 'page': '0', 'sorting': 'Title'})
        page0 = r.json()

        r = requests.post('http://127.0.0.1:5000/location',
                          json={'location': 'London', 'page': '1', 'sorting': 'Title'})
        page1 = r.json()

        self.assertNotEqual(page0[0], page1[0])


if __name__ == '__main__':
    unittest.main()
