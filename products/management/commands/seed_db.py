import random

from django.core.management.base import BaseCommand

from products.models.category import ProductCategory
from products.models.product import Product
from products.models.sku import ProductSKU
from suppliers.models.supplier import Supplier


class Command(BaseCommand):
    help = 'Seeds the database with initial data (Indonesia Context)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Categories (Indonesia)
        categories = [
            "Elektronik", "Komputer & Laptop", "Peralatan Rumah Tangga", "Seni & Kerajinan", "Otomotif",
            "Perlengkapan Bayi", "Kecantikan & Perawatan Diri", "Fashion Wanita", "Fashion Pria", "Kesehatan"
        ]
        
        for name in categories:
            category, created = ProductCategory.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Created category: {name}')
            else:
                self.stdout.write(f'Category already exists: {name}')
        
        # Suppliers (Indonesia)
        suppliers_data = [
            {"name": "PT Sumber Makmur Jaya", "address": "Jl. Sudirman No. 123, Jakarta Pusat", "phone": "0215550101", "email": "kontak@sumbermakmur.co.id"},
            {"name": "CV Abadi Sentosa", "address": "Jl. Tunjungan No. 45, Surabaya", "phone": "0315550102", "email": "info@abadisentosa.com"},
            {"name": "PT Teknologi Nusantara", "address": "Jl. Dago No. 88, Bandung", "phone": "0225550103", "email": "sales@teknus.co.id"},
            {"name": "UD Berkah Alam", "address": "Jl. Pemuda No. 10, Semarang", "phone": "0245550104", "email": "support@berkahalam.com"},
            {"name": "PT Sinar Harapan", "address": "Jl. Gatot Subroto No. 202, Medan", "phone": "0615550105", "email": "kontak@sinarharapan.co.id"},
            {"name": "CV Maju Bersama", "address": "Jl. Pantai Losari No. 303, Makassar", "phone": "04115550106", "email": "admin@majubersama.com"},
            {"name": "PT Global Elektronik", "address": "Mangga Dua Mall Lt. 3, Jakarta Utara", "phone": "0215550107", "email": "sales@globalelektronik.com"},
            {"name": "UD Tani Sejahtera", "address": "Jl. Ijen No. 404, Malang", "phone": "03415550108", "email": "info@tanisejahtera.com"},
            {"name": "PT Tekstil Indonesia", "address": "Jl. Slamet Riyadi No. 505, Solo", "phone": "02715550109", "email": "marketing@tekstilindo.co.id"},
            {"name": "CV Karya Mandiri", "address": "Jl. Malioboro No. 707, Yogyakarta", "phone": "02745550110", "email": "hello@karyamandiri.com"},
        ]
        
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=data["name"],
                defaults={
                    "address": data["address"],
                    "phone": data["phone"],
                    "email": data["email"]
                }
            )
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')
            else:
                self.stdout.write(f'Supplier already exists: {supplier.name}')

        # Products (Indonesia)
        products_data = [
            {"name": "Ponsel Pintar Nusantara X", "description": "Smartphone canggih buatan lokal dengan fitur AI", "price": 3000000, "category": "Elektronik"},
            {"name": "Laptop Merah Putih Pro", "description": "Laptop performa tinggi untuk profesional", "price": 15000000, "category": "Komputer & Laptop"},
            {"name": "Lampu Pintar Hemat Energi", "description": "Lampu LED dengan kontrol WiFi dan hemat listrik", "price": 150000, "category": "Peralatan Rumah Tangga"},
            {"name": "Set Cat Akrilik Pelangi", "description": "24 warna cat akrilik berkualitas tinggi", "price": 75000, "category": "Seni & Kerajinan"},
            {"name": "Pengkilap Mobil Kinclong", "description": "Wax premium untuk perlindungan cat mobil maksimal", "price": 50000, "category": "Otomotif"},
            {"name": "Monitor Bayi Aman", "description": "Monitor video dengan penglihatan malam dan sensor suara", "price": 1200000, "category": "Perlengkapan Bayi"},
            {"name": "Krim Wajah Mutiara", "description": "Krim pelembab dengan ekstrak mutiara alami", "price": 85000, "category": "Kecantikan & Perawatan Diri"},
            {"name": "Gamis Batik Modern", "description": "Gamis batik tulis asli Pekalongan, bahan katun primisima", "price": 250000, "category": "Fashion Wanita"},
            {"name": "Jaket Kulit Garut", "description": "Jaket kulit domba asli buatan pengrajin Garut", "price": 1500000, "category": "Fashion Pria"},
            {"name": "Blender Jus Sehat", "description": "Blender kecepatan tinggi untuk smoothie dan bumbu", "price": 450000, "category": "Kesehatan"},
        ]

        for data in products_data:
            category = ProductCategory.objects.get(name=data["category"])
            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "price": data["price"],
                    "category": category
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')
            
            # Create SKU for the product
            if not ProductSKU.objects.filter(product=product).exists():
                sku_code = f"{random.randint(100000000000, 999999999999)}"
                
                # Ensure uniqueness
                while ProductSKU.objects.filter(sku=sku_code).exists():
                    sku_code = f"{random.randint(100000000000, 999999999999)}"
                
                ProductSKU.objects.create(
                    product=product,
                    sku=sku_code,
                    stock=random.randint(10, 100)
                )
                self.stdout.write(f'Created SKU for {product.name}: {sku_code}')
            else:
                self.stdout.write(f'SKU already exists for product: {product.name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with Indonesian data'))
