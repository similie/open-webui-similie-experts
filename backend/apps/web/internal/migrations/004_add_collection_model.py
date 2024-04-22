from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    @migrator.create_model
    class Collection(pw.Model):
        id = pw.AutoField()
        name = pw.CharField()
        key = pw.CharField(max_length=255, unique=True)
        title = pw.CharField()
        content = pw.TextField(null=True)
        user_id =  pw.CharField(max_length=255)
        timestamp = pw.DateField()

        class Meta:
            table_name = "collection"




def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    migrator.remove_model("collection")

