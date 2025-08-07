from rest_framework import serializers

class HttpErrorBodySerializer(serializers.Serializer):
    message = serializers.CharField()
    stack = serializers.CharField(required=False)

class HttpResponseBodySerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.JSONField()
    error = HttpErrorBodySerializer(many=True, required=False)
    meta = serializers.JSONField(required=False)