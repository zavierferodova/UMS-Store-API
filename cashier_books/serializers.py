from rest_framework import serializers

from users.serializers import UserSerializer

from .models import CashierBook


class CashierBookSerializer(serializers.ModelSerializer):
    cashier_id = serializers.PrimaryKeyRelatedField(
        queryset=CashierBook._meta.get_field('cashier').related_model.objects.all(),
        source='cashier',
        write_only=True,
        required=True
    )
    cashier = UserSerializer(read_only=True)

    class Meta:
        model = CashierBook
        fields = [
            'id', 'code', 'cashier_id', 'cashier', 'cash_drawer', 'time_open', 'time_closed', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'code', 'time_open', 'created_at', 'updated_at', 'cashier')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['cash_drawer'].read_only = True

    def validate(self, attrs):
        cashier = attrs.get('cashier')
        if not self.instance:
            if cashier and CashierBook.objects.filter(cashier=cashier, time_closed__isnull=True).exists():
                raise serializers.ValidationError("User already has an open cashier book. Please close it first.")
        return attrs

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['cashier'] = UserSerializer(instance.cashier, context=self.context).data
        response.pop('cashier_id', None)
        return response
