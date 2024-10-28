# Create your models here.
from django.contrib.auth.models import User
from django.db import models


# Modelo Brand
class Brand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Modelo Category
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Modelo Location
class Location(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Modelo State
class State(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Modelo Product
class Product(models.Model):
    name = models.CharField(max_length=255)

    # Relación con la clase Brand (ForeignKey)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    model = models.CharField(max_length=255, blank=True, null=True)

    bar_code = models.CharField(max_length=255, blank=True, null=True)

    serial_number = models.CharField(max_length=100, blank=True, null=True)

    # Relación con la clase Category (ForeignKey)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # Relación con la clase State (ForeignKey)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.model}'


# Modelo Inventory
class Inventory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    location = models.ForeignKey('Location', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f'{self.product.name} - {self.quantity} units at {self.location.name}'


# Modelo Income (Ingresos de productos)
class Income(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    delivery_order = models.FileField(upload_to='delivery_orders/', blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        # Actualizar el inventario con el ingreso
        inventory, created = Inventory.objects.get_or_create(
            product=self.product,
            location=self.location,
            defaults={'quantity': 0}
        )
        inventory.quantity += self.quantity
        inventory.save()

        super().save(*args, **kwargs)  # Guardar la transacción Income


class Outcome(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)  # Referencia a Inventory
    qty = models.PositiveIntegerField()
    date_time = models.DateTimeField(auto_now_add=True)
    dest_location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='destination_location')
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        # Disminuir la cantidad en el inventario actual

        if self.inventory.quantity >= self.qty:
            self.inventory.quantity -= self.qty
            self.inventory.save()
        else:
            raise ValueError('La cantidad en inventario no es suficiente para este egreso')

        # Si hay una ubicación de destino, crear o actualizar el inventario en esa ubicación
        if self.dest_location:
            dest_inventory, created = Inventory.objects.get_or_create(
                product=self.inventory.product,
                location=self.dest_location,
                defaults={'quantity': 0}
            )
            dest_inventory.quantity += self.qty
            dest_inventory.save()

        super().save(*args, **kwargs)  # Guardar la transacción Outcome

    def __str__(self):
        return f'Egreso: {self.inventory.name} - {self.qty} units from {self.inventory.location.name}'
