from rest_framework import serializers
from core.models import Wallet, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "wallet",
            "amount",
            "transaction_type",
            "created_at",
        ]
        read_only_fields = ["wallet", "created_at"]


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = [
            "id",
            "user",
            "balance",
            "transactions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]
