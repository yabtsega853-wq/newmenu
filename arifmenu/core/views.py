import io
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
import segno

from .forms import ItemForm, PlaceCreateForm, PlaceForm, SignupForm
from .models import MenuItem, Place


def home(request):
    q = request.GET.get("q", "").strip()
    area = request.GET.get("area", "").strip()
    category = request.GET.get("category", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    ptype = request.GET.get("type", "").strip()
    searching = any([q, area, category, max_price, ptype])
    base = Place.objects.filter(is_active=True)
    places = base
    dishes = MenuItem.objects.none()

    if ptype:
        places = places.filter(place_type=ptype)
    if area:
        places = places.filter(area__iexact=area)
    if q:
        places = places.filter(Q(name__icontains=q) | Q(
            area__icontains=q) | Q(items__name__icontains=q)).distinct()
    if q or category or max_price:
        dishes = MenuItem.objects.filter(
            place__is_active=True, is_available=True).select_related("place")
        if q:
            dishes = dishes.filter(name__icontains=q)
        if ptype:
            dishes = dishes.filter(place__place_type=ptype)
        if area:
            dishes = dishes.filter(place__area__iexact=area)
        if category:
            dishes = dishes.filter(category__iexact=category)
        if max_price:
            try:
                dishes = dishes.filter(price__lte=Decimal(max_price))
            except InvalidOperation:
                pass
        dishes = dishes.order_by("price")[:40]
        if category or max_price:
            ids = {d.place_id for d in dishes}
            places = places.filter(id__in=ids)

    ctx = {
        "q": q, "ptype": ptype, "types": [(k, l, Place.EMOJI[k]) for k, l in Place.TYPES], "area": area, "category": category, "max_price": max_price,
        "searching": searching, "places": places[:60], "dishes": dishes,
        "featured": [] if searching else base.filter(is_featured=True)[:6],
        "areas": base.values_list("area", flat=True).distinct().order_by("area"),
        "categories": MenuItem.objects.filter(place__is_active=True).values_list("category", flat=True).distinct().order_by("category"),
    }
    return render(request, "home.html", ctx)


def place_detail(request, slug):
    place = get_object_or_404(Place, slug=slug)
    if not place.is_active and place.owner != request.user and not request.user.is_staff:
        return render(request, "pending.html", {"place": place}, status=404)
    if place.is_active and place.owner != request.user:
        Place.objects.filter(pk=place.pk).update(views=F("views") + 1)
    grouped = {}
    for it in place.items.all():
        grouped.setdefault(it.category, []).append(it)
    return render(request, "place_detail.html", {"place": place, "grouped": grouped})


def place_qr(request, slug):
    place = get_object_or_404(Place, slug=slug)
    url = request.build_absolute_uri(
        reverse("place_detail", args=[place.slug]))
    buf = io.BytesIO()
    segno.make(url, error="m").save(buf, kind="svg", scale=10, border=2)
    resp = HttpResponse(buf.getvalue(), content_type="image/svg+xml")
    if request.GET.get("download"):
        resp["Content-Disposition"] = f'attachment; filename="{place.slug}-qr.svg"'
    return resp


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("place_create")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard(request):
    return render(request, "dashboard.html", {"places": request.user.places.all()})


@login_required
def place_create(request):
    form = PlaceCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        place = form.save(commit=False)
        place.owner = request.user
        place.save()
        messages.success(
            request, "Great! Now add your menu items. You can add photos and more details below.")
        return redirect("manage_place", slug=place.slug)
    return render(request, "form.html", {"form": form, "title": "Add your place"})


def _own(request, slug):
    if request.user.is_staff:
        return get_object_or_404(Place, slug=slug)
    return get_object_or_404(Place, slug=slug, owner=request.user)


@login_required
def manage_place(request, slug):
    place = _own(request, slug)
    form = PlaceForm(request.POST or None,
                     request.FILES or None, instance=place)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Saved.")
        return redirect("manage_place", slug=place.slug)
    return render(request, "manage_place.html", {"place": place, "form": form, "items": place.items.all()})


@login_required
def item_edit(request, slug, pk=None):
    place = _own(request, slug)
    item = get_object_or_404(MenuItem, pk=pk, place=place) if pk else None
    form = ItemForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.place = place
        obj.save()
        return redirect("manage_place", slug=place.slug)
    return render(request, "form.html", {"form": form, "title": "Edit item" if item else "Add menu item"})


@login_required
@require_POST
def item_toggle(request, slug, pk):
    item = get_object_or_404(MenuItem, pk=pk, place=_own(request, slug))
    item.is_available = not item.is_available
    item.save(update_fields=["is_available"])
    return redirect("manage_place", slug=slug)


@login_required
@require_POST
def item_delete(request, slug, pk):
    get_object_or_404(MenuItem, pk=pk, place=_own(request, slug)).delete()
    return redirect("manage_place", slug=slug)
