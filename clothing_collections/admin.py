from django.contrib import admin

from . import models

@admin.register(models.Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = [
        "label",
        "shortcut",
    ]


@admin.register(models.Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "for_bid",
        "min_bid_add_on",
    ]


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        "batch",
        "code",
        "price",
        "size",
        "brand",
    ]
    list_filter = ["batch", "brand", "size"]
