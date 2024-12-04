from rest_framework import serializers

from indexing.models import Indexing


class IndexingSerializer(serializers.ModelSerializer):
    # Ensure the embedding field is serialized as a list of floats
    embedding = serializers.ListField(
        child=serializers.FloatField(),
        required=True  # Optional if you want to allow creation without embedding
    )

    class Meta:
        model = Indexing
        fields = ['title', 'content']
