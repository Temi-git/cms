import io
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
from banners.models import Entity, Banner, UpcomingEvent


class Command(BaseCommand):
    help = 'Seeds database with initial sample entities, banners, events with images, and a default superuser.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting seed process...'))

        # 1. Create default admin superuser if not present
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))
        else:
            self.stdout.write('Superuser "admin" already exists.')

        # Helper function to generate a dummy image in memory
        def generate_sample_image(filename_prefix, color_rgb):
            img = Image.new('RGB', (800, 300), color=color_rgb)
            draw = ImageDraw.Draw(img)
            draw.rectangle([10, 10, 790, 290], outline=(255, 255, 255), width=3)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return ContentFile(buffer.getvalue(), name=f"{filename_prefix}.png")

        # 2. Seed Entity 1: TechCorp
        entity1, created1 = Entity.objects.get_or_create(
            slug='tech-corp',
            defaults={
                'name': 'TechCorp Solutions',
                'url': 'https://techcorp.example.com',
                'is_active': True
            }
        )

        if created1:
            self.stdout.write(self.style.SUCCESS(f'Created Entity: {entity1.name}'))

            # Create Banners for TechCorp
            b1 = Banner.objects.create(
                entity=entity1,
                title='Summer Sale 2026',
                text='Get 50% off all software licenses during our annual summer event.',
                link='https://techcorp.example.com/summer-sale',
                is_active=True
            )
            b1.image.save('summer_sale.png', generate_sample_image('summer_sale', (41, 128, 185)), save=True)

            b2 = Banner.objects.create(
                entity=entity1,
                title='Cloud Migration Offer',
                text='Upgrade your legacy systems to our cloud platform today.',
                link='https://techcorp.example.com/cloud',
                is_active=True
            )
            b2.image.save('cloud_offer.png', generate_sample_image('cloud_offer', (39, 174, 96)), save=True)

            # Inactive Banner
            b3 = Banner.objects.create(
                entity=entity1,
                title='Expired Promo',
                text='This promo is no longer active.',
                link='https://techcorp.example.com/expired',
                is_active=False
            )
            b3.image.save('expired_promo.png', generate_sample_image('expired_promo', (192, 57, 43)), save=True)

            # Create Upcoming Events for TechCorp with images
            e1 = UpcomingEvent.objects.create(
                entity=entity1,
                name='Product Launch 2026',
                description='Join us live for the grand unveil of our next-gen platform.',
                event_date=datetime(2026, 12, 15, 14, 0, tzinfo=timezone.utc),
                is_active=True
            )
            e1.image.save('product_launch.png', generate_sample_image('product_launch', (230, 126, 34)), save=True)

            e2 = UpcomingEvent.objects.create(
                entity=entity1,
                name='Global Tech Developer Summit',
                description='Annual developer conference bringing together engineers worldwide.',
                event_date=datetime(2026, 11, 20, 10, 0, tzinfo=timezone.utc),
                is_active=True
            )
            e2.image.save('tech_summit.png', generate_sample_image('tech_summit', (155, 89, 182)), save=True)

        # 3. Seed Entity 2: Acme Inc
        entity2, created2 = Entity.objects.get_or_create(
            slug='acme-inc',
            defaults={
                'name': 'Acme Corporation',
                'url': 'https://acme.example.com',
                'is_active': True
            }
        )

        if created2:
            self.stdout.write(self.style.SUCCESS(f'Created Entity: {entity2.name}'))

            # Create Banner for Acme Inc
            b4 = Banner.objects.create(
                entity=entity2,
                title='Black Friday Megadeals',
                text='Exclusive discounts on enterprise hardware and tools.',
                link='https://acme.example.com/blackfriday',
                is_active=True
            )
            b4.image.save('black_friday.png', generate_sample_image('black_friday', (142, 68, 173)), save=True)

            # Create Upcoming Event for Acme Inc with image
            e3 = UpcomingEvent.objects.create(
                entity=entity2,
                name='Acme Partner Keynote',
                description='Quarterly strategy alignment for business partners.',
                event_date=datetime(2026, 10, 5, 9, 30, tzinfo=timezone.utc),
                is_active=True
            )
            e3.image.save('partner_keynote.png', generate_sample_image('partner_keynote', (52, 73, 94)), save=True)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
