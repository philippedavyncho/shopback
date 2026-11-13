from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from categories.models import Category
from inventory.models import Stock
from products.models import Brand, Product, ProductVariant


DEMO_PRODUCTS = [
    ("Smartphone Nova 128 Go", "Smartphones", "Nova", "Un smartphone fluide avec ecran lumineux, appareil photo precis et batterie longue duree.", "Noir - 128 Go", "DEMO-NOVA-128", "189900", "219900", 18),
    ("Ordinateur portable Atlas 14 pouces", "Ordinateurs", "Atlas", "Un ordinateur leger pour le travail, les etudes et les deplacements du quotidien.", "16 Go - 512 Go SSD", "DEMO-ATLAS-14", "429900", None, 7),
    ("Ecouteurs sans fil Pulse", "Accessoires electroniques", "Pulse", "Des ecouteurs compacts avec boitier de charge et son equilibre pour vos journees.", "Blanc", "DEMO-PULSE-WH", "24900", "29900", 32),
    ("Refrigerateur compact Fresh 230 L", "Refrigerateur", "Fresh", "Un refrigerateur pratique et silencieux, adapte aux cuisines familiales.", "Inox - 230 L", "DEMO-FRESH-230", "279900", None, 4),
    ("Sac urbain Nomade", "Sacs", "Nomade", "Un sac resistant avec plusieurs rangements pour transporter vos essentiels.", "Vert olive - 22 L", "DEMO-NOMADE-22", "32900", None, 14),
    ("Montre connectee Move", "Montres connectees", "Move", "Suivez vos activites, vos notifications et votre rythme quotidien en un coup d'oeil.", "Noir - Bracelet ajustable", "DEMO-MOVE-BK", "59900", "69900", 11),
    ("Baskets legeres Sprint", "Chaussures", "Sprint", "Des baskets confortables et legeres pour marcher et bouger toute la journee.", "Blanc - Taille 40", "DEMO-SPRINT-40", "44900", None, 9),
    ("Tablette compacte Reader 10 pouces", "Tablettes", "Reader", "Une tablette polyvalente pour lire, regarder vos contenus et consulter vos documents.", "Gris - 64 Go", "DEMO-READER-10", "119900", None, 6),
    ("Polo femme Coton", "Vetements femme", "Coton & Co", "Un polo confortable facile a porter au quotidien.", "Bleu - Taille M", "DEMO-POLO-F-M", "16900", None, 15),
    ("Chemise homme Classique", "Vetements homme", "Classique", "Une chemise polyvalente pour le travail et les sorties.", "Blanc - Taille L", "DEMO-CHEMISE-H-L", "22900", None, 12),
    ("Ballon de football Match", "Sport", "Match", "Un ballon resistant pour les entrainements et les matchs entre amis.", "Taille 5", "DEMO-BALLON-5", "12900", "15900", 20),
    ("Telephone Neo 64 Go", "Telephone", "Neo", "Un telephone simple et pratique avec double SIM et batterie longue duree.", "Noir - 64 Go", "DEMO-NEO-64", "79900", None, 10),
    ("Enceinte portable Tempo", "Electronique", "Tempo", "Une enceinte compacte sans fil pour ecouter votre musique a la maison ou dehors.", "Noir", "DEMO-TEMPO-BK", "29900", "34900", 17),
    ("Lave-linge Essentiel 7 kg", "Electromenager", "Essentiel", "Un lave-linge pratique avec plusieurs programmes pour le linge du quotidien.", "Blanc - 7 kg", "DEMO-LAVE-LINGE-7", "219900", None, 5),
    ("Blender Mix 1,5 L", "Electromenager", "Mix", "Un blender polyvalent pour preparer smoothies, sauces et soupes.", "Noir - 1,5 L", "DEMO-BLENDER-15", "24900", None, 13),
]


class Command(BaseCommand):
    help = "Ajoute des categories et articles de demonstration sans doublons."

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        updated = 0
        for name, category_name, brand_name, description, variant_name, sku, price, compare, quantity in DEMO_PRODUCTS:
            category_slug = slugify(category_name)
            category, _ = Category.objects.get_or_create(
                slug=category_slug,
                defaults={"name": category_name, "is_active": True},
            )
            brand, _ = Brand.objects.get_or_create(name=brand_name)
            product, was_created = Product.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "description": description,
                    "category": category,
                    "brand": brand,
                    "status": Product.Status.ACTIVE,
                },
            )
            created += int(was_created)
            updated += int(not was_created)
            variant, _ = ProductVariant.objects.update_or_create(
                sku=sku,
                defaults={
                    "product": product,
                    "name": variant_name,
                    "price": price,
                    "compare_at_price": compare,
                    "currency": "XOF",
                    "is_active": True,
                },
            )
            Stock.objects.update_or_create(
                variant=variant,
                defaults={"quantity": quantity, "reserved": 0},
            )
        self.stdout.write(self.style.SUCCESS(
            f"Demonstration prete : {created} article(s) ajoute(s), "
            f"{updated} actualise(s), avec variantes et stock."
        ))
