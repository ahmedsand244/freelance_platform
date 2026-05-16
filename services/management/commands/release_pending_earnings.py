from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from services.models import WalletTransaction, Wallet

class Command(BaseCommand):
    help = 'Releases pending wallet earnings that have passed the PENDING_RELEASE_DAYS period'

    def handle(self, *args, **kwargs):
        release_days = getattr(settings, 'PENDING_RELEASE_DAYS', 14)
        threshold_date = timezone.now() - timedelta(days=release_days)
        
        # Find all pending earnings older than threshold_date
        pending_transactions = WalletTransaction.objects.filter(
            transaction_type='earning',
            status='pending',
            created_at__lte=threshold_date
        )

        count = 0
        for tx in pending_transactions:
            wallet = tx.wallet
            amount = tx.amount
            
            # Update balances safely
            wallet.pending_balance -= amount
            wallet.available_balance += amount
            wallet.save()
            
            # Mark transaction as available
            tx.status = 'available'
            tx.available_at = timezone.now()
            tx.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully released {count} pending transactions.'))
