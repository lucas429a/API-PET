from rest_framework import serializers
from groups.serializer import GroupSerializer
from traits.serializers import TraitSerializers
from .models import PetGender


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices=PetGender.choices,
        default=PetGender.Not_Informed
    )

    group = GroupSerializer()
    traits = TraitSerializers(many=True)
