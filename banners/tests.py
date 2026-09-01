from datetime import datetime, timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from banners.models import Entity, Banner, UpcomingEvent


class BannerSystemTests(TestCase):
    """
    Test suite for Multi-Entity Banner Management System separate & combined APIs.
    """
    def setUp(self):
        self.client = Client()

        # Create active entity
        self.entity = Entity.objects.create(
            name='Test Enterprise',
            slug='test-enterprise',
            url='https://test.example.com',
            is_active=True
        )

        # Create inactive entity
        self.inactive_entity = Entity.objects.create(
            name='Inactive Co',
            slug='inactive-co',
            url='https://inactive.example.com',
            is_active=False
        )

        # Dummy image file
        dummy_image = SimpleUploadedFile(
            name='test_banner.png',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82',
            content_type='image/png'
        )

        # Active banner
        self.active_banner = Banner.objects.create(
            entity=self.entity,
            title='Summer Special',
            text='Get 20% off',
            link='https://test.example.com/sale',
            image=dummy_image,
            is_active=True
        )

        # Inactive banner
        self.inactive_banner = Banner.objects.create(
            entity=self.entity,
            title='Old Special',
            text='Expired discount',
            link='https://test.example.com/old',
            image=dummy_image,
            is_active=False
        )

        # Active upcoming event with image
        self.active_event = UpcomingEvent.objects.create(
            entity=self.entity,
            name='Annual Conference 2026',
            description='Keynote speaker presentation',
            event_date=datetime(2026, 12, 15, 10, 0, tzinfo=timezone.utc),
            image=dummy_image,
            is_active=True
        )

    def test_banner_only_api(self):
        """Test GET /api/banner/<slug>/ returns ONLY banner data."""
        url = reverse('banners:banner-detail', kwargs={'slug': 'test-enterprise'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['entity'], 'Test Enterprise')
        self.assertEqual(data['slug'], 'test-enterprise')
        self.assertIn('banners', data)
        self.assertNotIn('upcoming_events', data)
        self.assertEqual(len(data['banners']), 1)
        self.assertEqual(data['banners'][0]['title'], 'Summer Special')

    def test_events_only_api(self):
        """Test GET /api/events/<slug>/ returns ONLY upcoming events data with image URL."""
        url = reverse('banners:events-detail', kwargs={'slug': 'test-enterprise'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['entity'], 'Test Enterprise')
        self.assertEqual(data['slug'], 'test-enterprise')
        self.assertIn('upcoming_events', data)
        self.assertNotIn('banners', data)
        self.assertEqual(len(data['upcoming_events']), 1)
        self.assertEqual(data['upcoming_events'][0]['name'], 'Annual Conference 2026')
        self.assertEqual(data['upcoming_events'][0]['event_date'], 'December 15, 2026')
        self.assertIn('image', data['upcoming_events'][0])
        self.assertTrue('test_banner' in data['upcoming_events'][0]['image'])

    def test_combined_api_backward_compatibility(self):
        """Test GET /api/combined/<slug>/ returns both banners and events with image fields."""
        url = reverse('banners:combined-detail', kwargs={'slug': 'test-enterprise'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('banners', data)
        self.assertIn('upcoming_events', data)
        self.assertIn('image', data['upcoming_events'][0])

    def test_invalid_date_range_returns_400(self):
        """Invalid date ranges should fail before any queryset filtering."""
        url = reverse('banners:events-detail', kwargs={'slug': 'test-enterprise'})
        response = self.client.get(url, {'from': '2026-01-01', 'to': '2025-08-31'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')
        self.assertIn('from', response.json()['message'])
        self.assertIn('to', response.json()['message'])

    def test_404_error_responses(self):
        """Test 404 responses for non-existent and inactive entities."""
        banner_404 = self.client.get(reverse('banners:banner-detail', kwargs={'slug': 'non-existent'}))
        self.assertEqual(banner_404.status_code, 404)
        self.assertEqual(banner_404.json()['status'], 'error')

        events_404 = self.client.get(reverse('banners:events-detail', kwargs={'slug': 'inactive-co'}))
        self.assertEqual(events_404.status_code, 404)
        self.assertEqual(events_404.json()['status'], 'error')

    def test_cors_options(self):
        """Test OPTIONS CORS preflight handling."""
        res_banner = self.client.options(reverse('banners:banner-detail', kwargs={'slug': 'test-enterprise'}))
        self.assertEqual(res_banner.status_code, 200)
        self.assertEqual(res_banner.headers.get('Access-Control-Allow-Origin'), '*')

        res_events = self.client.options(reverse('banners:events-detail', kwargs={'slug': 'test-enterprise'}))
        self.assertEqual(res_events.status_code, 200)
        self.assertEqual(res_events.headers.get('Access-Control-Allow-Origin'), '*')
