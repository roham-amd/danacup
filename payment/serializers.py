from rest_framework import serializers
from core.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "transaction_id"]

    def validate(self, attrs):
        # Ensure payment amount matches order total
        if attrs["amount"] != attrs["order"].total_amount:
            raise serializers.ValidationError(
                {"amount": "Payment amount must match order total"}
            )
        return attrs
