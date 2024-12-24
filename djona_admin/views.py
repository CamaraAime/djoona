from glob import escape
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
import hashlib
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from djona_admin.models import CarouselImage, EtatVehicule, Image, PieceDetache, Produit
from django.db.models import Q
from collections import Counter
from collections import defaultdict
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Count, Min



def validate_price_filters(min_price, max_price):
    if min_price and not min_price.isdigit():
        return "Le prix minimum doit être un nombre."
    if max_price and not max_price.isdigit():
        return "Le prix maximum doit être un nombre."
    if min_price.isdigit() and max_price.isdigit() and int(min_price) > int(max_price):
        return "Le prix minimum ne peut pas être supérieur au prix maximum."
    return None

def filter_products(base_queryset, filters):
    return base_queryset.filter(filters) if filters else base_queryset


def IndexPage(request):
    list_products = Produit.objects.all()
    
    whatsapp_message = None
    if list_products.exists():
        whatsapp_message = list_products.first().whatsapp_message()

    # Statuts
    vente_statut = EtatVehicule.objects.filter(nom='vente').first()
    location_statut = EtatVehicule.objects.filter(nom='location').first()
    
    all_filtered_products = list_products.filter(
        Q(statut=vente_statut) | Q(statut=location_statut)
    )

    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    selected_type = request.GET.get('type', '').strip().lower()

    error_message = validate_price_filters(min_price, max_price)

    if error_message:
        filters = Q() 
    else:
        filters = Q()
        # Appliquer les filtres de prix
        if min_price.isdigit():
            filters &= Q(prix__gte=int(min_price))
        if max_price.isdigit():
            filters &= Q(prix__lte=int(max_price))
        # Appliquer le filtre de type
        if selected_type in ["occasion", "neuve"]:
            filters &= Q(type__iexact=selected_type)

    # Filtrage des produits
    filtered_products = filter_products(all_filtered_products, filters)
    vente_products = filtered_products.filter(statut=vente_statut)

    # Message d'erreur si aucun produit ne correspond
    if not error_message and not filtered_products.exists():
        error_message = "Aucun véhicule ne correspond aux critères de recherche."

    # Regroupement des produits par marque
    grouped_products = defaultdict(list)
    for product in filtered_products:
        grouped_products[product.marque].append(product)

    # Récupération des valeurs distinctes
    unique_marques = list_products.values_list('marque', flat=True).distinct()
    unique_carrosseries = list_products.values_list('type', flat=True).distinct()
    unique_boites = list_products.values_list('transmission', flat=True).distinct()
    unique_carburants = list_products.values_list('carburant', flat=True).distinct()

    # Comptage des types
    type_counts = Counter(product.type.lower() for product in vente_products if product.type)

    # Fonction pour image
    def get_image_count_and_first_url(product):
        return product.image_count(), product.first_image_url()

    # Contexte pour le rendu
    context = {
        "list_products": filtered_products,
        "unique_titles": list(grouped_products.keys()),
        "message": error_message,
        "type_counts": list(type_counts.items()),
        "grouped_products": grouped_products,
        "unique_marques": unique_marques,
        "unique_type": unique_carrosseries,
        "unique_transmission": unique_boites,
        "unique_carburants": unique_carburants,
        "first_image_urls": [get_image_count_and_first_url(product)[1] for product in filtered_products],
        "image_counts": [get_image_count_and_first_url(product)[0] for product in filtered_products],
        "min_price": min_price,  # Assurez-vous que ces variables sont passées
        "max_price": max_price,  # Assurez-vous que ces variables sont passées
        "selected_type": selected_type,
        "whatsapp_message": whatsapp_message,
    }

    return render(request, "index.html", context)



def searchCar(request):
    # Récupération des paramètres de la requête
    marque = request.GET.get('marque', '').strip()
    carrosserie = request.GET.get('type', '').strip()
    boite = request.GET.get('transmission', '').strip()
    carburant = request.GET.get('carburant', '').strip()

    # Gestion des messages d'erreur
    error_messages = {
        'marque': None,
        'type': None,
        'transmission': None,
        'carburant': None,
    }

    # Préparation des filtres
    filtres = Q()
    if marque:
        filtres &= Q(marque__exact=marque)
        if not Produit.objects.filter(marque__exact=marque).exists():
            error_messages['marque'] = f"Aucune marque ne correspond à '{marque}'."

    if carrosserie:
        filtres &= Q(type__exact=carrosserie)
        if not Produit.objects.filter(type__exact=carrosserie).exists():
            error_messages['type'] = f"Aucun type de carrosserie ne correspond à '{carrosserie}'."

    if boite:
        filtres &= Q(transmission__exact=boite)
        if not Produit.objects.filter(transmission__exact=boite).exists():
            error_messages['transmission'] = f"Aucune transmission ne correspond à '{boite}'."

    if carburant:
        filtres &= Q(carburant__exact=carburant)
        if not Produit.objects.filter(carburant__exact=carburant).exists():
            error_messages['carburant'] = f"Aucun carburant ne correspond à '{carburant}'."

    # Filtrage des produits
    produits = Produit.objects.filter(filtres) if filtres else Produit.objects.all()

    # Gestion du message si aucun produit trouvé
    message = None
    if not produits.exists():
        message = "Aucun véhicule ne correspond à vos critères."

    # Pagination des résultats
    paginator = Paginator(produits, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Récupération des valeurs uniques
    unique_marques = Produit.objects.values_list('marque', flat=True).distinct()
    unique_carrosseries = Produit.objects.values_list('type', flat=True).distinct()
    unique_boites = Produit.objects.values_list('transmission', flat=True).distinct()
    unique_carburants = Produit.objects.values_list('carburant', flat=True).distinct()

    # Contexte pour le template
    context = {
        'produits': produits,
        'message': message,
        'error_messages': error_messages, 
        "is_location_page": False,
        "is_piece_detache_page": False, 
        'is_recherche_vehicule_page': True,
        "list_products": page_obj.object_list,
        "page_obj": page_obj,
        "unique_marques": unique_marques,
        "unique_carrosseries": unique_carrosseries,
        "unique_boites": unique_boites,
        "unique_carburants": unique_carburants,
    }

    return render(request, 'recherchevehicule.html', context)




def AchatPage(request):
    list_products = Produit.objects.filter(statut__nom__iexact='vente')
    images = CarouselImage.objects.all()
    
    message = "Aucun véhicule en vente pour l'instant." if not list_products.exists() else ""
    
    paginator = Paginator(list_products, 6) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in page_obj.object_list:
        product.hashed_id = hashlib.sha256(str(product.id).encode('utf-8')).hexdigest()

    context = {
        "list_products": page_obj.object_list,
        "message": message,
        "page_obj": page_obj,
        'images': images,
    }
    return render(request, "achat.html", context)




def LocationPage(request):
    list_products = Produit.objects.filter(statut__nom__iexact='location') 
    images = CarouselImage.objects.all()
   
    if list_products.count() < 1:
        message = "Aucun véhicule en location pour l'instant."
    else:
        message = ""

    # Pagination
    paginator = Paginator(list_products, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in page_obj.object_list:
        product.hashed_id = hashlib.sha256(str(product.id).encode('utf-8')).hexdigest()

    context = {
        "message": message,
        "page_obj": page_obj,
        "is_location_page": True,
        "is_piece_detache_page": False, 
        'is_recherche_vehicule_page': False,
        'images': images,
    }
    return render(request, "location.html", context)



def piece_detache(request):
    images = PieceDetache.objects.all()    

    if not images.exists():
        message = "Aucune pièce détachée disponible pour le moment."
    else:
        message = None

    context = {
        'message': message, 
    }
    
    return render(request, "piece-detache.html", context)





def ProductDetailPage(request, id):
    product = get_object_or_404(Produit, id=id)
    whatsapp_message = product.whatsapp_message()
    image_urls = [image.image.url for image in product.images.all()]
    images = product.images.all()

    context = {
        "product": product,
        "whatsapp_message": whatsapp_message,
        "image_urls": image_urls,
        "images": images
    }
    return render(request, "product_detail.html", context)





def AboutPage(request):
    return render(request, "about.html")



def RejoindrePage(request):
    return render(request, "rejoindre.html")




def ContactConsPage(request):
    return render(request, "contactCons.html")


def carrosseriePage(request):
    type_counts = (
        Produit.objects.values('type')
        .annotate(count=Count('id'))
        .order_by('type')
    )

    first_images = {
        item['type']: Produit.objects.filter(type=item['type'])
        .values_list('images', flat=True)
        .first() or '/static/images/default-car.png'
        for item in type_counts
    }

    context = {
        'type_counts': type_counts,
        'first_images': first_images, 
    }
    return render(request, 'carrosseriePlus.html', context)



def common_view(request):
    images = CarouselImage.objects.all()
    return render(request, 'slide.html', {'images': images})



def ContactPage(request, product_id):
    product = get_object_or_404(Produit, id=product_id)

    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        numero = request.POST.get('numero', '').strip()
        ville = request.POST.get('ville', '').strip()
        email = request.POST.get('email', '').strip()
        description = request.POST.get('description', '').strip()

        if not all([nom, prenom, numero, ville, email, description]):
            messages.error(request, "Tous les champs sont obligatoires.")
            return HttpResponseRedirect(reverse('contact', args=[product.id]))

        subject = f"Demande de contact pour {product.marque} {product.modele}"
        message = (
            f"Nom : {escape(nom)}\n"
            f"Prénom : {escape(prenom)}\n"
            f"Numéro de téléphone : {escape(numero)}\n"
            f"Ville : {escape(ville)}\n"
            f"E-mail : {escape(email)}\n"
            f"Nombre de véhicules : {escape(description)}\n"
        )
        recipient = "contacts@djona.net"

        try:
            send_mail(
                subject,
                message,
                'contacts@djona.net',
                [recipient],
                fail_silently=False,
            )
            messages.success(
                request,
                f"M. {nom}, votre message a bien été envoyé à Djona concernant votre désir de vente de vos {description} véhicule(s).",
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
            messages.error(
                request,
                "Une erreur est survenue lors de l'envoi de votre message. Veuillez réessayer.",
            )

        return redirect('contact', product_id=product.id)

    return render(request, 'contactVehi.html', {'product': product})

