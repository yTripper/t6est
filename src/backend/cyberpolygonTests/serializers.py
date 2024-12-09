from rest_framework import serializers
from cyberpolygonApp.models import Test

import datetime

class TestSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False)

    class Meta:
        model = Test
        fields = ['title', 'description', 'created_at']

    def validate(self, title):
        if Test.objects.filter(title=title):
            raise serializers.ValidationError(
                "Такой тест уже существует")
        return title

    def save(self, data):
        test = Test.objects.create(title=data['title'], description=data['description'],
                                   created_at=datetime.date.today())
        return test