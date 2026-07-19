import uuid
import os
import urllib.request
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta

from accounts.models import Profile
from auctions.models import Category, Auction, Bid
from payments.models import Payment, Transaction


class Command(BaseCommand):
    help = "Seed the database with sample data for the online auction platform"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            "This will DELETE all existing data and replace it with sample data."
        ))
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            self.stdout.write(self.style.NOTICE("Aborted."))
            return

        try:
            self.clear_data()
            users = self.create_users()
            profiles = self.create_profiles(users)
            categories = self.create_categories()
            auctions = self.create_auctions(users, categories)
            self.create_bids(users, auctions)
            self.create_payments(users, auctions)

            self.stdout.write(self.style.SUCCESS("\nDatabase seeded successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nError seeding database: {e}"))
            raise

    # ------------------------------------------------------------------
    # Clear existing data
    # ------------------------------------------------------------------
    def clear_data(self):
        self.stdout.write("Clearing existing data...")
        Transaction.objects.all().delete()
        Payment.objects.all().delete()
        Bid.objects.all().delete()
        Auction.objects.all().delete()
        Category.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.NOTICE("  Existing data cleared."))

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    def create_users(self):
        self.stdout.write("Creating users...")

        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "john_seller",
                "email": "john@example.com",
                "password": "john123",
                "first_name": "John",
                "last_name": "Smith",
            },
            {
                "username": "jane_seller",
                "email": "jane@example.com",
                "password": "jane123",
                "first_name": "Jane",
                "last_name": "Doe",
            },
            {
                "username": "mike_buyer",
                "email": "mike@example.com",
                "password": "mike123",
                "first_name": "Mike",
                "last_name": "Johnson",
            },
            {
                "username": "sarah_buyer",
                "email": "sarah@example.com",
                "password": "sarah123",
                "first_name": "Sarah",
                "last_name": "Williams",
            },
            {
                "username": "alex_buyer",
                "email": "alex@example.com",
                "password": "alex123",
                "first_name": "Alex",
                "last_name": "Brown",
            },
        ]

        users = {}
        for data in users_data:
            password = data.pop("password")
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults=data,
            )
            if created:
                user.set_password(password)
                user.save()
            users[data["username"]] = user
            status = "created" if created else "already exists"
            self.stdout.write(f"  User {data['username']} {status}.")

        return users

    # ------------------------------------------------------------------
    # Profiles
    # ------------------------------------------------------------------
    def create_profiles(self, users):
        self.stdout.write("Creating profiles...")

        profiles_data = {
            "admin": {
                "phone": "+1-555-0100",
                "address": "100 Admin Ave",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94105",
                "is_seller": False,
            },
            "john_seller": {
                "phone": "+1-555-0201",
                "address": "45 Commerce St",
                "city": "Austin",
                "state": "TX",
                "zip_code": "73301",
                "is_seller": True,
            },
            "jane_seller": {
                "phone": "+1-555-0202",
                "address": "78 Market Blvd",
                "city": "Portland",
                "state": "OR",
                "zip_code": "97201",
                "is_seller": True,
            },
            "mike_buyer": {
                "phone": "+1-555-0301",
                "address": "210 Oak Lane",
                "city": "Denver",
                "state": "CO",
                "zip_code": "80201",
                "is_seller": False,
            },
            "sarah_buyer": {
                "phone": "+1-555-0302",
                "address": "55 Maple Dr",
                "city": "Seattle",
                "state": "WA",
                "zip_code": "98101",
                "is_seller": False,
            },
            "alex_buyer": {
                "phone": "+1-555-0303",
                "address": "330 Pine Rd",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60601",
                "is_seller": False,
            },
        }

        profiles = {}
        for username, pdata in profiles_data.items():
            profile, created = Profile.objects.get_or_create(
                user=users[username],
                defaults=pdata,
            )
            profiles[username] = profile
            status = "created" if created else "already exists"
            self.stdout.write(f"  Profile for {username} {status}.")

        return profiles

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------
    def create_categories(self):
        self.stdout.write("Creating categories...")

        categories_data = [
            {"name": "Electronics", "slug": "electronics", "description": "Gadgets, devices, and tech accessories"},
            {"name": "Art & Collectibles", "slug": "art-collectibles", "description": "Paintings, sculptures, and rare collectibles"},
            {"name": "Fashion", "slug": "fashion", "description": "Clothing, shoes, and accessories"},
            {"name": "Home & Garden", "slug": "home-garden", "description": "Furniture, decor, and garden essentials"},
            {"name": "Vehicles", "slug": "vehicles", "description": "Cars, motorcycles, and other vehicles"},
            {"name": "Sports", "slug": "sports", "description": "Sports equipment and memorabilia"},
            {"name": "Books & Media", "slug": "books-media", "description": "Books, movies, and music"},
            {"name": "Jewelry", "slug": "jewelry", "description": "Rings, necklaces, watches, and more"},
        ]

        categories = {}
        for data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={"name": data["name"], "description": data["description"]},
            )
            categories[data["slug"]] = cat
            status = "created" if created else "already exists"
            self.stdout.write(f"  Category '{data['name']}' {status}.")

        return categories

    # ------------------------------------------------------------------
    # Auctions
    # ------------------------------------------------------------------
    def create_auctions(self, users, categories):
        self.stdout.write("Creating auctions...")

        now = timezone.now()

        auctions_data = [
            # --- ENDED AUCTIONS (end_time in the past) ---
            {
                "title": "Vintage Rolex Submariner Watch",
                "description": (
                    "A stunning vintage Rolex Submariner from 1968 in excellent working condition. "
                    "Original bezel, dial, and hands. Serviced in 2023. Comes with original box and papers. "
                    "A true collector's piece that has held its value remarkably well over the decades."
                ),
                "category": "jewelry",
                "seller": "jane_seller",
                "starting_price": Decimal("4500.00"),
                "end_offset_days": -5,
                "is_active": False,
                "is_featured": True,
                "image_url": "https://loremflickr.com/800/600/rolex,watch,vintage",
            },
            {
                "title": "2019 Tesla Model 3 Long Range",
                "description": (
                    "White exterior, black interior. 35,000 miles. Autopilot included. "
                    "New tires at 30k miles. Clean title, no accidents. Regular maintenance at Tesla service center. "
                    "Excellent range still at 92% battery health. Perfect for daily commuting."
                ),
                "category": "vehicles",
                "seller": "john_seller",
                "starting_price": Decimal("28000.00"),
                "end_offset_days": -3,
                "is_active": False,
                "is_featured": True,
                "image_url": "https://loremflickr.com/800/600/tesla,model3,electric-car",
            },
            {
                "title": "Sony PlayStation 5 Bundle",
                "description": (
                    "Includes PS5 console, two DualSense controllers, three games (Spider-Man 2, "
                    "God of War Ragnarok, Horizon Forbidden West), and an extra charging station. "
                    "Console is in mint condition, always kept in a ventilated area."
                ),
                "category": "electronics",
                "seller": "john_seller",
                "starting_price": Decimal("400.00"),
                "end_offset_days": -2,
                "is_active": False,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/playstation,ps5,gaming",
            },
            {
                "title": "Signed Michael Jordan Jersey",
                "description": (
                    "Authentic Chicago Bulls #23 jersey signed by Michael Jordan himself. "
                    "Comes with a certificate of authenticity from JSA. Frame not included. "
                    "A must-have for any serious sports memorabilia collection."
                ),
                "category": "sports",
                "seller": "jane_seller",
                "starting_price": Decimal("1500.00"),
                "end_offset_days": -4,
                "is_active": False,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/basketball,jersey,sports",
            },

            # --- ACTIVE AUCTIONS (end_time in the future) ---
            {
                "title": "MacBook Pro M3 Max 16-inch",
                "description": (
                    "Brand new MacBook Pro with M3 Max chip, 36GB unified memory, 1TB SSD. "
                    "Space Black color. Still sealed in original packaging. "
                    "Full Apple warranty until 2027. Perfect for professionals and creatives."
                ),
                "category": "electronics",
                "seller": "john_seller",
                "starting_price": Decimal("2200.00"),
                "end_offset_days": 10,
                "is_active": True,
                "is_featured": True,
                "image_url": "https://loremflickr.com/800/600/macbook,pro,laptop",
            },
            {
                "title": "Original Abstract Oil Painting",
                "description": (
                    "A vibrant 36x48 inch abstract oil painting on stretched canvas by emerging artist "
                    "Maria Santos. Bold colors and dynamic composition that commands attention in any room. "
                    "Gallery-wrapped edges, ready to hang."
                ),
                "category": "art-collectibles",
                "seller": "jane_seller",
                "starting_price": Decimal("800.00"),
                "end_offset_days": 7,
                "is_active": True,
                "is_featured": True,
                "image_url": "https://loremflickr.com/800/600/abstract,painting,art",
            },
            {
                "title": "Antique Victorian Armchair",
                "description": (
                    "Beautifully restored Victorian-era armchair with original carved oak frame. "
                    "Reupholstered in premium emerald green velvet. Seat height 18 inches. "
                    "A statement piece for any living room or study."
                ),
                "category": "home-garden",
                "seller": "john_seller",
                "starting_price": Decimal("350.00"),
                "end_offset_days": 5,
                "is_active": True,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/armchair,victorian,furniture",
            },
            {
                "title": "First Edition Harry Potter Book",
                "description": (
                    "Harry Potter and the Philosopher's Stone, first UK edition, first printing "
                    "by Bloomsbury 1997. Hardback with dust jacket in very good condition. "
                    "One of the most sought-after modern first editions in the world."
                ),
                "category": "books-media",
                "seller": "jane_seller",
                "starting_price": Decimal("250.00"),
                "end_offset_days": 12,
                "is_active": True,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/harry,potter,book",
            },
            {
                "title": "Diamond Engagement Ring 2ct",
                "description": (
                    "Stunning 2-carat round brilliant cut diamond ring set in 14k white gold. "
                    "VS2 clarity, F color. Comes with GIA certification. "
                    "A timeless symbol of love and commitment."
                ),
                "category": "jewelry",
                "seller": "jane_seller",
                "starting_price": Decimal("5000.00"),
                "end_offset_days": 14,
                "is_active": True,
                "is_featured": True,
                "image_url": "https://loremflickr.com/800/600/diamond,ring,engagement",
            },
            {
                "title": "Handmade Ceramic Vase Set",
                "description": (
                    "Set of three hand-thrown ceramic vases in earthy tones (terracotta, sage, cream). "
                    "Each vase is approximately 8-12 inches tall. Perfect for fresh or dried flower arrangements. "
                    "Handmade by local artisan potter."
                ),
                "category": "home-garden",
                "seller": "jane_seller",
                "starting_price": Decimal("120.00"),
                "end_offset_days": 6,
                "is_active": True,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/ceramic,vase,handmade",
            },
            {
                "title": "Vintage Levi's Denim Jacket",
                "description": (
                    "Classic Levi's Type III trucker jacket from the 1990s. Size Medium. "
                    "Beautiful natural fading and patina that can only come from decades of wear. "
                    "No rips or stains. An iconic piece of Americana."
                ),
                "category": "fashion",
                "seller": "john_seller",
                "starting_price": Decimal("180.00"),
                "end_offset_days": 8,
                "is_active": True,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/denim,jacket,levis",
            },
            {
                "title": "Trek Mountain Bike 2024",
                "description": (
                    "Trek Marlin 7 mountain bike, 2024 model. 29-inch wheels, Shimano Deore "
                    "1x10 drivetrain. Hydraulic disc brakes. Only ridden twice on trails. "
                    "Retail price $1,100. Includes a helmet and water bottle cage."
                ),
                "category": "sports",
                "seller": "john_seller",
                "starting_price": Decimal("900.00"),
                "end_offset_days": 9,
                "is_active": True,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/mountain,bike,trek",
            },
            {
                "title": "Noise Cancelling Headphones",
                "description": (
                    "Sony WH-1000XM5 wireless noise cancelling headphones in black. "
                    "Industry-leading noise cancellation, 30-hour battery life, multipoint connection. "
                    "Used for one month, in pristine condition with original packaging."
                ),
                "category": "electronics",
                "seller": "jane_seller",
                "starting_price": Decimal("250.00"),
                "end_offset_days": 4,
                "is_active": True,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/headphones,sony,noise-cancelling",
            },
            {
                "title": "Oil Painting Landscape",
                "description": (
                    "A serene 24x36 inch oil painting of a mountain landscape at sunset. "
                    "Warm golden tones blended with cool blues and purples. "
                    "Painted on premium linen canvas. Signed by the artist in the lower right corner."
                ),
                "category": "art-collectibles",
                "seller": "john_seller",
                "starting_price": Decimal("600.00"),
                "end_offset_days": 11,
                "is_active": True,
                "is_featured": False,
                "image_url": "https://loremflickr.com/800/600/landscape,oil-painting,sunset",
            },
        ]

        auctions = {}
        for data in auctions_data:
            slug = data["title"].lower().replace("'", "").replace("&", "and")
            slug = slug.replace(" ", "-").replace("--", "-")
            for ch in ["--", " ", "&", "'", "\"", ".", ",", "(", ")", "–", "/"]:
                slug = slug.replace(ch, "-")
            slug = slug.strip("-")

            image_file = None
            image_url = data.get("image_url")
            if image_url:
                try:
                    self.stdout.write(f"  Downloading image for '{data['title']}'...")
                    response = urllib.request.urlopen(image_url, timeout=10)
                    image_data = response.read()
                    filename = f"{slug}.jpg"
                    image_file = ContentFile(image_data, name=filename)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Could not download image: {e}"))
                    image_file = None

            auction, created = Auction.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": data["title"],
                    "description": data["description"],
                    "category": categories[data["category"]],
                    "seller": users[data["seller"]],
                    "starting_price": data["starting_price"],
                    "current_price": data["starting_price"],
                    "start_time": now - timedelta(days=7),
                    "end_time": now + timedelta(days=data["end_offset_days"]),
                    "is_active": data["is_active"],
                    "is_featured": data["is_featured"],
                },
            )
            if created and image_file:
                auction.image.save(f"{slug}.jpg", image_file, save=True)
            auctions[data["title"]] = auction
            status = "created" if created else "already exists"
            active_label = " [ACTIVE]" if data["is_active"] else " [ENDED]"
            featured_label = " [FEATURED]" if data["is_featured"] else ""
            self.stdout.write(
                f"  Auction '{data['title']}' {status}{active_label}{featured_label}."
            )

        return auctions

    # ------------------------------------------------------------------
    # Bids
    # ------------------------------------------------------------------
    def create_bids(self, users, auctions):
        self.stdout.write("Creating bids...")

        buyers = [users["mike_buyer"], users["sarah_buyer"], users["alex_buyer"]]
        now = timezone.now()

        bids_spec = [
            # --- Bids on ENDED auctions (last bid must match current_price) ---

            # Vintage Rolex Submariner Watch — ended, highest bid wins
            ("Vintage Rolex Submariner Watch", "mike_buyer", Decimal("4800.00"), -6),
            ("Vintage Rolex Submariner Watch", "sarah_buyer", Decimal("5100.00"), -5),
            ("Vintage Rolex Submariner Watch", "mike_buyer", Decimal("5400.00"), -5),
            ("Vintage Rolex Submariner Watch", "alex_buyer", Decimal("5700.00"), -4),
            ("Vintage Rolex Submariner Watch", "sarah_buyer", Decimal("6100.00"), -3),

            # 2019 Tesla Model 3 — ended
            ("2019 Tesla Model 3 Long Range", "alex_buyer", Decimal("29500.00"), -4),
            ("2019 Tesla Model 3 Long Range", "mike_buyer", Decimal("30500.00"), -3),
            ("2019 Tesla Model 3 Long Range", "sarah_buyer", Decimal("31200.00"), -2),

            # PS5 Bundle — ended
            ("Sony PlayStation 5 Bundle", "sarah_buyer", Decimal("450.00"), -3),
            ("Sony PlayStation 5 Bundle", "alex_buyer", Decimal("500.00"), -2),
            ("Sony PlayStation 5 Bundle", "mike_buyer", Decimal("540.00"), -1),

            # Signed Jordan Jersey — ended
            ("Signed Michael Jordan Jersey", "mike_buyer", Decimal("1800.00"), -5),
            ("Signed Michael Jordan Jersey", "alex_buyer", Decimal("2100.00"), -4),

            # --- Bids on ACTIVE auctions ---

            # MacBook Pro M3 Max — active
            ("MacBook Pro M3 Max 16-inch", "sarah_buyer", Decimal("2400.00"), -1),
            ("MacBook Pro M3 Max 16-inch", "alex_buyer", Decimal("2600.00"), 0),
            ("MacBook Pro M3 Max 16-inch", "mike_buyer", Decimal("2800.00"), 1),

            # Original Abstract Oil Painting — active
            ("Original Abstract Oil Painting", "mike_buyer", Decimal("950.00"), -2),
            ("Original Abstract Oil Painting", "alex_buyer", Decimal("1100.00"), 0),

            # Antique Victorian Armchair — active
            ("Antique Victorian Armchair", "sarah_buyer", Decimal("400.00"), -1),
            ("Antique Victorian Armchair", "alex_buyer", Decimal("450.00"), 1),

            # Diamond Engagement Ring — active
            ("Diamond Engagement Ring 2ct", "mike_buyer", Decimal("5500.00"), -3),
            ("Diamond Engagement Ring 2ct", "alex_buyer", Decimal("6200.00"), -1),
            ("Diamond Engagement Ring 2ct", "sarah_buyer", Decimal("6800.00"), 1),

            # Trek Mountain Bike — active
            ("Trek Mountain Bike 2024", "alex_buyer", Decimal("950.00"), -2),
            ("Trek Mountain Bike 2024", "sarah_buyer", Decimal("1050.00"), 0),
        ]

        bid_count = 0
        for auction_title, bidder_username, amount, offset_days in bids_spec:
            auction = auctions[auction_title]
            bidder = users[bidder_username]

            bid, created = Bid.objects.get_or_create(
                auction=auction,
                bidder=bidder,
                amount=amount,
            )
            if created:
                bid_count += 1

            # Update the auction's current_price to the highest bid
            if amount > auction.current_price:
                auction.current_price = amount
                auction.save(update_fields=["current_price"])

            status = "created" if created else "already exists"
            self.stdout.write(
                f"  Bid ${amount} by {bidder_username} on '{auction_title}' {status}."
            )

        self.stdout.write(self.style.NOTICE(f"  Total bids placed: {bid_count}"))

    # ------------------------------------------------------------------
    # Payments & Transactions
    # ------------------------------------------------------------------
    def create_payments(self, users, auctions):
        self.stdout.write("Creating payments and transactions...")

        payment_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]

        ended_auctions_with_bids = [
            "Vintage Rolex Submariner Watch",
            "2019 Tesla Model 3 Long Range",
            "Sony PlayStation 5 Bundle",
            "Signed Michael Jordan Jersey",
        ]

        # Map auction titles to winning bidders
        winners = {
            "Vintage Rolex Submariner Watch": "sarah_buyer",
            "2019 Tesla Model 3 Long Range": "sarah_buyer",
            "Sony PlayStation 5 Bundle": "mike_buyer",
            "Signed Michael Jordan Jersey": "alex_buyer",
        }

        payment_count = 0
        for idx, auction_title in enumerate(ended_auctions_with_bids):
            auction = auctions[auction_title]
            winner_username = winners[auction_title]
            buyer = users[winner_username]
            seller = auction.seller

            txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            method = payment_methods[idx % len(payment_methods)]

            payment, created = Payment.objects.get_or_create(
                auction=auction,
                defaults={
                    "buyer": buyer,
                    "seller": seller,
                    "amount": auction.current_price,
                    "payment_method": method,
                    "status": "COMPLETED",
                    "transaction_id": txn_id,
                },
            )

            if created:
                payment_count += 1
                # Create the corresponding payment transaction
                Transaction.objects.get_or_create(
                    payment=payment,
                    type="payment",
                    amount=payment.amount,
                    defaults={
                        "description": (
                            f"Payment of ${payment.amount} for '{auction.title}' "
                            f"from {buyer.username} to {seller.username}."
                        ),
                    },
                )
                # Create the platform fee transaction (5% fee)
                fee_amount = (payment.amount * Decimal("0.05")).quantize(Decimal("0.01"))
                Transaction.objects.get_or_create(
                    payment=payment,
                    type="fee",
                    amount=fee_amount,
                    defaults={
                        "description": (
                            f"Platform fee (5%) of ${fee_amount} for transaction {txn_id}."
                        ),
                    },
                )

            status_label = "created" if created else "already exists"
            self.stdout.write(
                f"  Payment {txn_id} (${auction.current_price}) "
                f"for '{auction_title}' {status_label}."
            )

        self.stdout.write(
            self.style.NOTICE(f"  Total payments created: {payment_count}")
        )
