# views.py

from .models import Income, Outcome, Brand, Location, Product, Inventory, Category

from .forms import IncomeForm, OutcomeForm

from django.db.models import Count
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.http import HttpResponse

from openpyxl.workbook import Workbook

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


@login_required
def create_income(request):

    # Búsqueda de producto
    search_query = request.GET.get('search_query', '')
    products = None

    if search_query:
        products = Product.objects.filter(
            Q(name__icontains=search_query) |  # Búsqueda por nombre
            Q(model__icontains=search_query) |  # Búsqueda por modelo
            Q(serial_number__icontains=search_query)  # Búsqueda por número de serie
        )

    # Si ya se seleccionó un producto (por ejemplo, después de la búsqueda)
    selected_product_id = request.GET.get('product_id', None)
    selected_product = None

    if selected_product_id:
        selected_product = get_object_or_404(Product, id=selected_product_id)
        print(f"producto seleccionado: {selected_product}")

    # Formulario de ingreso
    if request.method == 'POST':
        form = IncomeForm(request.POST, request.FILES)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user  # Asigna el usuario que crea la transacción
            income.product = selected_product  # Asigna el producto seleccionado
            income.save()  # Llama al método save(), que también actualiza el inventario
            return redirect('inventory_list')  # Redirige a una lista de inventario
    else:
        form = IncomeForm()

    return render(request, 'inventory/create_income.html', {
        'products': products,
        'selected_product': selected_product,
        'form': form,
        'search_query': search_query,
    })


@login_required
def create_outcome(request):
    # Búsqueda de producto en el inventario
    search_query = request.GET.get('search_query', '')
    inventory_items = None

    if search_query:
        # Búsqueda en el inventario por nombre de producto, modelo o número de serie
        inventory_items = Inventory.objects.filter(
            Q(product__name__icontains=search_query) |
            Q(product__model__icontains=search_query) |
            Q(product__serial_number__icontains=search_query),
            quantity__gt=0  # Solo productos con cantidad mayor a 0
        )

    # Si ya se seleccionó un producto del inventario
    selected_inventory_id = request.GET.get('inventory_id', None)
    selected_inventory = None

    if selected_inventory_id:
        selected_inventory = get_object_or_404(Inventory, id=selected_inventory_id)

    # Formulario de salida
    if request.method == 'POST':
        form = OutcomeForm(request.POST)
        if form.is_valid():
            outcome = form.save(commit=False)
            if selected_inventory:
                # Asignar el inventario seleccionado al objeto Outcome
                outcome.inventory = selected_inventory
                outcome.user = request.user  # Asigna el usuario que crea la transacción
                outcome.save()
                return redirect('inventory_list')
            else:
                form.add_error(None, 'No se seleccionó un producto válido del inventario.')
    else:
        form = OutcomeForm()

    return render(request, 'inventory/create_outcome.html', {
        'inventory_items': inventory_items,
        'selected_inventory': selected_inventory,
        'form': form,
        'search_query': search_query,
    })

@login_required
def transaction_list(request):
    # Obtener los parámetros de búsqueda
    transaction_type = request.GET.get('transaction_type', '')  # Valor por defalut, income
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Inicializar lista vacía
    transactions = []

    # Convertir las fechas de cadena a objetos de fecha (si existen)
    if from_date:
        from_date = parse_date(from_date)
    if to_date:
        to_date = parse_date(to_date)

    # Filtrar transacciones por tipo y fechas
    if transaction_type == 'income':
        transactions = Income.objects.all()
    elif transaction_type == 'outcome':
        transactions = Outcome.objects.all()

    # Aplicar el filtro de fechas
    if from_date:
        transactions = transactions.filter(date_time__date__gte=from_date)
    if to_date:
        transactions = transactions.filter(date_time__date__lte=to_date)

    return render(request, 'inventory/transaction_list.html', {
        'transactions': transactions,
        'transaction_type': transaction_type,
        'from_date': from_date,
        'to_date': to_date,
    })


@login_required
def inventory_list(request):
    # Inicializa el queryset de inventario y aplica un orden
    inventories = Inventory.objects.filter(quantity__gt=0).order_by('product_id')

    # Filtros
    product_name = request.GET.get('product_name', None)
    brand_id = request.GET.get('brand', None)
    location_id = request.GET.get('location', None)
    category_id = request.GET.get('category', None)
    min_quantity = request.GET.get('min_quantity', None)
    max_quantity = request.GET.get('max_quantity', None)

    # Filtrar por nombre del producto
    if product_name:
        inventories = inventories.filter(product__name__icontains=product_name)

    # Filtrar por marca
    if brand_id:
        inventories = inventories.filter(product__brand_id=brand_id)

    # Filtrar por ubicación
    if location_id:
        inventories = inventories.filter(location_id=location_id)

    # Filtrar por categoría
    if category_id:
        inventories = inventories.filter(product__category_id=category_id)

    # Filtrar por cantidad mínima
    if min_quantity:
        inventories = inventories.filter(quantity__gte=min_quantity)

    # Filtrar por cantidad máxima
    if max_quantity:
        inventories = inventories.filter(quantity__lte=max_quantity)

    # Comprobar cantidad total de elementos tras filtros
    print("Total items after filtering:", inventories.count())  # Debug

    # Paginación: definir cuántos elementos mostrar por página
    paginator = Paginator(inventories, 6)  # Mostrar cant. elementos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Comprobar número de items en la página actual
    print("Items in current page:", len(page_obj))  # Debug

    # Calcular la suma total de cantidades
    total_quantity = inventories.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Cargar las marcas, ubicaciones y categorías para el formulario de búsqueda
    brands = Brand.objects.all()
    locations = Location.objects.all()
    categories = Category.objects.all()

    return render(request, 'inventory/inventory_list.html', {
        'page_obj': page_obj,
        'inventories': inventories,
        'total_quantity': total_quantity,  # Pasamos la suma total al contexto
        'brands': brands,
        'locations': locations,
        'categories': categories,
    })


@login_required
def dashboard(request):
    # Obtener recuento de elementos por categoría en el inventario
    category_data = (
        Inventory.objects
        .values('product__category__name')
        .annotate(total=Count('id'))
        .order_by('product__category__name')
    )

    # Preparar datos para Chart.js
    labels = [data['product__category__name'] for data in category_data]
    counts = [data['total'] for data in category_data]

    # Obtener recuento de elementos por estado en el inventario
    state_data = (
        Inventory.objects
        .values('product__state__name')
        .annotate(total=Count('id'))
        .order_by('product__state__name')
    )
    state_labels = [data['product__state__name'] for data in state_data]
    state_counts = [data['total'] for data in state_data]

    return render(request, 'dashboard.html', {
        'labels': labels,
        'counts': counts,
        'state_labels': state_labels,
        'state_counts': state_counts,
    })


@login_required
def generate_inventory_pdf(request):
    # Crear un objeto HttpResponse con un tipo de contenido para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'

    # Cambiar la orientación de la página a landscape (apaisada)
    p = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Título del PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, "Reporte de Inventario")

    # Obtener y aplicar los filtros de búsqueda de la vista inventory_list
    product_name = request.GET.get('product_name', None)
    brand_id = request.GET.get('brand', None)
    location_id = request.GET.get('location', None)
    category_id = request.GET.get('category', None)
    min_quantity = request.GET.get('min_quantity', None)
    max_quantity = request.GET.get('max_quantity', None)

    # Filtrar el queryset de inventarios de acuerdo a los filtros
    inventories = Inventory.objects.filter(quantity__gt=0)

    if product_name:
        inventories = inventories.filter(product__name__icontains=product_name)
    if brand_id:
        inventories = inventories.filter(product__brand_id=brand_id)
    if location_id:
        inventories = inventories.filter(location_id=location_id)
    if category_id:
        inventories = inventories.filter(product__category_id=category_id)
    if min_quantity:
        inventories = inventories.filter(quantity__gte=min_quantity)
    if max_quantity:
        inventories = inventories.filter(quantity__lte=max_quantity)

    # Calcular la suma total de cantidades para el filtro aplicado
    total_quantity = inventories.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Generar encabezados de tabla
    p.setFont("Helvetica-Bold", 8)
    p.drawString(50, height - 150, "Producto")
    p.drawString(200, height - 150, "Marca")
    p.drawString(300, height - 150, "Modelo")
    p.drawString(400, height - 150, "Número de serie")
    p.drawString(550, height - 150, "Cantidad")
    p.drawString(600, height - 150, "Ubicación")

    # Posición inicial para la primera fila de datos
    y = height - 170

    # Establecer la fuente para los datos
    p.setFont("Helvetica", 10)

    # Iterar sobre los inventarios y añadir cada uno al PDF
    for inventory in inventories:
        p.drawString(50, y, inventory.product.name or "N/A")
        p.drawString(200, y, inventory.product.brand.name or "N/A")
        p.drawString(300, y, inventory.product.model or "N/A")
        p.drawString(400, y, inventory.product.serial_number or "N/A")
        p.drawString(550, y, str(inventory.quantity))
        p.drawString(600, y, inventory.location.name or "N/A")

        # Mover hacia abajo para la siguiente fila
        y -= 20

        # Verificar si hay suficiente espacio en la página
        if y < 50:  # Espacio mínimo en la parte inferior de la página
            p.showPage()  # Crear una nueva página
            y = height - 100  # Reiniciar la posición Y para la nueva página
            p.setFont("Helvetica", 10)

    # Añadir el total de cantidades al final del PDF
    y -= 30  # Espacio extra antes del total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total de cantidades: {total_quantity}")

    # Guardar el PDF
    p.save()
    return response


@login_required
def generate_inventory_xls(request):
    # Crear un objeto HttpResponse con tipo de contenido de Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.xlsx"'

    # Crear un nuevo libro de Excel y obtener la hoja activa
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte de Inventario"

    # Filtros de búsqueda de la vista inventory_list
    product_name = request.GET.get('product_name', None)
    brand_id = request.GET.get('brand', None)
    location_id = request.GET.get('location', None)
    category_id = request.GET.get('category', None)
    min_quantity = request.GET.get('min_quantity', None)
    max_quantity = request.GET.get('max_quantity', None)

    # Filtrar el queryset de inventarios
    inventories = Inventory.objects.filter(quantity__gt=0)
    if product_name:
        inventories = inventories.filter(product__name__icontains=product_name)
    if brand_id:
        inventories = inventories.filter(product__brand_id=brand_id)
    if location_id:
        inventories = inventories.filter(location_id=location_id)
    if category_id:
        inventories = inventories.filter(product__category_id=category_id)
    if min_quantity:
        inventories = inventories.filter(quantity__gte=min_quantity)
    if max_quantity:
        inventories = inventories.filter(quantity__lte=max_quantity)

    # Calcular el total de cantidades
    total_quantity = inventories.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Escribir encabezados de columna
    headers = ["Producto", "Marca", "Modelo", "Número de serie", "Cantidad", "Ubicación"]
    ws.append(headers)

    # Escribir datos de inventario en el archivo
    for inventory in inventories:
        ws.append([
            inventory.product.name or "N/A",
            inventory.product.brand.name or "N/A",
            inventory.product.model or "N/A",
            inventory.product.serial_number or "N/A",
            inventory.quantity,
            inventory.location.name or "N/A"
        ])

    # Agregar la fila del total al final del listado
    ws.append([])
    ws.append(["", "", "", "Total de cantidades:", total_quantity])

    # Guardar el archivo de Excel en la respuesta
    wb.save(response)
    return response
