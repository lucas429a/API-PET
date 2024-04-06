from rest_framework.views import status, Response, Request, APIView
from .serializers import PetSerializer
from .models import Pet
from rest_framework.pagination import PageNumberPagination
from groups.models import Group
from traits.models import Trait


class PetView(APIView, PageNumberPagination):
    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_data = serializer.validated_data.pop("group")
        traits_data = serializer.validated_data.pop("traits")

        try:
            group = Group.objects.get(
                scientific_name=group_data["scientific_name"]
            )
        except Group.DoesNotExist:
            group = Group.objects.create(
                **group_data
            )
        pet = Pet.objects.create(
            **serializer.validated_data, group=group
        )

        for trait in traits_data:
            try:
                traits = Trait.objects.get(
                    name__iexact=trait["name"]
                )
            except Trait.DoesNotExist:
                traits = Trait.objects.create(
                    **trait
                )
            pet.traits.add(
                traits
            )

        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        by_trait = request.query_params.get("trait")
        if by_trait:
            pets = Pet.objects.filter(traits__name__iexact=by_trait)
        else:
            pets = Pet.objects.all()
        result = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id: int):
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response(
                {"detail": "Not found."}, status.HTTP_404_NOT_FOUND
            )
        serializer = PetSerializer(found_pet)
        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int):
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response(
                {"detail": "Not found."}, status.HTTP_404_NOT_FOUND
            )
        found_pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, pet_id: int):
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response(
                {"detail": "Not found."}, status.HTTP_404_NOT_FOUND
            )

        serializer = PetSerializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        if "group" in serializer.validated_data:
            group_data = serializer.validated_data.pop("group")
            try:
                group = Group.objects.get(
                    scientific_name=group_data["scientific_name"]
                )
            except Group.DoesNotExist:
                group = Group.objects.create(**group_data)
            found_pet.group = group

        if "traits" in serializer.validated_data:
            traits_data = serializer.validated_data.pop("traits")
            traits_list = []
            for trait in traits_data:
                try:
                    traits = Trait.objects.get(
                        name__iexact=trait["name"]
                    )
                except Trait.DoesNotExist:
                    traits = Trait.objects.create(
                        **trait
                    )
                traits_list.append(traits)
            found_pet.traits.set(
                traits_list
            )

        for key, value in serializer.validated_data.items():
            setattr(found_pet, key, value)
        found_pet.save()
        serializer = PetSerializer(found_pet)
        return Response(serializer.data, status.HTTP_200_OK)
