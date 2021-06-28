from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def item_image_path(instance, filename):
    return f"{instance.batch.slug}/final/{filename}"

def raw_item_image_path(instance, filename):
    return f"{instance.batch.slug}/raw/{filename}"


class Size(models.Model):
    """
    Clothing size
    """
    label = models.CharField(max_length=100)
    shortcut = models.CharField(max_length=100)

    def __str__(self):
        return self.label


class Batch(models.Model):
    created = models.DateTimeField(auto_now_add=timezone.now)
    name = models.CharField(max_length=100)

    for_bid = models.BooleanField(default=True)
    min_bid_add_on = models.PositiveIntegerField(default=20)
    slug = models.SlugField(max_length=50, blank=True)
    prefix = models.SlugField(max_length=5)

    class Meta:
        verbose_name = "batch"
        verbose_name_plural = "batches"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def calculate_potential_earnings(self) -> int:
        # TODO
        return 0


class RawItem(models.Model):
    batch = models.ForeignKey(Batch, related_name="raw_items", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=raw_item_image_path)


class Item(models.Model):
    raw_item = models.ForeignKey(RawItem, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)
    price = models.PositiveIntegerField()
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    brand = models.CharField(max_length=20, blank=True)
    brand_new = models.BooleanField(default=False)
    image = models.ImageField(upload_to=item_image_path)

    def __str__(self):
        return f'{self.batch}: {self.code}'

    @property
    def starting_bid_price(self):
        if self.batch.for_bid:
            return self.price + self.batch.min_bid_add_on

        return self.price
