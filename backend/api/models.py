from django.db import models

class EquipmentBatch(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    # Storing computed stats as JSON to avoid re-calculating on every fetch
    summary_stats = models.JSONField()

    def __str__(self):
        return self.filename