# Generated by Django 5.1.5 on 2025-01-28 03:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_producto_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='precio',
            field=models.DecimalField(decimal_places=3, max_digits=10),
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductoEnCarrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('carrito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='api.carrito')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.producto')),
            ],
        ),
    ]
