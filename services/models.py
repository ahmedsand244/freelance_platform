from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ─────────────────────────────────────────────
#  CATEGORY  /  SUBCATEGORY
# ─────────────────────────────────────────────

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=False, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font-awesome icon class e.g. fa-code")

    class Meta:
        verbose_name = _('Service Category')
        verbose_name_plural = _('Service Categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=False, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Sub Category')
        verbose_name_plural = _('Sub Categories')
        ordering = ['name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


# ─────────────────────────────────────────────
#  CATEGORY  (legacy simple model — kept for compatibility)
# ─────────────────────────────────────────────

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
#  SERVICE  PROVIDER
# ─────────────────────────────────────────────

class ServiceProvider(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='providers/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    # Profile 2.0 fields
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated skill tags")
    experience_years = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    profile_views = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @property
    def profile_strength(self):
        """Returns 0-100 profile completion score."""
        score = 0
        if self.bio: score += 25
        if self.profile_picture: score += 25
        if self.phone: score += 10
        if self.skills: score += 20
        if self.experience_years: score += 10
        if self.services.exists(): score += 10
        return score

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]


class PortfolioItem(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='portfolio/')
    link = models.URLField(blank=True, help_text="Link to live project (optional)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.provider.user.username}"


# ─────────────────────────────────────────────
#  SERVICE
# ─────────────────────────────────────────────

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    delivery_days = models.PositiveIntegerField(default=3)
    
    # --- Tier 2 (Premium/Gold) ---
    has_tier_2 = models.BooleanField(default=False)
    tier_2_name = models.CharField(max_length=50, default='Gold')
    tier_2_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tier_2_delivery_days = models.PositiveIntegerField(null=True, blank=True)
    tier_2_description = models.TextField(blank=True)

    # --- Tier 3 (Imperial/Diamond) ---
    has_tier_3 = models.BooleanField(default=False)
    tier_3_name = models.CharField(max_length=50, default='Imperial')
    tier_3_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tier_3_delivery_days = models.PositiveIntegerField(null=True, blank=True)
    tier_3_description = models.TextField(blank=True)

    is_active = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            try:
                from PIL import Image
                img = Image.open(self.image.path)
                img = img.convert('RGB')
                img.thumbnail((800, 800))
                img.save(self.image.path, format='WEBP', quality=85)
            except Exception:
                pass

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        from django.db.models import Avg
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0

    @property
    def review_count(self):
        return self.reviews.count()


# ─────────────────────────────────────────────
#  SERVICE  REVIEW  (verified purchase)
# ─────────────────────────────────────────────

class ServiceReview(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('service', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer.username} → {self.service.title} ({self.rating}★)"


# ─────────────────────────────────────────────
#  WISHLIST  /  FAVORITES
# ─────────────────────────────────────────────

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'service')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ♥ {self.service.title}"


# ─────────────────────────────────────────────
#  CART  /  ORDER
# ─────────────────────────────────────────────

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    tier = models.CharField(max_length=20, default='basic')
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)

    @property
    def price_at_tier(self):
        if self.tier == 'tier_2' and self.service.has_tier_2:
            return self.service.tier_2_price or self.service.price
        if self.tier == 'tier_3' and self.service.has_tier_3:
            return self.service.tier_3_price or self.service.price
        return self.service.price

    def __str__(self):
        return f"{self.user.username} — {self.service.title}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('revision', _('Revision Requested')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('disputed', _('Disputed')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    is_fully_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    @property
    def total_price(self):
        return sum(item.price_at_purchase * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} — {self.get_status_display()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    tier = models.CharField(max_length=20, default='basic')
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.service.title} × {self.quantity}"


# ─────────────────────────────────────────────
#  MILESTONES (ESCROW SYSTEM)
# ─────────────────────────────────────────────

class Milestone(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending Funding')),
        ('funded', _('Funded (In Escrow)')),
        ('active', _('Active (Work Started)')),
        ('in_review', _('In Review')),
        ('approved', _('Approved')),
        ('released', _('Released to Provider')),
        ('refunded', _('Refunded')),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Milestone: {self.title} for Order #{self.order.id} ({self.get_status_display()})"


# ─────────────────────────────────────────────
#  ORDER TASK (PROGRESS TRACKER)
# ─────────────────────────────────────────────

class OrderTask(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        status = 'Done' if self.is_completed else 'Pending'
        return f"[{status}] {self.title} — Order #{self.order.id}"



# ─────────────────────────────────────────────
#  ORDER DRAFT (PHASE 2: DRAFT SUBMISSIONS)
# ─────────────────────────────────────────────

class OrderDraft(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='drafts')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, help_text="Optional label for this draft")
    file = models.FileField(upload_to='order_drafts/%Y/%m/')
    note = models.TextField(blank=True, help_text="Optional note from freelancer to client")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Draft for Order #{self.order.id} — {self.file.name}"

    @property
    def filename(self):
        import os
        return os.path.basename(self.file.name)

    @property
    def file_extension(self):
        import os
        _, ext = os.path.splitext(self.file.name)
        return ext.lower().lstrip('.')

    @property
    def is_image(self):
        return self.file_extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']

    @property
    def file_size_display(self):
        try:
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size // 1024} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except Exception:
            return "Unknown"


# ─────────────────────────────────────────────
#  ORDER UPDATE (PHASE 4: ACTIVITY FEED)
# ─────────────────────────────────────────────

class OrderUpdate(models.Model):
    UPDATE_TYPES = [
        ('message', 'Message'),
        ('status', 'Status Change'),
        ('system', 'System'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='updates')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES, default='message')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update by {self.author.username} on Order #{self.order.id}"

    @property
    def is_freelancer_post(self):
        return self.order.items.filter(service__provider__user=self.author).exists()


# ─────────────────────────────────────────────
#  REVISION  REQUEST
# ─────────────────────────────────────────────

class RevisionRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='revisions')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Revision for Order #{self.order.id}"


# ─────────────────────────────────────────────
#  DISPUTE
# ─────────────────────────────────────────────

class Dispute(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('resolved_client', 'Resolved — Client Wins'),
        ('resolved_freelancer', 'Resolved — Freelancer Wins'),
        ('closed', 'Closed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='dispute')
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Dispute #{self.id} — Order #{self.order.id} ({self.status})"


# ─────────────────────────────────────────────
#  NOTIFICATION
# ─────────────────────────────────────────────

class Notification(models.Model):
    TYPE_CHOICES = [
        ('order', 'Order Update'),
        ('payment', 'Payment'),
        ('review', 'Review'),
        ('message', 'Message'),
        ('system', 'System'),
        ('dispute', 'Dispute'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.user.username}"


# ─────────────────────────────────────────────
#  ORGANIZER  MODULE  (kept from original)
# ─────────────────────────────────────────────

class Organizer(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='organizers/')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class OrganizerWork(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='works')
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='organizer_works/', null=True, blank=True)
    link = models.URLField(blank=True)

    def __str__(self):
        return self.title


class OrganizerReview(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.organizer.name}"


class OrganizerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='organizer_profiles/', null=True, blank=True)

    def __str__(self):
        return self.user.username


# ─────────────────────────────────────────────
#  EVENT  MODULE
# ─────────────────────────────────────────────

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to='events/')
    organizers = models.ManyToManyField(Organizer)

    def __str__(self):
        return self.title


class EventRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    client_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    event_name = models.CharField(max_length=200)
    date = models.DateField()
    number_of_organizers = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_name} — {self.client_name}"


# ─────────────────────────────────────────────
#  CONTACT  MESSAGE
# ─────────────────────────────────────────────

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(default="test@example.com")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} — {self.email}"


# ─────────────────────────────────────────────
#  BUYER REQUESTS / BIDDING SYSTEM
# ─────────────────────────────────────────────

class ProjectRequest(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open for Bidding'),
        ('awarded', 'Awarded'),
        ('closed', 'Closed/Expired'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_requests')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum budget in EGP")
    delivery_days = models.PositiveIntegerField(help_text="Expected delivery time in days")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.user.username}"


class ProjectBid(models.Model):
    project = models.ForeignKey(ProjectRequest, on_delete=models.CASCADE, related_name='bids')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='project_bids')
    message = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents multiple bids from the same provider on the same project
        unique_together = ('project', 'provider')
        ordering = ['price', 'delivery_days']

    def __str__(self):
        return f"Bid by {self.provider.user.username} for {self.project.title}"


# ─────────────────────────────────────────────
#  PAYMENT  /  WALLET
# ─────────────────────────────────────────────

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('in_escrow', 'In Escrow'),
        ('released', 'Released'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('wallet', 'Wallet'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    paymob_order_id = models.CharField(max_length=255, blank=True, null=True)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    seller_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} — {self.get_status_display()}"


class Transaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EGP')
    created_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Tx: {self.transaction_id} — {self.status}"


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    locked_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.username}'s Wallet — {self.available_balance + self.pending_balance} EGP"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earning', 'Earning'),
        ('withdrawal', 'Withdrawal'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('available', 'Available'),
        ('withdrawn', 'Withdrawn'),
        ('rejected', 'Rejected'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.CharField(max_length=255)
    reference_order_item = models.ForeignKey('OrderItem', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    available_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} ({self.status})"


class PayoutRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='payout_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payout_method_details = models.TextField(help_text="Bank account details, wallet number, etc.")
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payout #{self.id} for {self.amount} — {self.status}"


# ─────────────────────────────────────────────
#  MONETIZATION
# ─────────────────────────────────────────────

class FeaturedService(models.Model):
    """Paid promotion - show service in featured slots."""
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='featured')
    promoted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Featured: {self.service.title}"

    @property
    def is_live(self):
        now = timezone.now()
        return self.is_active and self.starts_at <= now <= self.ends_at


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    max_services = models.PositiveIntegerField(default=5)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — {self.price_monthly} EGP/mo"


class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} — {self.plan.name}"


# ─────────────────────────────────────────────
#  CHAT MESSAGE (WebSockets)
# ─────────────────────────────────────────────

class OrderMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    custom_offer = models.OneToOneField('CustomOffer', on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_message')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message by {self.sender.username} in Order #{self.order.id}"


# ─────────────────────────────────────────────
#  CUSTOM  OFFERS  (SPECIAL DEALS)
# ─────────────────────────────────────────────

class CustomOffer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_offers')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_offers')
    # If the offer is related to an existing order (extension)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_offers')
    
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days = models.PositiveIntegerField(default=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Offer from {self.sender.username} to {self.recipient.username} - {self.price} EGP"


# ─────────────────────────────────────────────
#  GROWTH & REFERRALS
# ─────────────────────────────────────────────

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="e.g., 10.00 for 10%")
    max_uses = models.PositiveIntegerField(default=100)
    current_uses = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.current_uses < self.max_uses and self.valid_from <= now <= self.valid_until

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}% off"


class Referral(models.Model):
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referrals")
    referred_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referred_by")
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    is_rewarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"


# ─────────────────────────────────────────────
#  SIGNUP SIGNAL (For Referrals)
# ─────────────────────────────────────────────
from allauth.account.signals import user_signed_up
from django.dispatch import receiver

@receiver(user_signed_up)
def user_signed_up_action(request, user, **kwargs):
    # Check for referral in session
    referrer_id = request.session.get('intended_referrer')
    if referrer_id:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            referrer = User.objects.get(id=referrer_id)
            Referral.objects.create(
                referrer=referrer,
                referred_user=user,
                reward_amount=50.00
            )
            request.session['referred_by'] = Referral.objects.get(referred_user=user).id
            if 'intended_referrer' in request.session:
                del request.session['intended_referrer']
        except Exception:
            pass

    # Send Premium Welcome HTML Email
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        site_url = request.build_absolute_uri('/')[:-1]
        context = {'user': user, 'site_url': site_url}
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject='Welcome to Freelance Yard!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception:
        pass
