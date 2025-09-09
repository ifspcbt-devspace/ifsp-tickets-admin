import uuid

from django.db import models
from django.db import models


class EventStatus(models.IntegerChoices):
    SCHEDULED = 1, "Agendado"
    PUBLISHED = 2, "Publicado"
    OPENED = 3, "Aberto"
    IN_PROGRESS = 4, "Em andamento"
    CANCELED = 5, "Cancelado"
    FINISHED = 6, "Finalizado"


class EnrollmentStatus(models.TextChoices):
    WAITING_CONFIRMATION = "WAITING", "Aguardando confirmação"
    CONFIRMED = "CONFIRMED", "Confirmado"
    DENIED = "DENIED", "Negado"


class OrderStatus(models.IntegerChoices):
    RESERVED = 10, "Reservado"
    PENDING = 11, "Pendente"
    APPROVED = 20, "Aprovado"
    FAILED = 21, "Recusado"
    CANCELED = 22, "Cancelado"
    FORCED_CANCELED = 23, "Cancelado Forçadamente"


class PaymentStatus(models.TextChoices):
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    IN_PROCESS = "IN_PROCESS"
    IN_MEDIATION = "IN_MEDIATION"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    CHARGED_BACK = "CHARGED_BACK"


class TicketStatus(models.IntegerChoices):
    AVAILABLE = 1, "Disponível"
    CONSUMED = 2, "Consumido"
    EXPIRED = 3, "Expirado"
    CANCELED = 4, "Cancelado"


class Addresses(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=255)
    complement = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        managed = False
        db_table = "addresses"

    def __str__(self):
        parts = [
            f"{self.street}, {self.number}",
            f"{self.neighborhood}" if self.neighborhood else "",
            f"{self.city} - {self.state}",
            f"{self.zip_code}" if self.zip_code else "",
            f"{self.country}",
        ]
        # Junta partes não vazias
        return ", ".join(filter(None, parts))


class Companies(models.Model):
    address = models.OneToOneField(Addresses, models.DO_NOTHING, blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = models.UUIDField()
    cnpj = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Organizador"
        verbose_name_plural = "Organizadores"
        managed = False
        db_table = "companies"

    def __str__(self):
        return self.name


class Enrollments(models.Model):
    birth_date = models.DateField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    event_id = models.UUIDField()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(blank=True, null=True)
    document = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.WAITING_CONFIRMATION,
    )

    class Meta:
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
        managed = False
        db_table = "enrollments"


class EventConfigurations(models.Model):
    pk = models.CompositePrimaryKey("event_id", "key")
    event = models.ForeignKey("Events", models.DO_NOTHING)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Configuração de Evento"
        verbose_name_plural = "Configurações de Evento"
        managed = False
        db_table = "event_configurations"


class Events(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    init_date = models.DateField()
    end_date = models.DateField()
    status = models.IntegerField(
        choices=EventStatus.choices, default=EventStatus.OPENED
    )
    address = models.OneToOneField(Addresses, models.DO_NOTHING, blank=True, null=True)
    company_id = models.OneToOneField(
        Companies, models.DO_NOTHING, db_column="company_id", blank=True, null=True
    )
    event_thumbnail = models.OneToOneField(
        "EventsThumbnails", models.DO_NOTHING, blank=True, null=True
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        managed = False
        db_table = "events"

    def __str__(self):
        return self.name


class EventsThumbnails(models.Model):
    uploaded_at = models.DateTimeField()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Thumbnail de Evento"
        verbose_name_plural = "Thumbnails de Eventos"
        managed = False  # Não deixa o Django tentar criar/alterar a tabela
        db_table = "events_thumbnails"

    def __str__(self):
        return self.filename


class OrderItems(models.Model):
    quantity = models.IntegerField()
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey("Orders", models.DO_NOTHING, blank=True, null=True)
    ticket = models.ForeignKey("TicketSale", models.DO_NOTHING)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
        managed = False
        db_table = "order_items"


class Orders(models.Model):
    birth_date = models.DateField()
    status = models.SmallIntegerField()
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField()
    customer = models.ForeignKey("Users", models.DO_NOTHING)
    document = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    payment_url = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        managed = False
        db_table = "orders"


class Payments(models.Model):
    amount = models.DecimalField(max_digits=38, decimal_places=2)
    approval_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    order_id = models.BigIntegerField()
    updated_at = models.DateTimeField()
    currency = models.CharField(max_length=255)
    external_id = models.CharField(max_length=255)
    payment_type = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        managed = False
        db_table = "payments"


class TicketSale(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    entries = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=38, decimal_places=2)
    stock = models.IntegerField(default=10000)
    event_id = models.OneToOneField(
        Events, models.DO_NOTHING, db_column="event_id", blank=False, null=False
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "Ingresso Para Venda"
        verbose_name_plural = "Ingresso Para Venda"
        managed = False
        db_table = "ticket_sale"

    def __str__(self):
        return self.name


class Tickets(models.Model):
    expired_in = models.DateField()
    valid_in = models.DateField()
    created_at = models.DateTimeField()
    last_time_consumed = models.DateTimeField(blank=True, null=True)
    enrollment = models.OneToOneField(Enrollments, models.DO_NOTHING)
    event_id = models.UUIDField()
    id = models.UUIDField(primary_key=True)
    ticket_sale_id = models.UUIDField()
    code = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Ingresso"
        verbose_name_plural = "Ingressos"
        managed = False
        db_table = "tickets"

    def __str__(self):
        return self.description


class Users(models.Model):
    username = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    bio = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    password_date = models.DateField(blank=True, null=True, editable=False)
    role_id = models.IntegerField()
    company_id = models.UUIDField(blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.CharField(unique=True, max_length=255, editable=False)
    password = models.CharField(max_length=255, blank=True, null=True, editable=False)
    phone = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        managed = False
        db_table = "users"

    def __str__(self):
        return self.name
