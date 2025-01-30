from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.
from pgvector.django import VectorField


class Indexing(models.Model):
    file_name = models.CharField(max_length=100, null=True, blank=True)
    project_name = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField()
    doc_tag = models.CharField(max_length=100, null=True,
                               blank=True)  # for combining multiple documents with same type of projects
    last_commit_id = models.CharField(max_length=50, null=True, blank=True)
    embedding = VectorField(dimensions=1024, null=True, blank=True)  # Specify the vector dimension

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
