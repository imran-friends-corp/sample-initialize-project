from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    created_by_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    updated_by_email = serializers.SerializerMethodField()


    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else ""

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else ""

    def get_updated_by_name(self, obj):
        return obj.created_by.name if obj.updated_by else ""

    def get_updated_by_email(self, obj):
        return obj.created_by.email if obj.updated_by else ""
